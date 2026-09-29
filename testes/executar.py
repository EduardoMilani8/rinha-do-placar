"""Executor oficial dos testes da Rinha do Placar.

Duas fases:
  corretude  roda os cenários de testes/cenarios/ (eliminatória)
  carga      rajada de submissões + leituras simultâneas do placar, seguida da
             conferência do placar final contra o oráculo

Só usa a biblioteca padrão do Python (3.10 ou mais novo).

Exemplos:
  python3 testes/executar.py corretude
  python3 testes/executar.py carga --seed 42 --submissoes 5000
"""

import argparse
import http.client
import json
import pathlib
import random
import socket
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import gerador
import oraculo

TIMEOUT = 2.0          # segundos; passou disso, conta como erro
TENTATIVAS = 3         # cada envio é tentado até 3 vezes (a API é idempotente)
LIMITE_ERROS = 0.01    # padrão: mais de 1% de tentativas com falha reprova a carga
PASTA_CENARIOS = pathlib.Path(__file__).parent / "cenarios"


class Cliente:
    """Cliente HTTP com uma conexão persistente por thread."""

    def __init__(self, base):
        url = urlparse(base)
        self.host = url.hostname or "localhost"
        self.porta = url.port or 80
        self._local = threading.local()

    def requisitar(self, metodo, caminho, corpo=None):
        """Devolve (status, json ou None). Levanta OSError/HTTPException em falha de rede."""
        dados = json.dumps(corpo).encode() if corpo is not None else None
        cabecalhos = {"Content-Type": "application/json"} if dados is not None else {}
        conexao = getattr(self._local, "conexao", None)
        if conexao is None:
            conexao = self._local.conexao = http.client.HTTPConnection(self.host, self.porta, timeout=TIMEOUT)
        try:
            if conexao.sock is None:
                conexao.connect()
                # Sem isso, o Nagle + ACK atrasado do TCP soma ~40 ms em cada requisição.
                conexao.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            conexao.request(metodo, caminho, dados, cabecalhos)
            resposta = conexao.getresponse()
            bruto = resposta.read()
        except (OSError, http.client.HTTPException):
            conexao.close()
            self._local.conexao = None
            raise
        try:
            return resposta.status, (json.loads(bruto) if bruto else None)
        except ValueError:
            return resposta.status, None


# --------------------------------------------------------------------------
# Fase 1: corretude
# --------------------------------------------------------------------------

def _executar_passo(cli, passo, falhas):
    tipo = passo["tipo"]
    if tipo == "paralelo":
        with ThreadPoolExecutor(max_workers=len(passo["passos"])) as pool:
            list(pool.map(lambda p: _executar_passo(cli, p, falhas), passo["passos"]))
        return
    if tipo == "submissao":
        corpo = {k: passo[k] for k in ("id", "equipe_id", "problema", "minuto", "veredito")}
        repeticoes = passo.get("repetir", 1)
        for i in range(repeticoes):
            aceitos = (200, 201) if repeticoes > 1 and i > 0 else (201,)
            _checar(cli, falhas, "POST", "/submissoes", corpo, aceitos)
    elif tipo == "rejulgar":
        _checar(cli, falhas, "PATCH", "/submissoes/" + passo["id"], {"veredito": passo["veredito"]}, (200,))
    elif tipo == "requisicao":
        _checar(cli, falhas, passo["metodo"], passo["caminho"], passo["corpo"], (passo["esperar_status"],))
    else:
        raise ValueError("tipo de passo desconhecido: " + tipo)


def _checar(cli, falhas, metodo, caminho, corpo, aceitos):
    try:
        status, _ = cli.requisitar(metodo, caminho, corpo)
    except (OSError, http.client.HTTPException) as erro:
        falhas.append("%s %s: erro de rede (%s)" % (metodo, caminho, erro))
        return
    if status not in aceitos:
        falhas.append("%s %s: esperado status %s, veio %d" % (metodo, caminho, "/".join(map(str, aceitos)), status))


def rodar_cenario(cli, cenario):
    falhas = []
    try:
        status, _ = cli.requisitar("POST", "/admin/reset")
        if status != 204:
            return ["POST /admin/reset: esperado 204, veio %d" % status]
        for equipe in cenario["equipes"]:
            _checar(cli, falhas, "POST", "/equipes", equipe, (201,))
        for passo in cenario["passos"]:
            _executar_passo(cli, passo, falhas)

        status, placar = cli.requisitar("GET", "/placar")
        if status != 200:
            falhas.append("GET /placar: esperado 200, veio %d" % status)
        else:
            falhas += ["placar " + d for d in oraculo.diferencas(placar, cenario["placar"])]
        for equipe_id, esperado in cenario.get("detalhes", {}).items():
            status, detalhe = cli.requisitar("GET", "/equipes/" + equipe_id)
            if status != 200:
                falhas.append("GET /equipes/%s: esperado 200, veio %d" % (equipe_id, status))
            else:
                falhas += ["equipe %s %s" % (equipe_id, d) for d in oraculo.diferencas(detalhe, esperado)]
    except (OSError, http.client.HTTPException) as erro:
        falhas.append("erro de rede: %s" % erro)
    return falhas


