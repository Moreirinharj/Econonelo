import time
import json
from utils.logger import log_acao
from database.conexao import conectar


def abrir_concurso(concurso_id: str, universidade: str, especialidade: str, vagas: int, salario: int, materias: list, nivel: str = "superior", duracao_horas: float = 48) -> bool:
    """Abre um concurso público."""
    conn = conectar()
    cur = conn.cursor()
    encerra_em = time.time() + (duracao_horas * 3600)
    try:
        cur.execute("""
            INSERT INTO concursos (id, universidade, especialidade, vagas, salario, materias, nivel, inscricao_aberta, criado_em, encerra_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """, (concurso_id, universidade, especialidade, vagas, salario, json.dumps(materias), nivel, time.time(), encerra_em))
        conn.commit()
        conn.close()
        log_acao("CONCURSO_ABERTO", f"id={concurso_id} univ={universidade} esp={especialidade}")
        return True
    except Exception as e:
        conn.close()
        log_acao("ERRO_CONCURSO", f"erro={e}")
        return False


def listar_concursos_abertos(especialidade: str = None):
    """Lista concursos com inscrições abertas."""
    conn = conectar()
    cur = conn.cursor()
    
    # Primeiro, limpa concursos expirados
    cur.execute("UPDATE concursos SET inscricao_aberta = 0 WHERE encerra_em < ?", (time.time(),))
    conn.commit()
    
    if especialidade:
        cur.execute("SELECT * FROM concursos WHERE inscricao_aberta = 1 AND especialidade = ? ORDER BY encerra_em ASC", (especialidade,))
    else:
        cur.execute("SELECT * FROM concursos WHERE inscricao_aberta = 1 ORDER BY encerra_em ASC")
    
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d["materias"] = json.loads(d["materias"])
        rows.append(d)
    conn.close()
    return rows


def obter_concurso(concurso_id: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM concursos WHERE id = ?", (concurso_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    d = dict(row)
    d["materias"] = json.loads(d["materias"])
    conn.close()
    return d


def registrar_participacao(concurso_id: str, personagem_id: int, nota: float, aprovado: bool, posicao: int = None) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO participacoes_concurso (concurso_id, personagem_id, nota, aprovado, posicao, criado_em)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (concurso_id, personagem_id, nota, 1 if aprovado else 0, posicao, time.time()))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    log_acao("PARTICIPACAO_CONCURSO", f"concurso={concurso_id} personagem={personagem_id} nota={nota} aprovado={aprovado}")
    return pid


def ja_participou_concurso(personagem_id: int, concurso_id: str) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM participacoes_concurso WHERE personagem_id = ? AND concurso_id = ?", (personagem_id, concurso_id))
    total = cur.fetchone()["c"]
    conn.close()
    return total > 0


def listar_participacoes_personagem(personagem_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, c.universidade, c.especialidade, c.salario
        FROM participacoes_concurso p
        JOIN concursos c ON p.concurso_id = c.id
        WHERE p.personagem_id = ?
        ORDER BY p.criado_em DESC
    """, (personagem_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def definir_cargo_professor(personagem_id: int, cargo: str, salario: int, concurso_id: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE personagens SET cargo_atual = ?, salario_cargo = ?, concurso_aprovado = ?
        WHERE id = ?
    """, (cargo, salario, concurso_id, personagem_id))
    conn.commit()
    conn.close()
    log_acao("CARGO_DEFINIDO", f"personagem={personagem_id} cargo={cargo} salario={salario}")


def obter_ranking_concurso(concurso_id: str, limite: int = 10):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, pe.nome as personagem_nome
        FROM participacoes_concurso p
        JOIN personagens pe ON p.personagem_id = pe.id
        WHERE p.concurso_id = ?
        ORDER BY p.nota DESC
        LIMIT ?
    """, (concurso_id, limite))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
