"""IA que controla as empresas: estoque, preços, pedidos automáticos."""
import random
import json
import time
import database as db
from utils.logger import log_acao


def simular_dia_empresas() -> dict:
    """Simula um dia de operação das empresas."""
    empresas = db.listar_empresas()
    resultados = {
        "estoque_reposto": 0,
        "precos_ajustados": 0,
        "pedidos_gerados": 0,
        "empresas_falidas": 0,
        "movimentacoes": []
    }
    
    for empresa in empresas:
        # 1. Repor estoque (30% de chance por produto)
        if random.random() < 0.30:
            produtos = db.listar_produtos(empresa["id"])
            for produto in produtos:
                if produto["estoque"] < 20 and random.random() < 0.50:
                    reposicao = random.randint(30, 100)
                    conn = db.conectar()
                    cur = conn.cursor()
                    cur.execute("UPDATE produtos_empresa SET estoque = estoque + ? WHERE id = ?",
                               (reposicao, produto["id"]))
                    conn.commit()
                    conn.close()
                    resultados["estoque_reposto"] += 1
        
        # 2. Ajustar preços baseado em inflação e demanda
        if random.random() < 0.20:
            produtos = db.listar_produtos(empresa["id"])
            for produto in produtos:
                # Inflação aumenta preços
                inflacao = float(db.obter_estado_mundo("inflacao"))
                variacao = random.uniform(-0.05, 0.10) + (inflacao / 1000)
                novo_preco = max(1, int(produto["preco"] * (1 + variacao)))
                
                conn = db.conectar()
                cur = conn.cursor()
                cur.execute("UPDATE produtos_empresa SET preco = ? WHERE id = ?",
                           (novo_preco, produto["id"]))
                conn.commit()
                conn.close()
                resultados["precos_ajustados"] += 1
        
        # 3. Gerar pedidos automáticos de NPCs (20% de chance por empresa)
        if empresa["tipo"] in ["restaurante", "mercado"] and random.random() < 0.20:
            produtos = db.listar_produtos(empresa["id"])
            if produtos:
                # Escolhe 1-3 produtos aleatórios
                num_itens = random.randint(1, 3)
                itens = []
                valor_total = 0
                
                for _ in range(num_itens):
                    produto = random.choice(produtos)
                    quantidade = random.randint(1, 3)
                    itens.append({
                        "produto_id": produto["id"],
                        "nome": produto["nome"],
                        "quantidade": quantidade,
                        "preco_unitario": produto["preco"]
                    })
                    valor_total += produto["preco"] * quantidade
                
                valor_total += 10  # Taxa de entrega
                
                # Cria pedido de NPC (cliente_id = -1 pra indicar NPC)
                conn = db.conectar()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO pedidos (cliente_id, empresa_id, itens, valor_total, status, endereco_entrega, criado_em)
                    VALUES (-1, ?, ?, ?, 'pendente', ?, ?)
                """, (empresa["id"], json.dumps(itens), valor_total,
                      f"{empresa['cidade']} (NPC)", time.time()))
                pedido_id = cur.lastrowid
                conn.commit()
                conn.close()
                
                # Reduz estoque
                for item in itens:
                    db.comprar_produto(item["produto_id"], item["quantidade"])
                
                # Adiciona dinheiro ao caixa da empresa
                conn = db.conectar()
                cur = conn.cursor()
                cur.execute("UPDATE empresas SET saldo = saldo + ? WHERE id = ?",
                           (valor_total - 10, empresa["id"]))
                conn.commit()
                conn.close()
                
                resultados["pedidos_gerados"] += 1
                resultados["movimentacoes"].append(f"🛵 {empresa['nome']} gerou pedido NPC #{pedido_id}")
        
        # 4. Empresas com saldo muito baixo podem "quebrar" (5% de chance)
        if empresa["saldo"] < 500 and random.random() < 0.05:
            conn = db.conectar()
            cur = conn.cursor()
            cur.execute("UPDATE empresas SET ativo = 0 WHERE id = ?", (empresa["id"],))
            conn.commit()
            conn.close()
            resultados["empresas_falidas"] += 1
            resultados["movimentacoes"].append(f"💀 {empresa['nome']} faliu!")
        
        # 5. Empresas com saldo alto podem expandir (10% de chance)
        if empresa["saldo"] > 50000 and random.random() < 0.10:
            investimento = random.randint(5000, 15000)
            conn = db.conectar()
            cur = conn.cursor()
            cur.execute("UPDATE empresas SET saldo = saldo - ? WHERE id = ?",
                       (investimento, empresa["id"]))
            conn.commit()
            conn.close()
            resultados["movimentacoes"].append(f"📈 {empresa['nome']} investiu ${investimento} em expansão")
    
    log_acao("IA_EMPRESAS_SIMULADA", f"repostos={resultados['estoque_reposto']} ajustados={resultados['precos_ajustados']} pedidos={resultados['pedidos_gerados']}")
    
    return resultados


def gerar_noticia_empresa() -> dict:
    """Gera notícia sobre empresas."""
    empresas = db.listar_empresas()
    if not empresas:
        return None
    
    empresa = random.choice(empresas)
    
    tipos_noticia = [
        ("📈 Lucro recorde", f"{empresa['nome']} em {empresa['cidade']} reporta lucro recorde este mês."),
        ("📉 Queda nas vendas", f"{empresa['nome']} enfrenta queda de vendas devido à crise econômica."),
        ("🆕 Novo produto", f"{empresa['nome']} lança novo produto e atrai clientes em {empresa['cidade']}."),
        ("👥 Contratações", f"{empresa['nome']} anuncia contratação de 50 novos funcionários."),
        ("🏆 Prêmio de qualidade", f"{empresa['nome']} recebe prêmio de melhor empresa do ano."),
    ]
    
    titulo, corpo = random.choice(tipos_noticia)
    db.adicionar_noticia(titulo, corpo, "economia")
    
    return {"titulo": titulo, "corpo": corpo}


def ver_status_empresa(empresa_id: str) -> dict:
    """Mostra status detalhado de uma empresa."""
    empresa = db.obter_empresa(empresa_id)
    if not empresa:
        return {"sucesso": False, "msg": "Empresa não encontrada."}
    
    produtos = db.listar_produtos(empresa_id)
    
    # Calcula métricas
    total_produtos = len(produtos)
    estoque_total = sum(p["estoque"] for p in produtos)
    produtos_baixo_estoque = len([p for p in produtos if p["estoque"] < 20])
    valor_estoque = sum(p["estoque"] * p["preco"] for p in produtos)
    
    return {
        "sucesso": True,
        "empresa": empresa,
        "metricas": {
            "total_produtos": total_produtos,
            "estoque_total": estoque_total,
            "produtos_baixo_estoque": produtos_baixo_estoque,
            "valor_estoque": valor_estoque,
            "saldo_caixa": empresa["saldo"]
        }
    }
