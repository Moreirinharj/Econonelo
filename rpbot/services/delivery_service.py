"""Sistema de delivery/iFood integrado com empresas e motoboys."""
import json
import random
import time
import database as db
from utils.logger import log_acao
from services.clima_service import obter_bonus_motoboy


def listar_empresas_delivery(estado_atual: str = None) -> list:
    """Lista empresas que fazem delivery."""
    empresas = db.listar_empresas(tipo="restaurante")
    empresas.extend(db.listar_empresas(tipo="mercado"))
    
    if estado_atual:
        # Filtra por estado (cidade começa com UF ou contém nome do estado)
        empresas = [e for e in empresas if estado_atual in e.get("cidade", "")]
    
    return empresas


def criar_pedido(personagem_id: int, empresa_id: str, itens: list) -> dict:
    """Cria um pedido de delivery."""
    personagem = db.obter_personagem_por_id(personagem_id)
    empresa = db.obter_empresa(empresa_id)
    
    if not personagem:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    if not empresa:
        return {"sucesso": False, "msg": "Empresa não encontrada."}
    
    # Calcula valor total
    valor_total = 0
    itens_validos = []
    
    for item in itens:
        produto_id = item["produto_id"]
        quantidade = item.get("quantidade", 1)
        
        produto = db.obter_produto(produto_id)
        if not produto or produto["empresa_id"] != empresa_id:
            continue
        
        if produto["estoque"] < quantidade:
            return {"sucesso": False, "msg": f"Estoque insuficiente de {produto['nome']}. Disponível: {produto['estoque']}"}
        
        valor_total += produto["preco"] * quantidade
        itens_validos.append({
            "produto_id": produto_id,
            "nome": produto["nome"],
            "quantidade": quantidade,
            "preco_unitario": produto["preco"]
        })
    
    if not itens_validos:
        return {"sucesso": False, "msg": "Nenhum item válido no pedido."}
    
    # Adiciona taxa de entrega
    taxa_entrega = 10
    valor_total += taxa_entrega
    
    # Verifica saldo
    if personagem["saldo"] < valor_total:
        return {
            "sucesso": False,
            "msg": f"💸 Saldo insuficiente! Total: ${valor_total} (inclui taxa de entrega ${taxa_entrega})",
            "helper": "💡 Usa `?trabalhar` pra fazer uma grana ou `?sacar` do banco."
        }
    
    # Cria pedido
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pedidos (cliente_id, empresa_id, itens, valor_total, status, endereco_entrega, criado_em)
        VALUES (?, ?, ?, ?, 'pendente', ?, ?)
    """, (personagem_id, empresa_id, json.dumps(itens_validos), valor_total, 
          f"{personagem.get('estado_atual', 'SP')}, {personagem.get('estado', 'SP')}", time.time()))
    pedido_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    # Desconta do personagem
    db.atualizar_saldo_personagem(personagem_id, -valor_total)
    
    # Reduz estoque
    for item in itens_validos:
        db.comprar_produto(item["produto_id"], item["quantidade"])
    
    # Adiciona dinheiro ao caixa da empresa
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE empresas SET saldo = saldo + ? WHERE id = ?", (valor_total - taxa_entrega, empresa_id))
    conn.commit()
    conn.close()
    
    db.registrar_transacao(personagem_id, "delivery", valor_total, f"Pedido em {empresa['nome']}")
    
    log_acao("PEDIDO_CRIADO", f"pedido_id={pedido_id} cliente={personagem_id} empresa={empresa_id} valor={valor_total}")
    
    # Tenta acionar um motoboy
    motoboy_id = acionar_motoboy(personagem_id, pedido_id)
    
    return {
        "sucesso": True,
        "pedido_id": pedido_id,
        "valor_total": valor_total,
        "taxa_entrega": taxa_entrega,
        "empresa": empresa["nome"],
        "itens": itens_validos,
        "motoboy_id": motoboy_id,
        "msg": f"🛵 **Pedido realizado!**\n\n**Empresa:** {empresa['nome']}\n**Total:** ${valor_total} (inclui taxa ${taxa_entrega})\n**Status:** Aguardando motoboy"
    }


def acionar_motoboy(cliente_id: int, pedido_id: int) -> int:
    """Tenta acionar um motoboy disponível."""
    # Busca motoboys disponíveis (profissão motoboy e não presos)
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id FROM personagens 
        WHERE profissao = 'motoboy' AND preso = 0 AND ativo = 1
        ORDER BY RANDOM() LIMIT 1
    """)
    motoboy = cur.fetchone()
    conn.close()
    
    if motoboy:
        # Atualiza pedido com motoboy
        conn = db.conectar()
        cur = conn.cursor()
        cur.execute("UPDATE pedidos SET motoboy_id = ?, status = 'em_entrega' WHERE id = ?", 
                   (motoboy["id"], pedido_id))
        conn.commit()
        conn.close()
        
        log_acao("MOTOBOYACIONADO", f"pedido={pedido_id} motoboy={motoboy['id']}")
        return motoboy["id"]
    
    return None


