import sqlite3
import time

DB_PATH = "rpbot.db"


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def iniciar_banco():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS personagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            nome TEXT NOT NULL,
            idade INTEGER NOT NULL,
            cor_pele TEXT NOT NULL,
            tipo_cabelo TEXT NOT NULL,
            cor_cabelo TEXT NOT NULL,
            estado TEXT NOT NULL,
            religiao TEXT NOT NULL,
            saldo INTEGER NOT NULL DEFAULT 0,
            profissao TEXT,
            nivel INTEGER NOT NULL DEFAULT 1,
            xp INTEGER NOT NULL DEFAULT 0,
            ultimo_trabalho REAL NOT NULL DEFAULT 0,
            ativo INTEGER NOT NULL DEFAULT 0,
            criado_em REAL NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS relacionamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personagem_id INTEGER NOT NULL,
            alvo_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pendente',
            criado_em REAL NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chamados_oab (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personagem_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'aberto',
            advogado_id INTEGER,
            criado_em REAL NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS boletins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personagem_id INTEGER NOT NULL,
            descricao_original TEXT NOT NULL,
            texto_formal TEXT NOT NULL,
            criado_em REAL NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS processos_oab (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personagem_id INTEGER NOT NULL,
            alvo_id INTEGER NOT NULL,
            tipo_remocao TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'aberto',
            criado_em REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------
# PERSONAGENS
# ---------------------------------------------------------------
def contar_personagens(user_id: str) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM personagens WHERE user_id = ?", (user_id,))
    total = cur.fetchone()["c"]
    conn.close()
    return total


def criar_personagem(user_id: str, dados: dict) -> int:
    conn = conectar()
    cur = conn.cursor()
    # o novo personagem sempre vira o ativo; desativa os outros do usuário
    cur.execute("UPDATE personagens SET ativo = 0 WHERE user_id = ?", (user_id,))
    cur.execute("""
        INSERT INTO personagens
        (user_id, nome, idade, cor_pele, tipo_cabelo, cor_cabelo, estado, religiao,
         saldo, ativo, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (
        user_id, dados["nome"], dados["idade"], dados["cor_pele"], dados["tipo_cabelo"],
        dados["cor_cabelo"], dados["estado"], dados["religiao"], dados.get("saldo", 500),
        time.time(),
    ))
    conn.commit()
    novo_id = cur.lastrowid
    conn.close()
    return novo_id


def listar_personagens(user_id: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE user_id = ? ORDER BY id", (user_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def pegar_personagem_ativo(user_id: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE user_id = ? AND ativo = 1", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def pegar_personagem_por_id(personagem_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE id = ?", (personagem_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def definir_personagem_ativo(user_id: str, personagem_id: int) -> bool:
    personagens = listar_personagens(user_id)
    if not any(p["id"] == personagem_id for p in personagens):
        return False
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET ativo = 0 WHERE user_id = ?", (user_id,))
    cur.execute("UPDATE personagens SET ativo = 1 WHERE id = ?", (personagem_id,))
    conn.commit()
    conn.close()
    return True


def atualizar_saldo_personagem(personagem_id: int, delta: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT saldo FROM personagens WHERE id = ?", (personagem_id,))
    saldo_atual = cur.fetchone()["saldo"]
    novo_saldo = max(0, saldo_atual + delta)
    cur.execute("UPDATE personagens SET saldo = ? WHERE id = ?", (novo_saldo, personagem_id))
    conn.commit()
    conn.close()
    return novo_saldo


def definir_profissao_personagem(personagem_id: int, profissao: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET profissao = ? WHERE id = ?", (profissao, personagem_id))
    conn.commit()
    conn.close()


def registrar_trabalho_personagem(personagem_id: int, ganho: int, xp_ganho: int):
    from data.config import xp_para_proximo_nivel
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT saldo, xp, nivel FROM personagens WHERE id = ?", (personagem_id,))
    row = cur.fetchone()
    novo_saldo = row["saldo"] + ganho
    novo_xp = row["xp"] + xp_ganho
    nivel = row["nivel"]

    subiu_nivel = False
    while novo_xp >= xp_para_proximo_nivel(nivel):
        novo_xp -= xp_para_proximo_nivel(nivel)
        nivel += 1
        subiu_nivel = True

    cur.execute(
        "UPDATE personagens SET saldo = ?, xp = ?, nivel = ?, ultimo_trabalho = ? WHERE id = ?",
        (novo_saldo, novo_xp, nivel, time.time(), personagem_id),
    )
    conn.commit()
    conn.close()
    return {"saldo": novo_saldo, "nivel": nivel, "subiu_nivel": subiu_nivel}


def top_saldos(limite: int = 10):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens ORDER BY saldo DESC LIMIT ?", (limite,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def todos_personagens():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ---------------------------------------------------------------
# RELACIONAMENTOS (família / amigos / amantes)
# ---------------------------------------------------------------
def criar_pedido_relacao(personagem_id: int, alvo_id: int, tipo: str) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO relacionamentos (personagem_id, alvo_id, tipo, status, criado_em)
        VALUES (?, ?, ?, 'pendente', ?)
    """, (personagem_id, alvo_id, tipo, time.time()))
    conn.commit()
    pedido_id = cur.lastrowid
    conn.close()
    return pedido_id


def responder_pedido_relacao(pedido_id: int, aceitar: bool):
    conn = conectar()
    cur = conn.cursor()
    if aceitar:
        cur.execute("UPDATE relacionamentos SET status = 'aceito' WHERE id = ?", (pedido_id,))
    else:
        cur.execute("DELETE FROM relacionamentos WHERE id = ?", (pedido_id,))
    conn.commit()
    conn.close()


def remover_relacao_direta(personagem_id: int, alvo_id: int, tipo: str) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM relacionamentos
        WHERE personagem_id = ? AND alvo_id = ? AND tipo = ? AND status = 'aceito'
    """, (personagem_id, alvo_id, tipo))
    afetou = cur.rowcount > 0
    conn.commit()
    conn.close()
    return afetou


def listar_familia(personagem_id: int):
    """Retorna todas as relações aceitas envolvendo esse personagem, nos dois sentidos."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM relacionamentos
        WHERE (personagem_id = ? OR alvo_id = ?) AND status = 'aceito'
    """, (personagem_id, personagem_id))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def ja_existe_relacao(personagem_id: int, alvo_id: int, tipo: str) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as c FROM relacionamentos
        WHERE personagem_id = ? AND alvo_id = ? AND tipo = ? AND status IN ('pendente', 'aceito')
    """, (personagem_id, alvo_id, tipo))
    total = cur.fetchone()["c"]
    conn.close()
    return total > 0


def contar_pais(personagem_id: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as c FROM relacionamentos
        WHERE personagem_id = ? AND tipo IN ('pai', 'mae') AND status = 'aceito'
    """, (personagem_id,))
    total = cur.fetchone()["c"]
    conn.close()
    return total


# ---------------------------------------------------------------
# CHAMADOS OAB (hub geral: qualquer assunto jurídico não estruturado)
# ---------------------------------------------------------------
def abrir_chamado_oab(personagem_id: int, descricao: str) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chamados_oab (personagem_id, descricao, status, criado_em)
        VALUES (?, ?, 'aberto', ?)
    """, (personagem_id, descricao, time.time()))
    conn.commit()
    chamado_id = cur.lastrowid
    conn.close()
    return chamado_id


def listar_advogados_disponiveis():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM personagens WHERE profissao IN ('advogado', 'advogado_criminal')
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def assumir_chamado_oab(chamado_id: int, advogado_personagem_id: int) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE chamados_oab SET status = 'em_andamento', advogado_id = ?
        WHERE id = ? AND status = 'aberto'
    """, (advogado_personagem_id, chamado_id))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    return sucesso


# ---------------------------------------------------------------
# BOLETINS DE OCORRÊNCIA (redigidos pela IA jurídica)
# ---------------------------------------------------------------
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
    return boletim_id


def listar_boletins(personagem_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM boletins WHERE personagem_id = ? ORDER BY id DESC", (personagem_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ---------------------------------------------------------------
# PROCESSOS OAB (remoção de pai/mãe/filho/filha)
# ---------------------------------------------------------------
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
    return dict(processo)
