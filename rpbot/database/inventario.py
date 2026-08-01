import time
from utils.logger import log_acao
from database.conexao import conectar


def adicionar_item(personagem_id: int, item_nome: str, item_tipo: str, quantidade: int = 1, peso: float = 1.0, dados_extra: str = None) -> int:
    """Adiciona item ao inventário. Se já existe, soma quantidade."""
    conn = conectar()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, quantidade FROM inventario
        WHERE personagem_id = ? AND item_nome = ? AND item_tipo = ?
    """, (personagem_id, item_nome, item_tipo))
    existente = cur.fetchone()
    
    if existente:
        nova_qtd = existente["quantidade"] + quantidade
        cur.execute("UPDATE inventario SET quantidade = ? WHERE id = ?", (nova_qtd, existente["id"]))
        item_id = existente["id"]
    else:
        cur.execute("""
            INSERT INTO inventario (personagem_id, item_nome, item_tipo, quantidade, peso, dados_extra, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (personagem_id, item_nome, item_tipo, quantidade, peso, dados_extra, time.time()))
        item_id = cur.lastrowid
    
    conn.commit()
    conn.close()
    log_acao("ITEM_ADICIONADO", f"personagem_id={personagem_id} item={item_nome} tipo={item_tipo} qtd={quantidade}")
    return item_id


def remover_item(personagem_id: int, item_id: int, quantidade: int = 1) -> bool:
    """Remove quantidade de um item. Se chegar a 0, deleta."""
    conn = conectar()
    cur = conn.cursor()
    
    cur.execute("SELECT quantidade FROM inventario WHERE id = ? AND personagem_id = ?", (item_id, personagem_id))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return False
    
    nova_qtd = row["quantidade"] - quantidade
    if nova_qtd <= 0:
        cur.execute("DELETE FROM inventario WHERE id = ?", (item_id,))
    else:
        cur.execute("UPDATE inventario SET quantidade = ? WHERE id = ?", (nova_qtd, item_id))
    
    conn.commit()
    conn.close()
    log_acao("ITEM_REMOVIDO", f"personagem_id={personagem_id} item_id={item_id} qtd={quantidade}")
    return True


def listar_inventario(personagem_id: int, tipo: str = None):
    """Lista itens do inventário, opcionalmente filtrando por tipo."""
    conn = conectar()
    cur = conn.cursor()
    
    if tipo:
        cur.execute("""
            SELECT * FROM inventario
            WHERE personagem_id = ? AND item_tipo = ?
            ORDER BY item_tipo, item_nome
        """, (personagem_id, tipo))
    else:
        cur.execute("""
            SELECT * FROM inventario
            WHERE personagem_id = ?
            ORDER BY item_tipo, item_nome
        """, (personagem_id,))
    
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def calcular_peso_total(personagem_id: int) -> float:
    """Calcula peso total do inventário."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT SUM(quantidade * peso) as total
        FROM inventario
        WHERE personagem_id = ?
    """, (personagem_id,))
    row = cur.fetchone()
    conn.close()
    return row["total"] if row["total"] else 0.0


def equipar_item(personagem_id: int, item_id: int) -> bool:
    """Marca item como equipado."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE inventario SET equipado = 1 WHERE id = ? AND personagem_id = ?", (item_id, personagem_id))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    if sucesso:
        log_acao("ITEM_EQUIPADO", f"personagem_id={personagem_id} item_id={item_id}")
    return sucesso


def desequipar_item(personagem_id: int, item_id: int) -> bool:
    """Desmarca item como equipado."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE inventario SET equipado = 0 WHERE id = ? AND personagem_id = ?", (item_id, personagem_id))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    if sucesso:
        log_acao("ITEM_DESEQUIPADO", f"personagem_id={personagem_id} item_id={item_id}")
    return sucesso


def obter_item(personagem_id: int, item_id: int):
    """Obtém um item específico."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventario WHERE id = ? AND personagem_id = ?", (item_id, personagem_id))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