def completar_pedido(pedido_id: int, motoboy_id: int) -> dict:
    """Motoboy completa a entrega."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pedidos WHERE id = ? AND motoboy_id = ?", (pedido_id, motoboy_id))
    pedido = cur.fetchone()
    conn.close()
    
    if not pedido:
        return {"sucesso": False, "msg": "Pedido não encontrado ou não é seu."}
    
    if pedido["status"] == "entregue":
        return {"sucesso": False, "msg": "Esse pedido já foi entregue."}
    
    # Atualiza status
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE pedidos SET status = 'entregue' WHERE id = ?", (pedido_id,))
    conn.commit()
    conn.close()
    
    # Paga o motoboy (30% do valor do pedido)
    bonus_clima = obter_bonus_motoboy()
    pagamento_base = int(pedido["valor_total"] * 0.30)
    pagamento = int(pagamento_base * bonus_clima)
    db.atualizar_saldo_personagem(motoboy_id, pagamento)
    db.registrar_transacao(motoboy_id, "salario_delivery", pagamento, f"Entrega do pedido #{pedido_id}")
    db.registrar_trabalho_personagem(motoboy_id, 0, 15)
    
    log_acao("ENTREGA_COMPLETA", f"pedido={pedido_id} motoboy={motoboy_id} pagamento={pagamento}")
    
    return {
        "sucesso": True,
        "pagamento": pagamento,
        "msg": f"✅ **Entrega concluída!**\n\nVocê recebeu ${pagamento} pela entrega do pedido #{pedido_id}."
    }


def listar_pedidos_pendentes(motoboy_id: int) -> list:
    """Lista pedidos pendentes pra um motoboy aceitar."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, e.nome as empresa_nome
        FROM pedidos p
        JOIN empresas e ON p.empresa_id = e.id
        WHERE p.status = 'pendente' AND p.motoboy_id IS NULL
        ORDER BY p.criado_em ASC
        LIMIT 10
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def aceitar_pedido(motoboy_id: int, pedido_id: int) -> dict:
    """Motoboy aceita um pedido pendente."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pedidos WHERE id = ? AND status = 'pendente' AND motoboy_id IS NULL", (pedido_id,))
    pedido = cur.fetchone()
    conn.close()
    
    if not pedido:
        return {"sucesso": False, "msg": "Pedido não encontrado ou já foi aceito."}
    
    # Atualiza pedido com motoboy
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE pedidos SET motoboy_id = ?, status = 'em_entrega' WHERE id = ?", 
               (motoboy_id, pedido_id))
    conn.commit()
    conn.close()
    
    log_acao("PEDIDO_ACEITO", f"pedido={pedido_id} motoboy={motoboy_id}")
    
    return {
        "sucesso": True,
        "msg": f"🛵 **Pedido aceito!**\n\nVá até a empresa e entregue o pedido #{pedido_id}.\nAo concluir, usa `?completarentrega {pedido_id}` pra receber."
    }
