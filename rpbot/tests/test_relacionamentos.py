import unittest
from tests.conftest import limpar_banco
import database as db


def criar_personagem_teste(nome="A"):
    dados = {
        "nome": nome, "idade": 20, "cor_pele": "x",
        "tipo_cabelo": "y", "cor_cabelo": "z",
        "estado": "SP", "religiao": "nenhuma",
    }
    return db.criar_personagem("user_teste", dados)


class TestRelacionamentos(unittest.TestCase):
    def setUp(self):
        limpar_banco()

    def test_criar_pedido_relacao(self):
        p1 = criar_personagem_teste("Pai")
        p2 = criar_personagem_teste("Filho")
        pid = db.criar_pedido_relacao(p1, p2, "pai")
        self.assertGreater(pid, 0)

    def test_aceitar_pedido(self):
        p1 = criar_personagem_teste("A")
        p2 = criar_personagem_teste("B")
        pid = db.criar_pedido_relacao(p1, p2, "amigo")
        db.responder_pedido_relacao(pid, aceitar=True)
        familia = db.listar_familia(p1)
        self.assertEqual(len(familia), 1)

    def test_recusar_pedido(self):
        p1 = criar_personagem_teste("A")
        p2 = criar_personagem_teste("B")
        pid = db.criar_pedido_relacao(p1, p2, "amigo")
        db.responder_pedido_relacao(pid, aceitar=False)
        familia = db.listar_familia(p1)
        self.assertEqual(len(familia), 0)

    def test_ja_existe_relacao(self):
        p1 = criar_personagem_teste("A")
        p2 = criar_personagem_teste("B")
        self.assertFalse(db.ja_existe_relacao(p1, p2, "amigo"))
        db.criar_pedido_relacao(p1, p2, "amigo")
        self.assertTrue(db.ja_existe_relacao(p1, p2, "amigo"))


class TestChamados(unittest.TestCase):
    def setUp(self):
        limpar_banco()

    def test_abrir_chamado_emergencia(self):
        p = criar_personagem_teste()
        cid = db.abrir_chamado_emergencia(p, "192", "teste")
        self.assertGreater(cid, 0)

        c = db.obter_chamado_emergencia(cid)
        self.assertEqual(c["status"], "aberto")
        self.assertEqual(c["tipo"], "192")

    def test_atender_chamado(self):
        p = criar_personagem_teste()
        cid = db.abrir_chamado_emergencia(p, "192", "teste")
        atendente = criar_personagem_teste("Medico")
        sucesso = db.atender_chamado_emergencia(cid, atendente)
        self.assertTrue(sucesso)

        c = db.obter_chamado_emergencia(cid)
        self.assertEqual(c["status"], "atendido")


if __name__ == "__main__":
    unittest.main()
