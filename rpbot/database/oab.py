import time
from utils.logger import log_acao
from database.conexao import conectar


def salvar_boletim(personagem_id: int, descricao_original: str, texto_formal: str) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO boletins (personagem_id, descricao_original, texto_formal, criado_em)
        VALUES (?, ?, ?, ?)
    """, (personagem_id, descricao_original, texto_formal, time.time()))
    conn.commit()
    boletim_id = cur.lastrowid
    conn.close()
    log_acao("BOLETIM_SALVO", f"id={boletim_id} personagem_id={personagem_id}")
    return boletim_id


def listar_boletins(personagem_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM boletins WHERE personagem_id = ? ORDER BY id DESC", (personagem_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def abrir_processo_oab(personagem_id: int, alvo_id: int, tipo_remocao: str) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO processos_oab (personagem_id, alvo_id, tipo_remocao, status, criado_em)
        VALUES (?, ?, ?, 'aberto', ?)
    """, (personagem_id, alvo_id, tipo_remocao, time.time()))
    conn.commit()
    processo_id = cur.lastrowid
    conn.close()
    log_acao("PROCESSO_OAB_ABERTO", f"id={processo_id} de={personagem_id} para={alvo_id} tipo={tipo_remocao}")
    return processo_id


def listar_processos_abertos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM processos_oab WHERE status = 'aberto'")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def resolver_processo_oab(processo_id: int, aprovar: bool):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM processos_oab WHERE id = ?", (processo_id,))
    processo = cur.fetchone()
    if processo is None:
        conn.close()
        return None

    novo_status = "aprovado" if aprovar else "negado"
    cur.execute("UPDATE processos_oab SET status = ? WHERE id = ?", (novo_status, processo_id))

    if aprovar:
        cur.execute("""
            DELETE FROM relacionamentos
            WHERE personagem_id = ? AND alvo_id = ? AND tipo = ? AND status = 'aceito'
        """, (processo["personagem_id"], processo["alvo_id"], processo["tipo_remocao"]))

    conn.commit()
    conn.close()
    log_acao("PROCESSO_OAB_RESOLVIDO", f"id={processo_id} status={novo_status}")
    return dict(processo)
