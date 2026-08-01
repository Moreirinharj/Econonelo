import time
from utils.logger import log_acao
from database.conexao import conectar


def criar_pedido_relacao(personagem_id: int, alvo_id: int, tipo: str) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO relacionamentos (personagem_id, alvo_id, tipo, status, criado_em)
        VALUES (?, ?, ?, 'pendente', ?)
    """, (personagem_id, alvo_id, tipo, time.time()))
    conn.commit()
    pedido_id = cur.lastrowid
    conn.close()
    log_acao("PEDIDO_RELACAO_CRIADO", f"id={pedido_id} de={personagem_id} para={alvo_id} tipo={tipo}")
    return pedido_id


def responder_pedido_relacao(pedido_id: int, aceitar: bool):
    conn = conectar()
    cur = conn.cursor()
    if aceitar:
        cur.execute("UPDATE relacionamentos SET status = 'aceito' WHERE id = ?", (pedido_id,))
        log_acao("PEDIDO_RELACAO_ACEITO", f"pedido_id={pedido_id}")
    else:
        cur.execute("DELETE FROM relacionamentos WHERE id = ?", (pedido_id,))
        log_acao("PEDIDO_RELACAO_RECUSADO", f"pedido_id={pedido_id}")
    conn.commit()
    conn.close()


def remover_relacao_direta(personagem_id: int, alvo_id: int, tipo: str) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM relacionamentos
        WHERE personagem_id = ? AND alvo_id = ? AND tipo = ? AND status = 'aceito'
    """, (personagem_id, alvo_id, tipo))
    afetou = cur.rowcount > 0
    conn.commit()
    conn.close()
    if afetou:
        log_acao("RELACAO_REMOVIDA", f"de={personagem_id} para={alvo_id} tipo={tipo}")
    return afetou


def listar_familia(personagem_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM relacionamentos
        WHERE (personagem_id = ? OR alvo_id = ?) AND status = 'aceito'
    """, (personagem_id, personagem_id))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def ja_existe_relacao(personagem_id: int, alvo_id: int, tipo: str) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as c FROM relacionamentos
        WHERE personagem_id = ? AND alvo_id = ? AND tipo = ? AND status IN ('pendente', 'aceito')
    """, (personagem_id, alvo_id, tipo))
    total = cur.fetchone()["c"]
    conn.close()
    return total > 0


def contar_pais(personagem_id: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as c FROM relacionamentos
        WHERE personagem_id = ? AND tipo IN ('pai', 'mae') AND status = 'aceito'
    """, (personagem_id,))
    total = cur.fetchone()["c"]
    conn.close()
    return total
