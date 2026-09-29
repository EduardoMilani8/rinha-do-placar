"""Gerador determinístico de uma competição simulada.

A mesma semente sempre produz os mesmos dados. O resultado esperado é
calculado com o oráculo, aplicando os rejulgamentos ao final.

Uso: python3 testes/gerador.py --seed 42 --saida dados/
"""

import argparse
import json
import pathlib
import random

import oraculo

DURACAO = 300
N_PROBLEMAS = 12
FRACAO_DUPLICATAS = 0.03
FRACAO_REJULGAMENTOS = 0.02
JITTER_DESORDEM = 30  # minutos de "bagunça" na ordem de envio


def _sortear_veredito(rnd, habilidade):
    p_aceito = 0.05 + 0.30 * habilidade
    if rnd.random() < p_aceito:
        return "ACEITO"
    return rnd.choices(["ERRADO", "ERRO_COMPILACAO", "TEMPO_EXCEDIDO"], weights=[60, 12, 28])[0]


def gerar(seed, n_equipes=300, n_submissoes=30000):
    rnd = random.Random(seed)
    equipes = [{"id": "eq-%04d" % i, "nome": "Equipe %04d" % i} for i in range(1, n_equipes + 1)]
    habilidade = {e["id"]: rnd.random() ** 2 for e in equipes}
    problemas = [chr(ord("A") + i) for i in range(N_PROBLEMAS)]

    submissoes = []
    for i in range(1, n_submissoes + 1):
        equipe_id = rnd.choice(equipes)["id"]
        submissoes.append({
            "id": "sub-%06d" % i,
            "equipe_id": equipe_id,
            "problema": rnd.choice(problemas),
            "minuto": rnd.randrange(0, DURACAO),
            "veredito": _sortear_veredito(rnd, habilidade[equipe_id]),
        })

    # Ordem de envio: aproximadamente cronológica, mas bagunçada.
    envios = [(s["minuto"] + rnd.uniform(-JITTER_DESORDEM, JITTER_DESORDEM), s) for s in submissoes]
    # Duplicatas: a mesma submissão reenviada logo depois.
    for chave, sub in rnd.sample(envios, int(len(envios) * FRACAO_DUPLICATAS)):
        envios.append((chave + rnd.uniform(0, 20), dict(sub)))
    envios.sort(key=lambda par: par[0])
    envios = [sub for _, sub in envios]

    # Rejulgamentos: o veredito final de algumas submissões muda.
    rejulgamentos = []
    for sub in rnd.sample(submissoes, int(len(submissoes) * FRACAO_REJULGAMENTOS)):
        novo = rnd.choice([v for v in oraculo.VEREDITOS if v != sub["veredito"]])
        rejulgamentos.append({"id": sub["id"], "veredito": novo})

    estado = oraculo.Estado()
    for equipe in equipes:
        estado.adicionar_equipe(equipe)
    for sub in envios:
        estado.adicionar_submissao(sub)
    for rej in rejulgamentos:
        estado.rejulgar(rej["id"], rej["veredito"])

    return {
        "equipes": equipes,
        "envios": envios,
        "rejulgamentos": rejulgamentos,
        "esperado": estado.placar(),
    }


def _escrever_jsonl(caminho, itens):
    with open(caminho, "w", encoding="utf-8") as f:
        for item in itens:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--equipes", type=int, default=300)
    ap.add_argument("--submissoes", type=int, default=30000)
    ap.add_argument("--saida", default="dados")
    args = ap.parse_args()

    dados = gerar(args.seed, args.equipes, args.submissoes)
    pasta = pathlib.Path(args.saida)
    pasta.mkdir(parents=True, exist_ok=True)
    _escrever_jsonl(pasta / "equipes.jsonl", dados["equipes"])
    _escrever_jsonl(pasta / "envios.jsonl", dados["envios"])
    _escrever_jsonl(pasta / "rejulgamentos.jsonl", dados["rejulgamentos"])
    (pasta / "esperado.json").write_text(
        json.dumps(dados["esperado"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Gerado em %s: %d equipes, %d envios (com duplicatas), %d rejulgamentos" % (
        pasta, len(dados["equipes"]), len(dados["envios"]), len(dados["rejulgamentos"])))


if __name__ == "__main__":
    main()
