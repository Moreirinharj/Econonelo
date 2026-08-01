import time
from utils.logger import log_acao
from database.conexao import conectar


def criar_evento(tipo: str, titulo: str, descricao: str, efeitos: str = None, duracao_horas: float = None) -> int:
    """Cria um novo evento ativo."""
    expira_em = time.time() + (duracao_horas * 3600) if duracao_horas else None
    
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO eventos (tipo, titulo, descricao, efeitos, ativo, criado_em, expira_em)
        VALUES (?, ?, ?, ?, 1, ?, ?)
    """, (tipo, titulo, descricao, efeitos, time.time(), expira_em))
    conn.commit()
    evento_id = cur.lastrowid
    conn.close()
    log_acao("EVENTO_CRIADO", f"id={evento_id} tipo={tipo} titulo={titulo}")
    return evento_id


def listar_eventos_ativos():
    """Lista todos os eventos ativos."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM eventos WHERE ativo = 1 ORDER BY criado_em DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def obter_evento(evento_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM eventos WHERE id = ?", (evento_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def desativar_evento(evento_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE eventos SET ativo = 0 WHERE id = ?", (evento_id,))
    conn.commit()
    conn.close()
    log_acao("EVENTO_DESATIVADO", f"id={evento_id}")


def limpar_eventos_expirados():
    """Remove eventos que já expiraram."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE eventos SET ativo = 0
        WHERE expira_em IS NOT NULL AND expira_em < ?
    """, (time.time(),))
    conn.commit()
    conn.close()
