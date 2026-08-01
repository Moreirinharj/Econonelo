import unittest
from tests.conftest import limpar_banco
import database as db


class TestPersonagens(unittest.TestCase):
    def setUp(self):
        limpar_banco()

    def test_criar_personagem(self):
        dados = {
            "nome": "João", "idade": 25, "cor_pele": "branca",
            "tipo_cabelo": "curto", "cor_cabelo": "preto",
            "estado": "SP", "religiao": "nenhuma",
        }
        pid = db.criar_personagem("user1", dados)
        self.assertGreater(pid, 0)

        p = db.obter_personagem_por_id(pid)
        self.assertEqual(p["nome"], "João")
        self.assertEqual(p["ativo"], 1)

    def test_listar_personagens(self):
        dados = {
            "nome": "A", "idade": 20, "cor_pele": "x",
            "tipo_cabelo": "y", "cor_cabelo": "z",
            "estado": "SP", "religiao": "nenhuma",
        }
        db.criar_personagem("user1", dados)
        db.criar_personagem("user1", dados)
        lista = db.listar_personagens("user1")
        self.assertEqual(len(lista), 2)

    def test_personagem_ativo(self):
        dados = {
            "nome": "A", "idade": 20, "cor_pele": "x",
            "tipo_cabelo": "y", "cor_cabelo": "z",
            "estado": "SP", "religiao": "nenhuma",
        }
        id1 = db.criar_personagem("user1", dados)
        id2 = db.criar_personagem("user1", dados)

        ativo = db.obter_personagem_ativo("user1")
        self.assertEqual(ativo["id"], id2)

        db.definir_personagem_ativo("user1", id1)
        ativo = db.obter_personagem_ativo("user1")
        self.assertEqual(ativo["id"], id1)

    def test_atualizar_saldo(self):
        dados = {
            "nome": "A", "idade": 20, "cor_pele": "x",
            "tipo_cabelo": "y", "cor_cabelo": "z",
            "estado": "SP", "religiao": "nenhuma", "saldo": 1000,
        }
        pid = db.criar_personagem("user1", dados)
        novo = db.atualizar_saldo_personagem(pid, 500)
        self.assertEqual(novo, 1500)

        novo = db.atualizar_saldo_personagem(pid, -2000)
        self.assertEqual(novo, 0)

    def test_prender_soltar(self):
        dados = {
            "nome": "A", "idade": 20, "cor_pele": "x",
            "tipo_cabelo": "y", "cor_cabelo": "z",
            "estado": "SP", "religiao": "nenhuma",
        }
        pid = db.criar_personagem("user1", dados)
        db.prender_personagem(pid)
        p = db.obter_personagem_por_id(pid)
        self.assertEqual(p["preso"], 1)

        db.soltar_personagem(pid)
        p = db.obter_personagem_por_id(pid)
        self.assertEqual(p["preso"], 0)


if __name__ == "__main__":
    unittest.main()
