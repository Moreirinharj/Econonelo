import time
from utils.logger import log_acao
from database.conexao import conectar


# ===== SALDO BANCO =====

def obter_saldo_banco(personagem_id: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT saldo_banco FROM personagens WHERE id = ?", (personagem_id,))
    row = cur.fetchone()
    conn.close()
    return row["saldo_banco"] if row else 0


def modificar_saldo_banco(personagem_id: int, delta: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT saldo_banco FROM personagens WHERE id = ?", (personagem_id,))
    atual = cur.fetchone()["saldo_banco"]
    novo = max(0, atual + delta)
    cur.execute("UPDATE personagens SET saldo_banco = ? WHERE id = ?", (novo, personagem_id))
    conn.commit()
    conn.close()
    return novo


# ===== CARTÃO =====

def obter_dados_cartao(personagem_id: int) -> dict:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT limite_cartao, fatura_cartao FROM personagens WHERE id = ?", (personagem_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return {"limite": 0, "fatura": 0, "disponivel": 0}
    return {
        "limite": row["limite_cartao"],
        "fatura": row["fatura_cartao"],
        "disponivel": max(0, row["limite_cartao"] - row["fatura_cartao"]),
    }


def comprar_cartao(personagem_id: int, valor: int) -> dict:
    """Compra no cartão. Retorna sucesso + dados atualizados."""
    dados = obter_dados_cartao(personagem_id)
    if valor > dados["disponivel"]:
        return {"sucesso": False, "mensagem": "Limite insuficiente."}
    
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET fatura_cartao = fatura_cartao + ? WHERE id = ?", (valor, personagem_id))
    conn.commit()
    conn.close()
    
    novos_dados = obter_dados_cartao(personagem_id)
    log_acao("COMPRA_CARTAO", f"personagem_id={personagem_id} valor={valor}")
    return {"sucesso": True, "dados": novos_dados}


def pagar_fatura(personagem_id: int, valor: int) -> dict:
    """Paga valor da fatura usando saldo do banco."""
    dados = obter_dados_cartao(personagem_id)
    if dados["fatura"] == 0:
        return {"sucesso": False, "mensagem": "Fatura já está zerada."}
    
    valor_real = min(valor, dados["fatura"])
    saldo_banco = obter_saldo_banco(personagem_id)
    
    if saldo_banco < valor_real:
        return {"sucesso": False, "mensagem": f"Saldo do banco insuficiente. Você tem ${saldo_banco}."}
    
    modificar_saldo_banco(personagem_id, -valor_real)
    
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET fatura_cartao = fatura_cartao - ? WHERE id = ?", (valor_real, personagem_id))
    conn.commit()
    conn.close()
    
    log_acao("FATURA_PAGA", f"personagem_id={personagem_id} valor={valor_real}")
    return {"sucesso": True, "valor_pago": valor_real, "dados": obter_dados_cartao(personagem_id)}


# ===== PIX =====

def definir_chave_pix(personagem_id: int, chave: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET chave_pix = ? WHERE id = ?", (chave, personagem_id))
    conn.commit()
    conn.close()
    log_acao("CHAVE_PIX_DEFINIDA", f"personagem_id={personagem_id} chave={chave}")


def obter_chave_pix(personagem_id: int) -> str:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT chave_pix FROM personagens WHERE id = ?", (personagem_id,))
    row = cur.fetchone()
    conn.close()
    return row["chave_pix"] if row else None


def buscar_personagem_por_pix(chave: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE chave_pix = ?", (chave,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# ===== TRANSAÇÕES =====

def registrar_transacao(personagem_id: int, tipo: str, valor: int, descricao: str = None, destino_id: int = None) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transacoes (personagem_id, tipo, valor, descricao, destino_id, criado_em)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (personagem_id, tipo, valor, descricao, destino_id, time.time()))
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    return tid


def listar_transacoes(personagem_id: int, limite: int = 20):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM transacoes
        WHERE personagem_id = ?
        ORDER BY criado_em DESC
        LIMIT ?
    """, (personagem_id, limite))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
