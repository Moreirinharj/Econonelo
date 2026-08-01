"""Funções para gerenciar pedidos de delivery."""
from database.conexao import conectar
import time
import json


def criar_pedido(empresa_id: str, cliente_id: int, produtos: list, valor_total: float, endereco_entrega: str) -> int:
    """Cria um novo pedido de delivery."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pedidos_delivery (empresa_id, cliente_id, produtos, valor_total, endereco_entrega, status, criado_em)
        VALUES (?, ?, ?, ?, ?, 'pendente', ?)
    """, (empresa_id, cliente_id, json.dumps(produtos), valor_total, endereco_entrega, time.time()))
    pedido_id = cur.lastrowid
    conn.commit()
    conn.close()
    return pedido_id


def listar_pedidos(status: str = None, cliente_id: int = None) -> list:
    """Lista pedidos."""
    conn = conectar()
    cur = conn.cursor()
    
    query = "SELECT * FROM pedidos_delivery WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if cliente_id:
        query += " AND cliente_id = ?"
        params.append(cliente_id)
    
    query += " ORDER BY criado_em DESC"
    cur.execute(query, params)
    pedidos = [dict(row) for row in cur.fetchall()]
    
    # Converter produtos de JSON para list
    for pedido in pedidos:
        if pedido.get('produtos'):
            try:
                pedido['produtos'] = json.loads(pedido['produtos'])
            except:
                pedido['produtos'] = []
    
    conn.close()
    return pedidos


def obter_pedido(pedido_id: int) -> dict:
    """Obtém um pedido específico."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pedidos_delivery WHERE id = ?", (pedido_id,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        pedido = dict(row)
        if pedido.get('produtos'):
            try:
                pedido['produtos'] = json.loads(pedido['produtos'])
            except:
                pedido['produtos'] = []
        return pedido
    return None


def atribuir_motoboy(pedido_id: int, motoboy_id: int) -> bool:
    """Atribui motoboy a um pedido."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE pedidos_delivery SET motoboy_id = ?, status = 'em_entrega' WHERE id = ?",
                (motoboy_id, pedido_id))
    conn.commit()
    conn.close()
    return True


def finalizar_entrega(pedido_id: int) -> bool:
    """Finaliza entrega de um pedido."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE pedidos_delivery SET status = 'entregue', entregue_em = ? WHERE id = ?",
                (time.time(), pedido_id))
    conn.commit()
    conn.close()
    return True
