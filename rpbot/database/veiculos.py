import time
import random
import string
from utils.logger import log_acao
from database.conexao import conectar


def gerar_placa() -> str:
    """Gera uma placa no formato AAA-0A00 ou AAA-0000."""
    letras = ''.join(random.choices(string.ascii_uppercase, k=3))
    if random.choice([True, False]):
        numeros = f"{random.randint(0, 9)}{random.choice(string.ascii_uppercase)}{random.randint(0, 9)}{random.randint(0, 9)}"
    else:
        numeros = f"{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}"
    return f"{letras}-{numeros}"


def criar_veiculo(modelo: str, valor: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    placa = gerar_placa()
    
    # Garante que a placa é única
    while True:
        cur.execute("SELECT id FROM veiculos WHERE placa = ?", (placa,))
        if cur.fetchone() is None:
            break
        placa = gerar_placa()
        
    cur.execute("""
        INSERT INTO veiculos (modelo, placa, combustivel, saude, seguro_ativo, documentacao, valor, vendido, criado_em)
        VALUES (?, ?, 100, 100, 0, 'regular', ?, 0, ?)
    """, (modelo, placa, valor, time.time()))
    conn.commit()
    veiculo_id = cur.lastrowid
    conn.close()
    log_acao("VEICULO_CRIADO", f"id={veiculo_id} modelo={modelo} placa={placa}")
    return veiculo_id


def obter_veiculo(veiculo_id: int = None, placa: str = None):
    conn = conectar()
    cur = conn.cursor()
    if veiculo_id:
        cur.execute("SELECT * FROM veiculos WHERE id = ?", (veiculo_id,))
    elif placa:
        cur.execute("SELECT * FROM veiculos WHERE placa = ?", (placa.upper(),))
    else:
        conn.close()
        return None
    
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def listar_veiculos_disponiveis():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM veiculos WHERE vendido = 0 ORDER BY valor ASC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def listar_veiculos_do_proprietario(personagem_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM veiculos WHERE proprietario_id = ? AND vendido = 1", (personagem_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def comprar_veiculo(veiculo_id: int, personagem_id: int) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE veiculos SET proprietario_id = ?, vendido = 1
        WHERE id = ? AND vendido = 0
    """, (personagem_id, veiculo_id))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    if sucesso:
        log_acao("VEICULO_COMPRADO", f"veiculo_id={veiculo_id} personagem_id={personagem_id}")
    return sucesso


def vender_veiculo(veiculo_id: int) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE veiculos SET proprietario_id = NULL, vendido = 0 WHERE id = ?", (veiculo_id,))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    if sucesso:
        log_acao("VEICULO_VENDIDO", f"veiculo_id={veiculo_id}")
    return sucesso


def abastecer_veiculo(veiculo_id: int, litros: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT combustivel FROM veiculos WHERE id = ?", (veiculo_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return -1
    
    novo_combustivel = min(100, row["combustivel"] + litros)
    cur.execute("UPDATE veiculos SET combustivel = ? WHERE id = ?", (novo_combustivel, veiculo_id))
    conn.commit()
    conn.close()
    return novo_combustivel


def reparar_veiculo(veiculo_id: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE veiculos SET saude = 100 WHERE id = ?", (veiculo_id,))
    conn.commit()
    conn.close()
    log_acao("VEICULO_REPARADO", f"veiculo_id={veiculo_id}")
    return 100


def toggle_seguro(veiculo_id: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT seguro_ativo FROM veiculos WHERE id = ?", (veiculo_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return -1
    
    novo_status = 1 if row["seguro_ativo"] == 0 else 0
    cur.execute("UPDATE veiculos SET seguro_ativo = ? WHERE id = ?", (novo_status, veiculo_id))
    conn.commit()
    conn.close()
    log_acao("SEGURO_VEICULO", f"veiculo_id={veiculo_id} ativo={novo_status}")
    return novo_status


def aplicar_acidente(veiculo_id: int, severidade: int) -> dict:
    """Aplica dano ao veículo. Retorna dano e se o seguro cobriu."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT saude, seguro_ativo FROM veiculos WHERE id = ?", (veiculo_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return {"sucesso": False, "mensagem": "Veículo não encontrado."}
    
    dano = min(row["saude"], severidade)
    nova_saude = row["saude"] - dano
    coberto_seguro = row["seguro_ativo"] == 1
    
    cur.execute("UPDATE veiculos SET saude = ? WHERE id = ?", (nova_saude, veiculo_id))
    conn.commit()
    conn.close()
    
    log_acao("ACIDENTE_VEICULO", f"veiculo_id={veiculo_id} dano={dano} seguro={coberto_seguro}")
    return {
        "sucesso": True,
        "dano": dano,
        "nova_saude": nova_saude,
        "coberto_seguro": coberto_seguro
    }
