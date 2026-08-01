import time
import json
from utils.logger import log_acao
from database.conexao import conectar


def criar_empresa(empresa_id: str, nome: str, tipo: str, descricao: str, cidade: str, bairro: str = None, saldo: int = 10000) -> bool:
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO empresas (id, nome, tipo, descricao, cidade, bairro, saldo, ativo, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (empresa_id, nome, tipo, descricao, cidade, bairro, saldo, time.time()))
        conn.commit()
        conn.close()
        log_acao("EMPRESA_CRIADA", f"id={empresa_id} nome={nome}")
        return True
    except Exception as e:
        conn.close()
        return False


def obter_empresa(empresa_id: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM empresas WHERE id = ? AND ativo = 1", (empresa_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def listar_empresas(tipo: str = None, cidade: str = None):
    conn = conectar()
    cur = conn.cursor()
    query = "SELECT * FROM empresas WHERE ativo = 1"
    params = []
    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    if cidade:
        query += " AND cidade = ?"
        params.append(cidade)
    query += " ORDER BY nome"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def adicionar_produto(empresa_id: str, nome: str, categoria: str, preco: int, estoque: int) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO produtos_empresa (empresa_id, nome, categoria, preco, estoque)
        VALUES (?, ?, ?, ?, ?)
    """, (empresa_id, nome, categoria, preco, estoque))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def listar_produtos(empresa_id: str, categoria: str = None):
    conn = conectar()
    cur = conn.cursor()
    if categoria:
        cur.execute("SELECT * FROM produtos_empresa WHERE empresa_id = ? AND categoria = ? AND estoque > 0", (empresa_id, categoria))
    else:
        cur.execute("SELECT * FROM produtos_empresa WHERE empresa_id = ? AND estoque > 0", (empresa_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def obter_produto(produto_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produtos_empresa WHERE id = ?", (produto_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def comprar_produto(produto_id: int, quantidade: int) -> dict:
    """Reduz estoque e retorna produto atualizado."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produtos_empresa WHERE id = ?", (produto_id,))
    produto = cur.fetchone()
    if not produto:
        conn.close()
        return {"sucesso": False, "msg": "Produto não encontrado."}
    
    if produto["estoque"] < quantidade:
        conn.close()
        return {"sucesso": False, "msg": f"Estoque insuficiente. Disponível: {produto['estoque']}"}
    
    cur.execute("UPDATE produtos_empresa SET estoque = estoque - ? WHERE id = ?", (quantidade, produto_id))
    conn.commit()
    conn.close()
    
    # Adiciona dinheiro ao caixa da empresa
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE empresas SET saldo = saldo + ? WHERE id = ?", (produto["preco"] * quantidade, produto["empresa_id"]))
    conn.commit()
    conn.close()
    
    return {"sucesso": True, "produto": dict(produto), "quantidade": quantidade}


# ===== VAGAS DE EMPREGO =====

def criar_vaga(empresa_id: str, profissao: str, escolaridade: str, salario: int, vagas: int, descricao: str) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO vagas_emprego (empresa_id, profissao, escolaridade_req, salario, vagas, descricao, ativa, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    """, (empresa_id, profissao, escolaridade, salario, vagas, descricao, time.time()))
    conn.commit()
    vid = cur.lastrowid
    conn.close()
    return vid


def listar_vagas(profissao: str = None, escolaridade_min: str = None, ativa: bool = True):
    conn = conectar()
    cur = conn.cursor()
    query = """
        SELECT v.*, e.nome as empresa_nome, e.cidade
        FROM vagas_emprego v
        JOIN empresas e ON v.empresa_id = e.id
        WHERE v.ativa = 1 AND v.vagas > 0
    """
    params = []
    if profissao:
        query += " AND v.profissao = ?"
        params.append(profissao)
    if escolaridade_min:
        niveis = {"nenhuma": 0, "fundamental": 1, "medio": 2, "superior": 3, "pos": 4}
        nivel_min = niveis.get(escolaridade_min, 0)
        # SQLite não suporta comparação direta, filtramos depois
        pass
    query += " ORDER BY v.salario DESC"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    
    # Filtra por escolaridade
    if escolaridade_min:
        niveis = {"nenhuma": 0, "fundamental": 1, "medio": 2, "superior": 3, "pos": 4}
        nivel_min = niveis.get(escolaridade_min, 0)
        rows = [r for r in rows if niveis.get(r["escolaridade_req"], 0) <= nivel_min]
    
    return rows


def obter_vaga(vaga_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vagas_emprego WHERE id = ?", (vaga_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def contratar_personagem(vaga_id: int, personagem_id: int) -> dict:
    """Contrata personagem na vaga."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vagas_emprego WHERE id = ? AND ativa = 1 AND vagas > 0", (vaga_id,))
    vaga = cur.fetchone()
    if not vaga:
        conn.close()
        return {"sucesso": False, "msg": "Vaga não disponível."}
    
    cur.execute("UPDATE vagas_emprego SET vagas = vagas - 1 WHERE id = ?", (vaga_id,))
    cur.execute("UPDATE personagens SET profissao = ?, ultimo_trabalho = ? WHERE id = ?", 
                (vaga["profissao"], time.time(), personagem_id))
    conn.commit()
    conn.close()
    
    log_acao("CONTRATADO", f"personagem={personagem_id} vaga={vaga_id} profissao={vaga['profissao']}")
    return {"sucesso": True, "vaga": dict(vaga)}


def pedir_demissao_empresa(personagem_id: int) -> dict:
    """Personagem pede demissão."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET profissao = NULL WHERE id = ?", (personagem_id,))
    conn.commit()
    conn.close()
    return {"sucesso": True, "msg": "Você pediu demissão."}
