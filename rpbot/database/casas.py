import time
from utils.logger import log_acao
from database.conexao import conectar


def criar_casa(nome: str, tipo: str, cidade: str, bairro: str, preco: int, garagem: int = 0) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO casas (nome, tipo, cidade, bairro, preco, garagem, vendido, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, 0, ?)
    """, (nome, tipo, cidade, bairro, preco, garagem, time.time()))
    conn.commit()
    casa_id = cur.lastrowid
    conn.close()
    log_acao("CASA_CRIADA", f"id={casa_id} nome={nome} preco={preco}")
    return casa_id


def obter_casa(casa_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM casas WHERE id = ?", (casa_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def listar_casas_disponiveis(cidade: str = None, tipo: str = None):
    conn = conectar()
    cur = conn.cursor()
    
    query = "SELECT * FROM casas WHERE vendido = 0"
    params = []
    
    if cidade:
        query += " AND cidade = ?"
        params.append(cidade)
    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    
    query += " ORDER BY preco ASC"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def listar_casas_do_proprietario(personagem_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM casas WHERE proprietario_id = ? AND vendido = 1", (personagem_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def comprar_casa(casa_id: int, personagem_id: int) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE casas SET proprietario_id = ?, vendido = 1
        WHERE id = ? AND vendido = 0
    """, (personagem_id, casa_id))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    if sucesso:
        log_acao("CASA_COMPRADA", f"casa_id={casa_id} personagem_id={personagem_id}")
    return sucesso


def vender_casa(casa_id: int) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE casas SET proprietario_id = NULL, vendido = 0
        WHERE id = ?
    """, (casa_id,))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    if sucesso:
        log_acao("CASA_VENDIDA", f"casa_id={casa_id}")
    return sucesso


def depositar_no_cofre(casa_id: int, valor: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT cofre FROM casas WHERE id = ?", (casa_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return -1
    
    novo_cofre = row["cofre"] + valor
    cur.execute("UPDATE casas SET cofre = ? WHERE id = ?", (novo_cofre, casa_id))
    conn.commit()
    conn.close()
    return novo_cofre


def sacar_do_cofre(casa_id: int, valor: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT cofre FROM casas WHERE id = ?", (casa_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return -1
    
    novo_cofre = max(0, row["cofre"] - valor)
    cur.execute("UPDATE casas SET cofre = ? WHERE id = ?", (novo_cofre, casa_id))
    conn.commit()
    conn.close()
    return novo_cofre


def mudar_decoracao(casa_id: int, decoracao: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE casas SET decoracao = ? WHERE id = ?", (decoracao, casa_id))
    conn.commit()
    conn.close()
    log_acao("DECORACAO_MUDADA", f"casa_id={casa_id} decoracao={decoracao}")
