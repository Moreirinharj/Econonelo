"""Funções para gerenciar produtos das empresas."""
from database.conexao import conectar


def adicionar_produto(empresa_id: str, nome: str, preco: float, estoque: int = 0, descricao: str = None, categoria: str = None) -> int:
    """Adiciona um produto a uma empresa."""
    import time
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO produtos (empresa_id, nome, preco, estoque, descricao, categoria, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (empresa_id, nome, preco, estoque, descricao, categoria, time.time()))
    produto_id = cur.lastrowid
    conn.commit()
    conn.close()
    return produto_id


def listar_produtos(empresa_id: str) -> list:
    """Lista produtos de uma empresa."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produtos WHERE empresa_id = ? ORDER BY nome", (empresa_id,))
    produtos = [dict(row) for row in cur.fetchall()]
    conn.close()
    return produtos


def obter_produto(produto_id: int) -> dict:
    """Obtém um produto específico."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def comprar_produto(empresa_id: str, produto_id: int, quantidade: int) -> bool:
    """Processa compra de produto."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND empresa_id = ? AND estoque >= ?",
                (quantidade, produto_id, empresa_id, quantidade))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    return sucesso


def atualizar_estoque(produto_id: int, quantidade: int) -> bool:
    """Atualiza estoque de um produto."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE produtos SET estoque = ? WHERE id = ?", (quantidade, produto_id))
    conn.commit()
    conn.close()
    return True
