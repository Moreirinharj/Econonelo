"""Funções para gerenciar processos judiciais."""
from database.conexao import conectar
import time


def criar_processo(tipo: str, autor_id: int, reu_id: int, descricao: str, valor_causa: float = 0) -> int:
    """Cria um novo processo judicial."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO processos (tipo, autor_id, reu_id, descricao, status, valor_causa, criado_em)
        VALUES (?, ?, ?, ?, 'aberto', ?, ?)
    """, (tipo, autor_id, reu_id, descricao, valor_causa, time.time()))
    processo_id = cur.lastrowid
    conn.commit()
    conn.close()
    return processo_id


def listar_processos(status: str = None) -> list:
    """Lista processos."""
    conn = conectar()
    cur = conn.cursor()
    
    if status:
        cur.execute("SELECT * FROM processos WHERE status = ? ORDER BY criado_em DESC", (status,))
    else:
        cur.execute("SELECT * FROM processos ORDER BY criado_em DESC")
    
    processos = [dict(row) for row in cur.fetchall()]
    conn.close()
    return processos


def obter_processo(processo_id: int) -> dict:
    """Obtém um processo específico."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM processos WHERE id = ?", (processo_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def atribuir_advogado(processo_id: int, advogado_id: int, lado: str) -> bool:
    """Atribui advogado a um processo."""
    conn = conectar()
    cur = conn.cursor()
    
    if lado == "autor":
        cur.execute("UPDATE processos SET advogado_autor_id = ? WHERE id = ?", (advogado_id, processo_id))
    else:
        cur.execute("UPDATE processos SET advogado_reu_id = ? WHERE id = ?", (advogado_id, processo_id))
    
    conn.commit()
    conn.close()
    return True


def julgar_processo(processo_id: int, juiz_id: int, sentenca: str) -> bool:
    """Julga um processo."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE processos SET juiz_id = ?, sentenca = ?, status = 'julgado', julgado_em = ? WHERE id = ?",
                (juiz_id, sentenca, time.time(), processo_id))
    conn.commit()
    conn.close()
    return True
