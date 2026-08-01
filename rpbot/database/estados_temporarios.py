"""Tabela genérica pra salvar estados temporários (subornos, minigames, etc)."""
import time
import json
from database.conexao import conectar


def salvar_estado(categoria: str, chave: str, dados: dict, expira_em: float = None):
    """Salva estado temporário no banco."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS estados_temporarios (
            categoria TEXT NOT NULL,
            chave TEXT NOT NULL,
            dados TEXT NOT NULL,
            criado_em REAL NOT NULL,
            expira_em REAL,
            PRIMARY KEY (categoria, chave)
        )
    """)
    conn.commit()
    
    cur.execute("""
        INSERT OR REPLACE INTO estados_temporarios (categoria, chave, dados, criado_em, expira_em)
        VALUES (?, ?, ?, ?, ?)
    """, (categoria, chave, json.dumps(dados), time.time(), expira_em))
    conn.commit()
    conn.close()


def obter_estado(categoria: str, chave: str) -> dict:
    """Obtém estado temporário. Retorna None se não existir ou expirou."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS estados_temporarios (
            categoria TEXT NOT NULL,
            chave TEXT NOT NULL,
            dados TEXT NOT NULL,
            criado_em REAL NOT NULL,
            expira_em REAL,
            PRIMARY KEY (categoria, chave)
        )
    """)
    conn.commit()
    
    cur.execute("SELECT dados, expira_em FROM estados_temporarios WHERE categoria = ? AND chave = ?", (categoria, chave))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return None
    
    if row["expira_em"] and row["expira_em"] < time.time():
        remover_estado(categoria, chave)
        return None
    
    return json.loads(row["dados"])


def remover_estado(categoria: str, chave: str):
    """Remove estado temporário."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM estados_temporarios WHERE categoria = ? AND chave = ?", (categoria, chave))
    conn.commit()
    conn.close()


def limpar_estados_expirados():
    """Remove todos os estados expirados."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM estados_temporarios WHERE expira_em IS NOT NULL AND expira_em < ?", (time.time(),))
    conn.commit()
    conn.close()
