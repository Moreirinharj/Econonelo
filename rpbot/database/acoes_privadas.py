"""Funções para gerenciar ações privadas (agressões, etc)."""
from database.conexao import conectar
import time


def criar_acao_privada(tipo: str, autor_id: int, alvo_id: int, detalhes: str = None, resultado: str = None) -> int:
    """Cria uma nova ação privada."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO acoes_privadas (tipo, autor_id, alvo_id, detalhes, resultado, criado_em)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tipo, autor_id, alvo_id, detalhes, resultado, time.time()))
    acao_id = cur.lastrowid
    conn.commit()
    conn.close()
    return acao_id


def listar_acoes_privadas(autor_id: int = None, alvo_id: int = None) -> list:
    """Lista ações privadas."""
    conn = conectar()
    cur = conn.cursor()
    
    if autor_id:
        cur.execute("SELECT * FROM acoes_privadas WHERE autor_id = ? ORDER BY criado_em DESC", (autor_id,))
    elif alvo_id:
        cur.execute("SELECT * FROM acoes_privadas WHERE alvo_id = ? ORDER BY criado_em DESC", (alvo_id,))
    else:
        cur.execute("SELECT * FROM acoes_privadas ORDER BY criado_em DESC")
    
    acoes = [dict(row) for row in cur.fetchall()]
    conn.close()
    return acoes


def obter_acao_privada(acao_id: int) -> dict:
    """Obtém uma ação privada específica."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM acoes_privadas WHERE id = ?", (acao_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def marcar_visualizada(acao_id: int, usuario_id: int) -> bool:
    """Marca ação como visualizada."""
    conn = conectar()
    cur = conn.cursor()
    
    # Verificar se é autor ou alvo
    cur.execute("SELECT autor_id, alvo_id FROM acoes_privadas WHERE id = ?", (acao_id,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return False
    
    if row['autor_id'] == usuario_id:
        cur.execute("UPDATE acoes_privadas SET visualizado_autor = 1 WHERE id = ?", (acao_id,))
    elif row['alvo_id'] == usuario_id:
        cur.execute("UPDATE acoes_privadas SET visualizado_alvo = 1 WHERE id = ?", (acao_id,))
    else:
        conn.close()
        return False
    
    conn.commit()
    conn.close()
    return True
