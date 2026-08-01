"""Funções para gerenciar subornos e corrupção."""
from database.conexao import conectar
import time


def criar_suborno(subornador_id: int, subornado_id: int, tipo: str, valor: float, descricao: str = None) -> int:
    """Cria um novo suborno."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO corrupcao (subornador_id, subornado_id, tipo, valor, status, descricao, criado_em)
        VALUES (?, ?, ?, ?, 'pendente', ?, ?)
    """, (subornador_id, subornado_id, tipo, valor, descricao, time.time()))
    corrupcao_id = cur.lastrowid
    conn.commit()
    conn.close()
    return corrupcao_id


def listar_subornos(status: str = None) -> list:
    """Lista subornos."""
    conn = conectar()
    cur = conn.cursor()
    
    if status:
        cur.execute("SELECT * FROM corrupcao WHERE status = ? ORDER BY criado_em DESC", (status,))
    else:
        cur.execute("SELECT * FROM corrupcao ORDER BY criado_em DESC")
    
    subornos = [dict(row) for row in cur.fetchall()]
    conn.close()
    return subornos


def obter_suborno(corrupcao_id: int) -> dict:
    """Obtém um suborno específico."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM corrupcao WHERE id = ?", (corrupcao_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def aceitar_suborno(corrupcao_id: int) -> bool:
    """Aceita um suborno."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE corrupcao SET status = 'aceito', respondido_em = ? WHERE id = ?",
                (time.time(), corrupcao_id))
    conn.commit()
    conn.close()
    return True


def recusar_suborno(corrupcao_id: int) -> bool:
    """Recusa um suborno."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE corrupcao SET status = 'recusado', respondido_em = ? WHERE id = ?",
                (time.time(), corrupcao_id))
    conn.commit()
    conn.close()
    return True


def registrar_tentativa_suborno(subornador_id: int, subornado_id: int, tipo: str, valor: float, descricao: str = None) -> int:
    """Registra uma tentativa de suborno."""
    return criar_suborno(subornador_id, subornado_id, tipo, valor, descricao)


def denunciar_suborno(corrupcao_id: int) -> bool:
    """Denuncia um suborno."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE corrupcao SET status = 'denunciado', respondido_em = ? WHERE id = ?",
                (time.time(), corrupcao_id))
    conn.commit()
    conn.close()
    return True


def listar_subornos_envolvidos(personagem_id: int) -> list:
    """Lista subornos onde o personagem está envolvido (como subornador ou subornado)."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM corrupcao 
        WHERE subornador_id = ? OR subornado_id = ?
        ORDER BY criado_em DESC
    """, (personagem_id, personagem_id))
    subornos = [dict(row) for row in cur.fetchall()]
    conn.close()
    return subornos


def obter_tentativa_suborno(corrupcao_id: int) -> dict:
    """Obtém uma tentativa de suborno específica."""
    return obter_suborno(corrupcao_id)


def atualizar_reputacao_corrupta(personagem_id: int, delta: float) -> bool:
    """Atualiza a reputação corrupta de um personagem."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE personagens 
        SET reputacao_corrupta = MAX(0, reputacao_corrupta + ?)
        WHERE id = ?
    """, (delta, personagem_id))
    conn.commit()
    conn.close()
    return True


def obter_reputacao_corrupta(personagem_id: int) -> float:
    """Obtém a reputação corrupta de um personagem."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT reputacao_corrupta FROM personagens WHERE id = ?", (personagem_id,))
    row = cur.fetchone()
    conn.close()
    return row['reputacao_corrupta'] if row else 0.0
