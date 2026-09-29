"""Testes do oráculo: conferem a regra contra os cenários escritos à mão.

Os resultados esperados dos cenários foram calculados manualmente. Se o
oráculo e algum cenário divergirem, um dos dois está errado.

Uso: python3 testes/test_oraculo.py
"""

import json
import pathlib
import unittest

import oraculo

CENARIOS = sorted((pathlib.Path(__file__).parent / "cenarios").glob("*.json"))


def aplicar(estado, passos):
    for passo in passos:
        tipo = passo["tipo"]
        if tipo == "submissao":
            estado.adicionar_submissao(passo)
        elif tipo == "rejulgar":
            estado.rejulgar(passo["id"], passo["veredito"])
        elif tipo == "paralelo":
            aplicar(estado, passo["passos"])
        else:
            raise ValueError("passo não simulável: " + tipo)


class TestCenarios(unittest.TestCase):
    def test_todos_os_cenarios_batem_com_o_oraculo(self):
        self.assertTrue(CENARIOS, "nenhum cenário encontrado")
        for arquivo in CENARIOS:
            cenario = json.loads(arquivo.read_text(encoding="utf-8"))
            if any(p["tipo"] == "requisicao" for p in cenario["passos"]):
                continue  # cenários de validação só fazem sentido via HTTP
            with self.subTest(cenario=arquivo.stem):
                estado = oraculo.Estado()
                for equipe in cenario["equipes"]:
                    estado.adicionar_equipe(equipe)
                aplicar(estado, cenario["passos"])
                self.assertEqual(oraculo.diferencas(estado.placar(), cenario["placar"]), [])
                for equipe_id, esperado in cenario.get("detalhes", {}).items():
                    self.assertEqual(oraculo.diferencas(estado.detalhe_equipe(equipe_id), esperado), [])


class TestValidacao(unittest.TestCase):
    submissao = {"id": "s1", "equipe_id": "eq-a", "problema": "A", "minuto": 10, "veredito": "ACEITO"}

    def test_submissao_valida(self):
        self.assertIsNone(oraculo.validar_submissao(self.submissao))

    def test_submissao_invalida(self):
        casos = [
            {"problema": "a"}, {"problema": "ABC"}, {"minuto": -1}, {"minuto": 301},
            {"minuto": 1.5}, {"minuto": "1"}, {"minuto": True}, {"veredito": "TALVEZ"},
            {"id": ""}, {"equipe_id": None},
        ]
        for alteracao in casos:
            with self.subTest(alteracao=alteracao):
                self.assertIsNotNone(oraculo.validar_submissao({**self.submissao, **alteracao}))

    def test_limites_do_minuto(self):
        self.assertIsNone(oraculo.validar_submissao({**self.submissao, "minuto": 0}))
        self.assertIsNone(oraculo.validar_submissao({**self.submissao, "minuto": 300}))

    def test_equipe(self):
        self.assertIsNone(oraculo.validar_equipe({"id": "eq-a", "nome": "Equipe A"}))
        self.assertIsNotNone(oraculo.validar_equipe({"id": "eq-a"}))
        self.assertIsNotNone(oraculo.validar_equipe([]))


class TestEstado(unittest.TestCase):
    def test_duplicata_e_equipe_inexistente(self):
        estado = oraculo.Estado()
        estado.adicionar_equipe({"id": "eq-a", "nome": "A"})
        sub = {"id": "s1", "equipe_id": "eq-a", "problema": "A", "minuto": 1, "veredito": "ERRADO"}
        self.assertEqual(estado.adicionar_submissao(sub), "criada")
        self.assertEqual(estado.adicionar_submissao(sub), "duplicada")
        self.assertEqual(estado.adicionar_submissao({**sub, "id": "s2", "equipe_id": "x"}), "equipe_inexistente")

    def test_rejulgar_inexistente(self):
        self.assertFalse(oraculo.Estado().rejulgar("s1", "ACEITO"))


if __name__ == "__main__":
    unittest.main()
