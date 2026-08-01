"""Funções para gerenciar chamados de emergência."""
from database.conexao import conectar
import time


def criar_chamado(tipo: str, solicitante_id: int, local: str, descricao: str, prioridade: int = 1) -> int:
    """Cria um novo chamado."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chamados (tipo, solicitante_id, local, descricao, status, prioridade, criado_em)
        VALUES (?, ?, ?, ?, 'aberto', ?, ?)
    """, (tipo, solicitante_id, local, descricao, prioridade, time.time()))
    chamado_id = cur.lastrowid
    conn.commit()
    conn.close()
    return chamado_id


def listar_chamados(status: str = None, tipo: str = None) -> list:
    """Lista chamados."""
    conn = conectar()
    cur = conn.cursor()
    
    query = "SELECT * FROM chamados WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    
    query += " ORDER BY criado_em DESC"
    cur.execute(query, params)
    chamados = [dict(row) for row in cur.fetchall()]
    conn.close()
    return chamados


def obter_chamado(chamado_id: int) -> dict:
    """Obtém um chamado específico."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM chamados WHERE id = ?", (chamado_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def atender_chamado(chamado_id: int, atendente_id: int) -> bool:
    """Marca chamado como atendido."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE chamados SET atendente_id = ?, status = 'atendido', atendido_em = ? WHERE id = ?",
                (atendente_id, time.time(), chamado_id))
    conn.commit()
    conn.close()
    return True


def finalizar_chamado(chamado_id: int) -> bool:
    """Finaliza um chamado."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE chamados SET status = 'finalizado', finalizado_em = ? WHERE id = ?",
                (time.time(), chamado_id))
    conn.commit()
    conn.close()
    return True


def abrir_chamado_emergencia(solicitante_id: int, local: str, descricao: str, prioridade: int = 1) -> int:
    """Abre um chamado de emergência."""
    return criar_chamado("emergencia", solicitante_id, local, descricao, prioridade)


def atender_chamado_emergencia(chamado_id: int, atendente_id: int) -> bool:
    """Atende um chamado de emergência."""
    return atender_chamado(chamado_id, atendente_id)


def obter_chamado_emergencia(chamado_id: int) -> dict:
    """Obtém um chamado de emergência."""
    return obter_chamado(chamado_id)


def abrir_chamado_oab(solicitante_id: int, local: str, descricao: str) -> int:
    """Abre um chamado da OAB."""
    return criar_chamado("oab", solicitante_id, local, descricao, 2)


def assumir_chamado_oab(chamado_id: int, atendente_id: int) -> bool:
    """Assume um chamado da OAB."""
    return atender_chamado(chamado_id, atendente_id)


def pegar_chamado_emergencia(chamado_id: int, atendente_id: int) -> bool:
    """Pega um chamado de emergência."""
    return atender_chamado(chamado_id, atendente_id)
