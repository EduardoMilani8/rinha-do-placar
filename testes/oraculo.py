"""Oráculo da Rinha do Placar: a implementação de referência da regra de ranking.

Este módulo é a fonte da verdade sobre como o placar deve ser calculado.
Ele é usado pelo gerador de dados e pelo executor de testes. Se a especificação (docs/REGRA-DE-RANKING.md) e este arquivo
divergirem, é um bug: abra uma Issue.
"""

import re

PENALIDADE_POR_ERRO = 20
MINUTO_MAX = 300
VEREDITOS = ("ACEITO", "ERRADO", "ERRO_COMPILACAO", "TEMPO_EXCEDIDO")
# Vereditos que contam como tentativa errada (geram penalidade).
CONTAM_COMO_ERRO = ("ERRADO", "TEMPO_EXCEDIDO")

_RE_PROBLEMA = re.compile(r"^[A-Z]{1,2}$")
_TAMANHO_MAX_TEXTO = 64


def _texto_valido(valor):
    return isinstance(valor, str) and 0 < len(valor) <= _TAMANHO_MAX_TEXTO


def validar_equipe(dados):
    """Devolve uma mensagem de erro ou None se o corpo for válido."""
    if not isinstance(dados, dict):
        return "corpo deve ser um objeto JSON"
    if not _texto_valido(dados.get("id")):
        return "id deve ser um texto de 1 a 64 caracteres"
    if not _texto_valido(dados.get("nome")):
        return "nome deve ser um texto de 1 a 64 caracteres"
    return None


def validar_veredito(veredito):
    if veredito not in VEREDITOS:
        return "veredito deve ser um de: " + ", ".join(VEREDITOS)
    return None


def validar_submissao(dados):
    """Devolve uma mensagem de erro ou None se o corpo for válido."""
    if not isinstance(dados, dict):
        return "corpo deve ser um objeto JSON"
    if not _texto_valido(dados.get("id")):
        return "id deve ser um texto de 1 a 64 caracteres"
    if not _texto_valido(dados.get("equipe_id")):
        return "equipe_id deve ser um texto de 1 a 64 caracteres"
    problema = dados.get("problema")
    if not isinstance(problema, str) or not _RE_PROBLEMA.match(problema):
        return "problema deve ter 1 ou 2 letras maiúsculas"
    minuto = dados.get("minuto")
    if isinstance(minuto, bool) or not isinstance(minuto, int):
        return "minuto deve ser um número inteiro"
    if not 0 <= minuto <= MINUTO_MAX:
        return "minuto deve estar entre 0 e %d" % MINUTO_MAX
    return validar_veredito(dados.get("veredito"))


