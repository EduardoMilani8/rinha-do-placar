"""Servidor ingênuo: uma API mínima em memória, só com a biblioteca padrão.

Serve para duas coisas:
  1. Ver na prática como a especificação se comporta (status, formatos).
  2. Testar se o seu ambiente consegue rodar os testes (`executar.py`).

Ele NÃO concorre e NÃO serve de base para a solução: guarda tudo na memória de
um único processo, então não funciona com duas instâncias atrás de um balanceador.

Uso: python3 testes/servidor_ingenuo.py --porta 9999
"""

import argparse
import json
import threading
from typing import Any
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import oraculo

ESTADO = oraculo.Estado()
TRAVA = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    disable_nagle_algorithm = True

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def _responder(self, status, corpo=None):
        dados = b"" if corpo is None else json.dumps(corpo).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def _ler_json(self) -> Any:
        tamanho = int(self.headers.get("Content-Length") or 0)
        bruto = self.rfile.read(tamanho)
        try:
            return json.loads(bruto)
        except ValueError:
            return None

    def do_GET(self):
        if self.path == "/saude":
            return self._responder(200, {"status": "ok"})
        if self.path == "/placar":
            with TRAVA:
                return self._responder(200, ESTADO.placar())
        if self.path.startswith("/equipes/"):
            with TRAVA:
                detalhe = ESTADO.detalhe_equipe(self.path[len("/equipes/"):])
            if detalhe is None:
                return self._responder(404, {"erro": "equipe não encontrada"})
            return self._responder(200, detalhe)
        self._responder(404, {"erro": "rota não encontrada"})

    def do_POST(self):
        corpo = self._ler_json()
        if self.path == "/admin/reset":
            with TRAVA:
                ESTADO.reiniciar()
            return self._responder(204)
        if self.path == "/equipes":
            erro = oraculo.validar_equipe(corpo)
            if erro:
                return self._responder(422, {"erro": erro})
            with TRAVA:
                resultado = ESTADO.adicionar_equipe(corpo)
            if resultado == "existe":
                return self._responder(409, {"erro": "equipe já cadastrada"})
            return self._responder(201, {"id": corpo["id"]})
        if self.path == "/submissoes":
            erro = oraculo.validar_submissao(corpo)
            if erro:
                return self._responder(422, {"erro": erro})
            with TRAVA:
                resultado = ESTADO.adicionar_submissao(corpo)
            if resultado == "equipe_inexistente":
                return self._responder(404, {"erro": "equipe não encontrada"})
            return self._responder(200 if resultado == "duplicada" else 201, {"id": corpo["id"]})
        self._responder(404, {"erro": "rota não encontrada"})

    def do_PATCH(self):
        corpo = self._ler_json()
        if self.path.startswith("/submissoes/"):
            veredito = corpo.get("veredito") if isinstance(corpo, dict) else None
            erro = oraculo.validar_veredito(veredito)
            if erro:
                return self._responder(422, {"erro": erro})
            with TRAVA:
                existe = ESTADO.rejulgar(self.path[len("/submissoes/"):], veredito)
            if not existe:
                return self._responder(404, {"erro": "submissão não encontrada"})
            return self._responder(200, {"veredito": veredito})
        self._responder(404, {"erro": "rota não encontrada"})


class Servidor(ThreadingHTTPServer):
    request_queue_size = 256
    daemon_threads = True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--porta", type=int, default=9999)
    args = ap.parse_args()
    servidor = Servidor(("127.0.0.1", args.porta), Handler)
    print("Servidor ingênuo em http://127.0.0.1:%d (Ctrl+C para parar)" % args.porta)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
