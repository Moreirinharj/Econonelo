"""Funções para gerenciar vagas de emprego."""
from database.conexao import conectar


def criar_vaga(empresa_id: str, profissao: str, salario: float, requisitos: str = None, nivel: str = "medio", descricao: str = None) -> int:
    """Cria uma nova vaga de emprego."""
    import time
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO vagas (empresa_id, profissao, salario, requisitos, nivel, descricao, ativa, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    """, (empresa_id, profissao, salario, requisitos, nivel, descricao, time.time()))
    vaga_id = cur.lastrowid
    conn.commit()
    conn.close()
    return vaga_id


def listar_vagas(empresa_id: str = None, ativa: bool = True) -> list:
    """Lista vagas de emprego."""
    conn = conectar()
    cur = conn.cursor()
    
    if empresa_id:
        cur.execute("""
            SELECT v.*, e.nome as empresa_nome 
            FROM vagas v 
            LEFT JOIN empresas e ON v.empresa_id = e.id 
            WHERE v.empresa_id = ? AND v.ativa = ?
            ORDER BY v.criado_em DESC
        """, (empresa_id, 1 if ativa else 0))
    else:
        cur.execute("""
            SELECT v.*, e.nome as empresa_nome 
            FROM vagas v 
            LEFT JOIN empresas e ON v.empresa_id = e.id 
            WHERE v.ativa = ?
            ORDER BY v.criado_em DESC
        """, (1 if ativa else 0,))
    
    vagas = [dict(row) for row in cur.fetchall()]
    conn.close()
    return vagas


def obter_vaga(vaga_id: int) -> dict:
    """Obtém uma vaga específica."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.*, e.nome as empresa_nome 
        FROM vagas v 
        LEFT JOIN empresas e ON v.empresa_id = e.id 
        WHERE v.id = ?
    """, (vaga_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def contratar_personagem(personagem_id: int, vaga_id: int) -> bool:
    """Contrata um personagem para uma vaga."""
    import database as db
    vaga = obter_vaga(vaga_id)
    if not vaga:
        return False
    
    # Atualizar profissão do personagem
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET profissao = ?, salario = ? WHERE id = ?",
                (vaga['profissao'], vaga['salario'], personagem_id))
    conn.commit()
    conn.close()
    return True


def pedir_demissao(personagem_id: int) -> bool:
    """Personagem pede demissão."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET profissao = 'desempregado', salario = 0 WHERE id = ?",
                (personagem_id,))
    conn.commit()
    conn.close()
    return True
