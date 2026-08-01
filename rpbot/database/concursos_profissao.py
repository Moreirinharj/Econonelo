import time
import json
from utils.logger import log_acao
from database.conexao import conectar


def abrir_concurso_profissao(profissao: str, orgao: str, vagas: int, salario: int, encerra_em: float) -> str:
    """Abre concurso pra uma profissão específica."""
    concurso_id = f"prof_{profissao}_{int(time.time())}"
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO concursos (id, universidade, especialidade, vagas, salario, materias, nivel, inscricao_aberta, criado_em, encerra_em)
            VALUES (?, ?, ?, ?, ?, ?, 'medio', 1, ?, ?)
        """, (concurso_id, orgao, profissao, vagas, salario, json.dumps([profissao]), time.time(), encerra_em))
        conn.commit()
        conn.close()
        log_acao("CONCURSO_PROFISSAO_ABERTO", f"id={concurso_id} profissao={profissao}")
        return concurso_id
    except Exception as e:
        conn.close()
        log_acao("ERRO_CONCURSO_PROFISSAO", f"erro={e}")
        return None


def listar_concursos_profissao(profissao: str = None):
    """Lista concursos de profissões."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE concursos SET inscricao_aberta = 0 WHERE encerra_em < ?", (time.time(),))
    conn.commit()
    
    if profissao:
        cur.execute("""
            SELECT * FROM concursos 
            WHERE inscricao_aberta = 1 AND especialidade = ?
            AND id LIKE 'prof_%'
            ORDER BY encerra_em ASC
        """, (profissao,))
    else:
        cur.execute("""
            SELECT * FROM concursos 
            WHERE inscricao_aberta = 1 AND id LIKE 'prof_%'
            ORDER BY encerra_em ASC
        """)
    
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d["materias"] = json.loads(d["materias"])
        rows.append(d)
    conn.close()
    return rows


def registrar_aprovacao_profissao(personagem_id: int, profissao: str, nota: float, concurso_id: str):
    """Registra que o personagem passou no concurso da profissão."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE personagens SET concurso_profissao = ?, nota_concurso = ?
        WHERE id = ?
    """, (profissao, nota, personagem_id))
    conn.commit()
    conn.close()
    log_acao("APROVACAO_PROFISSAO", f"personagem={personagem_id} profissao={profissao} nota={nota}")


def ja_passou_concurso_profissao(personagem_id: int, profissao: str) -> bool:
    """Verifica se já passou no concurso dessa profissão."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT concurso_profissao FROM personagens WHERE id = ?", (personagem_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return row["concurso_profissao"] == profissao


# ===== AULAS =====

def registrar_aula(professor_id: int, curso_id: int, tema: str, duracao_min: int, pagamento: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO aulas (professor_id, curso_id, tema, duracao_min, pagamento, alunos_presentes, criado_em)
        VALUES (?, ?, ?, ?, ?, 0, ?)
    """, (professor_id, curso_id, tema, duracao_min, pagamento, time.time()))
    conn.commit()
    aula_id = cur.lastrowid
    conn.close()
    log_acao("AULA_REGISTRADA", f"id={aula_id} professor={professor_id} curso={curso_id}")
    return aula_id


def registrar_presenca(aula_id: int, aluno_id: int, aproveitamento: float):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO presencas_aula (aula_id, aluno_id, aproveitamento, criado_em)
        VALUES (?, ?, ?, ?)
    """, (aula_id, aluno_id, aproveitamento, time.time()))
    conn.commit()
    conn.close()


def incrementar_alunos_aula(aula_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE aulas SET alunos_presentes = alunos_presentes + 1 WHERE id = ?", (aula_id,))
    conn.commit()
    conn.close()


def obter_aula(aula_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM aulas WHERE id = ?", (aula_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def listar_aulas_professor(professor_id: int, limite: int = 10):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.*, c.nome as curso_nome, c.universidade
        FROM aulas a
        JOIN cursos c ON a.curso_id = c.id
        WHERE a.professor_id = ?
        ORDER BY a.criado_em DESC
        LIMIT ?
    """, (professor_id, limite))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def listar_aulas_curso(curso_id: int, limite: int = 10):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.*, p.nome as professor_nome
        FROM aulas a
        JOIN personagens p ON a.professor_id = p.id
        WHERE a.curso_id = ?
        ORDER BY a.criado_em DESC
        LIMIT ?
    """, (curso_id, limite))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def ja_assistiu_aula(aluno_id: int, aula_id: int) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM presencas_aula WHERE aluno_id = ? AND aula_id = ?", (aluno_id, aula_id))
    total = cur.fetchone()["c"]
    conn.close()
    return total > 0
