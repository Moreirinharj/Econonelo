"""Funções para gerenciar heranças."""
from database.conexao import conectar
import time
import json


def criar_heranca(falecido_id: int, dinheiro: float = 0, casas: list = None, veiculos: list = None, itens: list = None, testamento: str = None) -> int:
    """Cria uma nova herança."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO herancas (falecido_id, dinheiro, casas, veiculos, itens, status, testamento, criado_em)
        VALUES (?, ?, ?, ?, ?, 'pendente', ?, ?)
    """, (falecido_id, dinheiro, json.dumps(casas or []), json.dumps(veiculos or []), json.dumps(itens or []), testamento, time.time()))
    heranca_id = cur.lastrowid
    conn.commit()
    conn.close()
    return heranca_id


def listar_herancas(status: str = None) -> list:
    """Lista heranças."""
    conn = conectar()
    cur = conn.cursor()
    
    if status:
        cur.execute("SELECT * FROM herancas WHERE status = ? ORDER BY criado_em DESC", (status,))
    else:
        cur.execute("SELECT * FROM herancas ORDER BY criado_em DESC")
    
    herancas = [dict(row) for row in cur.fetchall()]
    
    # Converter JSON fields
    for h in herancas:
        for campo in ['casas', 'veiculos', 'itens']:
            if h.get(campo):
                try:
                    h[campo] = json.loads(h[campo])
                except:
                    h[campo] = []
    
    conn.close()
    return herancas


def obter_heranca(heranca_id: int) -> dict:
    """Obtém uma herança específica."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM herancas WHERE id = ?", (heranca_id,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        h = dict(row)
        for campo in ['casas', 'veiculos', 'itens']:
            if h.get(campo):
                try:
                    h[campo] = json.loads(h[campo])
                except:
                    h[campo] = []
        return h
    return None


def processar_heranca(heranca_id: int, herdeiros: dict) -> bool:
    """Processa distribuição de herança."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE herancas SET herdeiros = ?, status = 'processado', processado_em = ? WHERE id = ?",
                (json.dumps(herdeiros), time.time(), heranca_id))
    conn.commit()
    conn.close()
    return True
