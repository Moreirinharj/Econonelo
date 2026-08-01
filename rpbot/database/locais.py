import time
from utils.logger import log_acao
from database.conexao import conectar


def criar_local(nome: str, tipo: str, cidade: str, bairro: str, descricao: str = None, abertura: str = "08:00", fechamento: str = "22:00") -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO locais (nome, tipo, cidade, bairro, descricao, horario_abertura, horario_fechamento, ativo, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (nome, tipo, cidade, bairro, descricao, abertura, fechamento, time.time()))
    conn.commit()
    local_id = cur.lastrowid
    conn.close()
    log_acao("LOCAL_CRIADO", f"id={local_id} nome={nome} tipo={tipo}")
    return local_id


def obter_local(local_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM locais WHERE id = ?", (local_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def listar_locais(cidade: str = None, tipo: str = None):
    conn = conectar()
    cur = conn.cursor()
    
    query = "SELECT * FROM locais WHERE ativo = 1"
    params = []
    
    if cidade:
        query += " AND cidade = ?"
        params.append(cidade)
    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    
    query += " ORDER BY cidade, bairro, nome"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def contar_locais(cidade: str = None) -> int:
    conn = conectar()
    cur = conn.cursor()
    if cidade:
        cur.execute("SELECT COUNT(*) as c FROM locais WHERE ativo = 1 AND cidade = ?", (cidade,))
    else:
        cur.execute("SELECT COUNT(*) as c FROM locais WHERE ativo = 1")
    total = cur.fetchone()["c"]
    conn.close()
    return total


def desativar_local(local_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE locais SET ativo = 0 WHERE id = ?", (local_id,))
    conn.commit()
    conn.close()
    log_acao("LOCAL_DESATIVADO", f"id={local_id}")


def local_aberto_agora(local: dict) -> bool:
    """Verifica se o local está aberto no horário atual."""
    try:
        agora = time.localtime()
        hora_agora = agora.tm_hour * 100 + agora.tm_min
        
        h_abr = int(local["horario_abertura"].replace(":", ""))
        h_fec = int(local["horario_fechamento"].replace(":", ""))
        
        return h_abr <= hora_agora <= h_fec
    except (ValueError, AttributeError):
        return True