class Estado:
    """Estado de uma competição: equipes e submissões."""

    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.equipes = {}
        self.submissoes = {}
        self._por_equipe = {}
        self._cache = {}

    def adicionar_equipe(self, dados):
        """Devolve 'criada' ou 'existe'."""
        if dados["id"] in self.equipes:
            return "existe"
        self.equipes[dados["id"]] = dados["nome"]
        self._por_equipe[dados["id"]] = []
        return "criada"

    def adicionar_submissao(self, dados):
        """Devolve 'criada', 'duplicada' ou 'equipe_inexistente'."""
        if dados["id"] in self.submissoes:
            return "duplicada"
        if dados["equipe_id"] not in self.equipes:
            return "equipe_inexistente"
        sub = {
            "id": dados["id"],
            "equipe_id": dados["equipe_id"],
            "problema": dados["problema"],
            "minuto": dados["minuto"],
            "veredito": dados["veredito"],
        }
        self.submissoes[sub["id"]] = sub
        self._por_equipe[sub["equipe_id"]].append(sub)
        self._cache.pop(sub["equipe_id"], None)
        return "criada"

    def rejulgar(self, submissao_id, veredito):
        """Devolve True se a submissão existia."""
        sub = self.submissoes.get(submissao_id)
        if sub is None:
            return False
        sub["veredito"] = veredito
        self._cache.pop(sub["equipe_id"], None)
        return True

    def detalhe_equipe(self, equipe_id):
        """Devolve o detalhe da equipe ou None se ela não existe."""
        if equipe_id not in self.equipes:
            return None
        return self._detalhe(equipe_id)

    def _detalhe(self, equipe_id):
        if equipe_id not in self._cache:
            self._cache[equipe_id] = self._calcular_equipe(equipe_id)
        return self._cache[equipe_id]

    def placar(self):
        """Ranking completo, com ordem total e determinística."""
        linhas = [self._detalhe(e) for e in self.equipes]
        linhas.sort(key=_chave_ordenacao)
        return [
            {
                "posicao": posicao,
                "equipe_id": l["equipe_id"],
                "nome": l["nome"],
                "resolvidos": l["resolvidos"],
                "penalidade": l["penalidade"],
                "ultimo_acerto": l["ultimo_acerto"],
            }
            for posicao, l in enumerate(linhas, start=1)
        ]

    def _calcular_equipe(self, equipe_id):
        por_problema = {}
        # Ordem cronológica: primeiro o minuto, depois o id da submissão.
        for sub in sorted(self._por_equipe[equipe_id], key=lambda s: (s["minuto"], s["id"])):
            p = por_problema.setdefault(sub["problema"], {
                "problema": sub["problema"],
                "resolvido": False,
                "tentativas_erradas": 0,
                "minuto_acerto": None,
                "penalidade": 0,
            })
            if p["resolvido"]:
                continue  # depois do acerto, nada mais conta
            if sub["veredito"] == "ACEITO":
                p["resolvido"] = True
                p["minuto_acerto"] = sub["minuto"]
                p["penalidade"] = sub["minuto"] + PENALIDADE_POR_ERRO * p["tentativas_erradas"]
            elif sub["veredito"] in CONTAM_COMO_ERRO:
                p["tentativas_erradas"] += 1
        problemas = [por_problema[k] for k in sorted(por_problema)]
        resolvidos = [p for p in problemas if p["resolvido"]]
        return {
            "equipe_id": equipe_id,
            "nome": self.equipes[equipe_id],
            "resolvidos": len(resolvidos),
            "penalidade": sum(p["penalidade"] for p in resolvidos),
            "ultimo_acerto": max((p["minuto_acerto"] for p in resolvidos), default=None),
            "problemas": problemas,
        }


def chave_ordenacao_placar(item):
    """Chave de ordenação de uma linha do placar (usada também pelos testes)."""
    ultimo = item["ultimo_acerto"] if item["ultimo_acerto"] is not None else 0
    return (-item["resolvidos"], item["penalidade"], ultimo, item["equipe_id"])


_chave_ordenacao = chave_ordenacao_placar


def diferencas(obtido, esperado, caminho="$"):
    """Compara `obtido` com `esperado` e devolve a lista de diferenças.

    Dicionários são comparados como subconjunto: só as chaves presentes em
    `esperado` são verificadas. Listas precisam ter o mesmo tamanho.
    """
    if isinstance(esperado, dict):
        if not isinstance(obtido, dict):
            return ["%s: esperado objeto, veio %r" % (caminho, obtido)]
        resultado = []
        for chave, valor in esperado.items():
            if chave not in obtido:
                resultado.append("%s.%s: campo ausente" % (caminho, chave))
            else:
                resultado += diferencas(obtido[chave], valor, "%s.%s" % (caminho, chave))
        return resultado
    if isinstance(esperado, list):
        if not isinstance(obtido, list):
            return ["%s: esperado lista, veio %r" % (caminho, obtido)]
        if len(obtido) != len(esperado):
            return ["%s: esperado %d itens, vieram %d" % (caminho, len(esperado), len(obtido))]
        resultado = []
        for i, (o, e) in enumerate(zip(obtido, esperado)):
            resultado += diferencas(o, e, "%s[%d]" % (caminho, i))
        return resultado
    if obtido != esperado or type(obtido) is not type(esperado):
        return ["%s: esperado %r, veio %r" % (caminho, esperado, obtido)]
    return []
