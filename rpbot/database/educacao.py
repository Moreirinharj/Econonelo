import time
from utils.logger import log_acao
from database.conexao import conectar

def criar_curso(nome: str, universidade: str, tipo: str, nivel: str, duracao_semestres: int, mensalidade: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO cursos (nome, universidade, tipo, nivel, duracao_semestres, mensalidade, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, universidade, tipo, nivel, duracao_semestres, mensalidade, time.time()))
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    log_acao("CURSO_CRIADO", f"id={cid} nome={nome} univ={universidade}")
    return cid

def listar_cursos(universidade: str = None, nivel: str = None):
    conn = conectar()
    cur = conn.cursor()
    query = "SELECT * FROM cursos WHERE 1=1"
    params = []
    if universidade:
        query += " AND universidade = ?"
        params.append(universidade)
    if nivel:
        query += " AND nivel = ?"
        params.append(nivel)
    query += " ORDER BY universidade, nome"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def obter_curso(curso_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cursos WHERE id = ?", (curso_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def matricular(personagem_id: int, curso_id: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO matriculas (personagem_id, curso_id, semestre_atual, status, matriculado_em)
        VALUES (?, ?, 1, 'matriculado', ?)
    """, (personagem_id, curso_id, time.time()))
    conn.commit()
    mid = cur.lastrowid
    conn.close()
    log_acao("MATRICULA_CRIADA", f"id={mid} personagem={personagem_id} curso={curso_id}")
    return mid

def obter_matricula_ativa(personagem_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.*, c.nome as curso_nome, c.universidade, c.duracao_semestres, c.mensalidade, c.nivel
        FROM matriculas m JOIN cursos c ON m.curso_id = c.id
        WHERE m.personagem_id = ? AND m.status = 'matriculado'
        ORDER BY m.matriculado_em DESC LIMIT 1
    """, (personagem_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def listar_matriculas_personagem(personagem_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.*, c.nome as curso_nome, c.universidade, c.nivel
        FROM matriculas m JOIN cursos c ON m.curso_id = c.id
        WHERE m.personagem_id = ?
        ORDER BY m.matriculado_em DESC
    """, (personagem_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def avancar_semestre(matricula_id: int) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT semestre_atual, status FROM matriculas WHERE id = ?", (matricula_id,))
    m = cur.fetchone()
    if not m or m["status"] != "matriculado":
        conn.close()
        return False
    cur.execute("UPDATE matriculas SET semestre_atual = semestre_atual + 1 WHERE id = ?", (matricula_id,))
    conn.commit()
    conn.close()
    return True

def concluir_curso(matricula_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE matriculas SET status = 'formado', formado_em = ?
        WHERE id = ?
    """, (time.time(), matricula_id))
    conn.commit()
    conn.close()
    log_acao("CURSO_CONCLUIDO", f"matricula_id={matricula_id}")

def atualizar_nota_media(matricula_id: int, nova_nota: float):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE matriculas SET nota_media = ? WHERE id = ?", (nova_nota, matricula_id))
    conn.commit()
    conn.close()

def contar_matriculas_ativas(personagem_id: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM matriculas WHERE personagem_id = ? AND status = 'matriculado'", (personagem_id,))
    total = cur.fetchone()["c"]
    conn.close()
    return total
