import time
import random
from utils.logger import log_acao
from database.conexao import conectar

def obter_estado_mundo(chave: str) -> str:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT valor FROM estado_mundo WHERE chave = ?", (chave,))
    row = cur.fetchone()
    conn.close()
    return row["valor"] if row else "Desconhecido"

def atualizar_estado_mundo(chave: str, valor: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO estado_mundo (chave, valor, atualizado_em)
        VALUES (?, ?, ?)
        ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor, atualizado_em = excluded.atualizado_em
    """, (chave, valor, time.time()))
    conn.commit()
    conn.close()
    log_acao("ESTADO_MUNDO_ATUALIZADO", f"{chave} = {valor}")

def adicionar_noticia(titulo: str, corpo: str, categoria: str) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO noticias (titulo, corpo, categoria, criado_em)
        VALUES (?, ?, ?, ?)
    """, (titulo, corpo, categoria, time.time()))
    conn.commit()
    nid = cur.lastrowid
    conn.close()
    log_acao("NOTICIA_GERADA", f"id={nid} categoria={categoria}")
    return nid

def listar_noticias_recentes(limite: int = 5):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM noticias ORDER BY criado_em DESC LIMIT ?", (limite,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def simular_acao_npc_aleatoria():
    """Faz um NPC aleatório fazer algo (comprar casa, ser preso, mudar de humor)."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, cidade, dinheiro, humor FROM npcs WHERE ativo = 1 ORDER BY RANDOM() LIMIT 1")
    npc = cur.fetchone()
    if not npc:
        conn.close()
        return None
    
    acao = random.choice(["comprar", "preso", "humor", "nada"])
    msg = ""
    
    if acao == "comprar" and npc["dinheiro"] > 10000:
        gasto = random.randint(1000, 5000)
        cur.execute("UPDATE npcs SET dinheiro = dinheiro - ? WHERE id = ?", (gasto, npc["id"]))
        msg = f"NPC {npc['nome']} comprou itens no valor de ${gasto} em {npc['cidade']}."
    elif acao == "preso":
        cur.execute("UPDATE npcs SET humor = humor - 20 WHERE id = ?", (npc["id"],))
        msg = f"NPC {npc['nome']} foi detido temporariamente em {npc['cidade']}."
    elif acao == "humor":
        delta = random.randint(-15, 15)
        cur.execute("UPDATE npcs SET humor = MAX(0, MIN(100, humor + ?)) WHERE id = ?", (delta, npc["id"]))
        msg = f"O humor de {npc['nome']} em {npc['cidade']} mudou."
    
    conn.commit()
    conn.close()
    return msg