def fase_corretude(cli):
    arquivos = sorted(PASTA_CENARIOS.glob("*.json"))
    reprovados = 0
    for arquivo in arquivos:
        cenario = json.loads(arquivo.read_text(encoding="utf-8"))
        falhas = rodar_cenario(cli, cenario)
        if falhas:
            reprovados += 1
            print("✘ %s: %s" % (arquivo.stem, cenario["nome"]))
            for falha in falhas[:8]:
                print("    - " + falha)
            if len(falhas) > 8:
                print("    ... e mais %d" % (len(falhas) - 8))
        else:
            print("✔ %s: %s" % (arquivo.stem, cenario["nome"]))
    print("\n%d de %d cenários passaram." % (len(arquivos) - reprovados, len(arquivos)))
    return reprovados == 0


# --------------------------------------------------------------------------
# Fase 2: carga
# --------------------------------------------------------------------------

class Metricas:
    def __init__(self):
        self._trava = threading.Lock()
        self.latencias = {}
        self.tentativas = 0
        self.falhas = 0

    def registrar(self, rotulo, segundos, ok):
        with self._trava:
            self.latencias.setdefault(rotulo, []).append(segundos)
            self.tentativas += 1
            if not ok:
                self.falhas += 1


def _percentil(valores, p):
    ordenados = sorted(valores)
    return ordenados[min(len(ordenados) - 1, int(len(ordenados) * p))]


def _enviar_com_tentativas(cli, metricas, rotulo, metodo, caminho, corpo, aceitos):
    """Devolve True se alguma tentativa foi aceita."""
    for _ in range(TENTATIVAS):
        inicio = time.perf_counter()
        try:
            status, _ = cli.requisitar(metodo, caminho, corpo)
            ok = status in aceitos
        except (OSError, http.client.HTTPException):
            ok = False
        metricas.registrar(rotulo, time.perf_counter() - inicio, ok)
        if ok:
            return True
    return False


def _placar_consistente(placar, n_equipes):
    """Confere se o placar lido durante a carga é um ranking válido e completo."""
    if not isinstance(placar, list) or len(placar) != n_equipes:
        return False
    for i, linha in enumerate(placar):
        if linha.get("posicao") != i + 1:
            return False
        if i > 0 and oraculo.chave_ordenacao_placar(placar[i - 1]) > oraculo.chave_ordenacao_placar(linha):
            return False
    return True


