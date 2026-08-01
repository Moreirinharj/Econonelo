import time
from utils.logger import log_acao
from database.conexao import conectar


def criar_npc(nome: str, idade: int, profissao: str, cidade: str, dinheiro: int = 1000, personalidade: str = "neutro") -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO npcs (nome, idade, profissao, cidade, dinheiro, personalidade, humor, ativo, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, 50, 1, ?)
    """, (nome, idade, profissao, cidade, dinheiro, personalidade, time.time()))
    conn.commit()
    npc_id = cur.lastrowid
    conn.close()
    log_acao("NPC_CRIADO", f"id={npc_id} nome={nome} profissao={profissao}")
    return npc_id


def obter_npc(npc_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM npcs WHERE id = ?", (npc_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def listar_npcs(cidade: str = None, profissao: str = None, limite: int = 50):
    conn = conectar()
    cur = conn.cursor()
    
    query = "SELECT * FROM npcs WHERE ativo = 1"
    params = []
    
    if cidade:
        query += " AND cidade = ?"
        params.append(cidade)
    if profissao:
        query += " AND profissao = ?"
        params.append(profissao)
    
    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(limite)
    
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def modificar_humor_npc(npc_id: int, delta: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT humor FROM npcs WHERE id = ?", (npc_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return -1
    
    novo_humor = max(0, min(100, row["humor"] + delta))
    cur.execute("UPDATE npcs SET humor = ? WHERE id = ?", (novo_humor, npc_id))
    conn.commit()
    conn.close()
    log_acao("NPC_HUMOR_MODIFICADO", f"npc_id={npc_id} delta={delta} novo={novo_humor}")
    return novo_humor


def modificar_dinheiro_npc(npc_id: int, delta: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT dinheiro FROM npcs WHERE id = ?", (npc_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return -1
    
    novo_dinheiro = max(0, row["dinheiro"] + delta)
    cur.execute("UPDATE npcs SET dinheiro = ? WHERE id = ?", (novo_dinheiro, npc_id))
    conn.commit()
    conn.close()
    return novo_dinheiro


def desativar_npc(npc_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE npcs SET ativo = 0 WHERE id = ?", (npc_id,))
    conn.commit()
    conn.close()
    log_acao("NPC_DESATIVADO", f"npc_id={npc_id}")


def contar_npcs() -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM npcs WHERE ativo = 1")
    total = cur.fetchone()["c"]
    conn.close()
    return total
