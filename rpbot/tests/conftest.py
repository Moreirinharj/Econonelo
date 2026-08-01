"""Configuração para os testes: usa um banco temporário."""
import os
import sqlite3
import tempfile
import sys

# Garante que o diretório raiz do projeto está no path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Cria banco temporário
TEST_DB = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name

# Aplica patch antes de qualquer import do database
import database.conexao as conn_mod
conn_mod.DB_PATH = TEST_DB


def limpar_banco():
    """Apaga e recria o banco de teste."""
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except PermissionError:
            pass
    conn = sqlite3.connect(TEST_DB)
    conn.close()
    from database.conexao import iniciar_banco
    iniciar_banco()


def obter_db_path():
    return TEST_DB