def fase_carga(cli, args):
    dados = gerador.gerar(args.seed, args.equipes, args.submissoes)
    metricas = Metricas()

    status, _ = cli.requisitar("POST", "/admin/reset")
    if status != 204:
        print("POST /admin/reset devolveu %d (esperado 204)" % status)
        return False
    for equipe in dados["equipes"]:
        if not _enviar_com_tentativas(cli, metricas, "POST /equipes", "POST", "/equipes", equipe, (201, 409)):
            print("Não foi possível cadastrar as equipes.")
            return False
    metricas.latencias.clear()
    metricas.tentativas = metricas.falhas = 0

    perdidos = []
    leituras_invalidas = []
    parar_leitores = threading.Event()

    def leitor():
        while not parar_leitores.is_set():
            inicio = time.perf_counter()
            try:
                status, placar = cli.requisitar("GET", "/placar")
                ok = status == 200
            except (OSError, http.client.HTTPException):
                ok, placar = False, None
            metricas.registrar("GET /placar", time.perf_counter() - inicio, ok)
            if ok and not _placar_consistente(placar, len(dados["equipes"])):
                leituras_invalidas.append(time.time())
            time.sleep(0.02)

    def enviar(sub):
        if not _enviar_com_tentativas(cli, metricas, "POST /submissoes", "POST", "/submissoes", sub, (200, 201)):
            perdidos.append(sub["id"])

    def rejulgar(rej):
        if not _enviar_com_tentativas(cli, metricas, "PATCH /submissoes", "PATCH",
                                      "/submissoes/" + rej["id"], {"veredito": rej["veredito"]}, (200,)):
            perdidos.append("rejulgamento:" + rej["id"])

    leitores = [threading.Thread(target=leitor, daemon=True) for _ in range(args.leitores)]
    inicio = time.perf_counter()
    for t in leitores:
        t.start()
    with ThreadPoolExecutor(max_workers=args.concorrencia) as pool:
        list(pool.map(enviar, dados["envios"]))
        # Rejulgamentos só começam depois que todos os envios foram confirmados.
        list(pool.map(rejulgar, dados["rejulgamentos"]))
    duracao = time.perf_counter() - inicio
    parar_leitores.set()
    for t in leitores:
        t.join()

    status, placar_final = cli.requisitar("GET", "/placar")
    if status != 200:
        diferencas = ["GET /placar final devolveu %d" % status]
    else:
        diferencas = oraculo.diferencas(placar_final, dados["esperado"])

    todas = [x for v in metricas.latencias.values() for x in v]
    taxa_erro = metricas.falhas / metricas.tentativas if metricas.tentativas else 1.0
    print("Carga: %d requisições em %.1fs (%.0f req/s)" % (metricas.tentativas, duracao, metricas.tentativas / duracao))
    print("%-20s %8s %9s %9s %9s" % ("endpoint", "reqs", "p50 ms", "p95 ms", "p99 ms"))
    for rotulo, valores in sorted(metricas.latencias.items()):
        print("%-20s %8d %9.1f %9.1f %9.1f" % (rotulo, len(valores), statistics.median(valores) * 1000,
                                               _percentil(valores, 0.95) * 1000, _percentil(valores, 0.99) * 1000))
    p99_global = _percentil(todas, 0.99) * 1000 if todas else float("inf")
    print("%-20s %8d %9.1f %9.1f %9.1f" % ("GLOBAL", len(todas), statistics.median(todas) * 1000,
                                           _percentil(todas, 0.95) * 1000, p99_global))

    ok_erros = taxa_erro <= args.limite_erros
    ok_perdas = not perdidos
    ok_leituras = not leituras_invalidas
    ok_final = not diferencas
    print("\nTaxa de falhas: %.2f%% (limite %.0f%%) ... %s" % (taxa_erro * 100, args.limite_erros * 100, "ok" if ok_erros else "REPROVADO"))
    print("Envios perdidos: %d ... %s" % (len(perdidos), "ok" if ok_perdas else "REPROVADO"))
    print("Placares inválidos durante a carga: %d ... %s" % (len(leituras_invalidas), "ok" if ok_leituras else "REPROVADO"))
    print("Placar final igual ao esperado ... %s" % ("ok" if ok_final else "REPROVADO"))
    for d in diferencas[:8]:
        print("    - " + d)

    aprovado = ok_erros and ok_perdas and ok_leituras and ok_final
    resultado = {
        "aprovado": aprovado, "p99_global_ms": round(p99_global, 2),
        "requisicoes_por_segundo": round(metricas.tentativas / duracao, 1),
        "taxa_falhas": round(taxa_erro, 5), "seed": args.seed,
    }
    if args.saida:
        pathlib.Path(args.saida).write_text(json.dumps(resultado, indent=2) + "\n", encoding="utf-8")
    print("\nResultado da carga: %s" % ("APROVADO" if aprovado else "REPROVADO"))
    return aprovado


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fase", choices=["corretude", "carga"])
    ap.add_argument("--url", default="http://localhost:9999", help="endereço base da API (padrão: %(default)s)")
    ap.add_argument("--seed", type=int, default=42, help="semente dos dados (a oficial é secreta)")
    ap.add_argument("--equipes", type=int, default=300)
    ap.add_argument("--submissoes", type=int, default=30000)
    ap.add_argument("--concorrencia", type=int, default=64, help="envios simultâneos")
    ap.add_argument("--leitores", type=int, default=16, help="leitores simultâneos do placar")
    ap.add_argument("--limite-erros", type=float, default=LIMITE_ERROS,
                    help="fração máxima de tentativas com falha (padrão: %(default)s; a etapa de falha usa 0.05)")
    ap.add_argument("--saida", help="arquivo JSON para gravar o resumo da carga")
    args = ap.parse_args()

    cli = Cliente(args.url)
    try:
        status, _ = cli.requisitar("GET", "/saude")
    except (OSError, http.client.HTTPException) as erro:
        print("Não consegui falar com %s: %s" % (args.url, erro))
        sys.exit(2)
    if status != 200:
        print("GET /saude devolveu %d (esperado 200)" % status)
        sys.exit(2)

    random.seed(args.seed)
    ok = fase_corretude(cli) if args.fase == "corretude" else fase_carga(cli, args)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
