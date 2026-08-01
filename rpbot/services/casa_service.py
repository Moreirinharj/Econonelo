"""Lógica de casas/imóveis."""
import database as db
from utils.logger import log_acao

DECORACOES = {
    "basica": {"nome": "Básica", "preco": 0},
    "moderna": {"nome": "Moderna", "preco": 5000},
    "luxo": {"nome": "Luxo", "preco": 20000},
    "rustica": {"nome": "Rústica", "preco": 3000},
}

TIPOS_CASA = {
    "apartamento": {"nome": "Apartamento", "preco_base": 50000, "garagem": 1},
    "casa": {"nome": "Casa", "preco_base": 80000, "garagem": 2},
    "cobertura": {"nome": "Cobertura", "preco_base": 200000, "garagem": 3},
    "mansao": {"nome": "Mansão", "preco_base": 500000, "garagem": 5},
}


def comprar_imovel(personagem_id: int, casa_id: int) -> dict:
    """Compra uma casa."""
    casa = db.obter_casa(casa_id)
    if casa is None:
        return {"sucesso": False, "mensagem": "Casa não encontrada."}
    
    if casa["vendido"]:
        return {"sucesso": False, "mensagem": "Essa casa já foi vendida."}
    
    personagem = db.obter_personagem_por_id(personagem_id)
    saldo_total = personagem["saldo"] + db.obter_saldo_banco(personagem_id)
    
    if saldo_total < casa["preco"]:
        return {"sucesso": False, "mensagem": f"Saldo insuficiente. Você tem ${saldo_total}, a casa custa ${casa['preco']}."}
    
    valor_restante = casa["preco"]
    saldo_bolso = personagem["saldo"]
    
    if saldo_bolso >= valor_restante:
        db.atualizar_saldo_personagem(personagem_id, -valor_restante)
    else:
        db.atualizar_saldo_personagem(personagem_id, -saldo_bolso)
        valor_restante -= saldo_bolso
        db.modificar_saldo_banco(personagem_id, -valor_restante)
    
    db.comprar_casa(casa_id, personagem_id)
    db.registrar_transacao(personagem_id, "compra_casa", casa["preco"], f"Compra de {casa['nome']}")
    
    log_acao("CASA_COMPRADA_SERVICE", f"personagem_id={personagem_id} casa_id={casa_id}")
    return {
        "sucesso": True,
        "mensagem": f"Você comprou {casa['nome']} por ${casa['preco']}!",
        "casa": casa,
    }


def vender_imovel(personagem_id: int, casa_id: int) -> dict:
    """Vende uma casa do personagem."""
    casa = db.obter_casa(casa_id)
    if casa is None:
        return {"sucesso": False, "mensagem": "Casa não encontrada."}
    
    if casa["proprietario_id"] != personagem_id:
        return {"sucesso": False, "mensagem": "Essa casa não é sua."}
    
    preco_venda = int(casa["preco"] * 0.8)
    db.atualizar_saldo_personagem(personagem_id, preco_venda)
    db.vender_casa(casa_id)
    db.registrar_transacao(personagem_id, "venda_casa", preco_venda, f"Venda de {casa['nome']}")
    
    log_acao("CASA_VENDIDA_SERVICE", f"personagem_id={personagem_id} casa_id={casa_id}")
    return {
        "sucesso": True,
        "mensagem": f"Você vendeu {casa['nome']} por ${preco_venda}!",
        "preco_venda": preco_venda,
    }


def reformar_casa(personagem_id: int, casa_id: int, decoracao: str) -> dict:
    """Reforma/muda decoração da casa."""
    casa = db.obter_casa(casa_id)
    if casa is None:
        return {"sucesso": False, "mensagem": "Casa não encontrada."}
    
    if casa["proprietario_id"] != personagem_id:
        return {"sucesso": False, "mensagem": "Essa casa não é sua."}
    
    if decoracao not in DECORACOES:
        return {"sucesso": False, "mensagem": f"Decoração inválida. Opções: {', '.join(DECORACOES.keys())}"}
    
    preco = DECORACOES[decoracao]["preco"]
    if preco > 0:
        personagem = db.obter_personagem_por_id(personagem_id)
        if personagem["saldo"] < preco:
            return {"sucesso": False, "mensagem": f"Saldo insuficiente. Reforma custa ${preco}."}
        db.atualizar_saldo_personagem(personagem_id, -preco)
    
    db.mudar_decoracao(casa_id, decoracao)
    log_acao("CASA_REFORMADA", f"personagem_id={personagem_id} casa_id={casa_id} decoracao={decoracao}")
    return {
        "sucesso": True,
        "mensagem": f"Casa reformada! Nova decoração: {DECORACOES[decoracao]['nome']}",
    }


def depositar_cofre(personagem_id: int, casa_id: int, valor: int) -> dict:
    """Deposita dinheiro no cofre da casa."""
    casa = db.obter_casa(casa_id)
    if casa is None:
        return {"sucesso": False, "mensagem": "Casa não encontrada."}
    
    if casa["proprietario_id"] != personagem_id:
        return {"sucesso": False, "mensagem": "Essa casa não é sua."}
    
    personagem = db.obter_personagem_por_id(personagem_id)
    if personagem["saldo"] < valor:
        return {"sucesso": False, "mensagem": "Dinheiro insuficiente no bolso."}
    
    db.atualizar_saldo_personagem(personagem_id, -valor)
    novo_cofre = db.depositar_no_cofre(casa_id, valor)
    
    return {
        "sucesso": True,
        "mensagem": f"Você depositou ${valor} no cofre. Total no cofre: ${novo_cofre}",
        "novo_cofre": novo_cofre,
    }


def sacar_cofre(personagem_id: int, casa_id: int, valor: int) -> dict:
    """Saca dinheiro do cofre da casa."""
    casa = db.obter_casa(casa_id)
    if casa is None:
        return {"sucesso": False, "mensagem": "Casa não encontrada."}
    
    if casa["proprietario_id"] != personagem_id:
        return {"sucesso": False, "mensagem": "Essa casa não é sua."}
    
    if casa["cofre"] < valor:
        return {"sucesso": False, "mensagem": f"Cofre tem apenas ${casa['cofre']}."}
    
    novo_cofre = db.sacar_do_cofre(casa_id, valor)
    db.atualizar_saldo_personagem(personagem_id, valor)
    
    return {
        "sucesso": True,
        "mensagem": f"Você sacou ${valor} do cofre. Restante no cofre: ${novo_cofre}",
        "novo_cofre": novo_cofre,
    }


def popular_casas() -> int:
    """Popula o mundo com casas disponíveis pra compra."""
    import database as db
    from utils.logger import log_acao
    
    # Verificar se já tem casas
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM casas WHERE vendido = 0")
    total = cur.fetchone()["total"]
    conn.close()
    
    if total >= 10:
        return 0
    
    agora = time.time()
    casas = [
        # São Paulo
        {"nome": "Apartamento Jardins", "tipo": "apartamento", "cidade": "São Paulo", "bairro": "Jardins", "preco": 450000, "garagem": 1},
        {"nome": "Casa Morumbi", "tipo": "casa", "cidade": "São Paulo", "bairro": "Morumbi", "preco": 800000, "garagem": 3},
        {"nome": "Studio Vila Madalena", "tipo": "studio", "cidade": "São Paulo", "bairro": "Vila Madalena", "preco": 280000, "garagem": 0},
        
        # Rio de Janeiro
        {"nome": "Cobertura Copacabana", "tipo": "cobertura", "cidade": "Rio de Janeiro", "bairro": "Copacabana", "preco": 650000, "garagem": 2},
        {"nome": "Casa Ipanema", "tipo": "casa", "cidade": "Rio de Janeiro", "bairro": "Ipanema", "preco": 1200000, "garagem": 2},
        
        # Belo Horizonte
        {"nome": "Apartamento Savassi", "tipo": "apartamento", "cidade": "Belo Horizonte", "bairro": "Savassi", "preco": 320000, "garagem": 1},
        {"nome": "Casa Lourdes", "tipo": "casa", "cidade": "Belo Horizonte", "bairro": "Lourdes", "preco": 550000, "garagem": 2},
        
        # Curitiba
        {"nome": "Apartamento Batel", "tipo": "apartamento", "cidade": "Curitiba", "bairro": "Batel", "preco": 380000, "garagem": 1},
        {"nome": "Casa Ecoville", "tipo": "casa", "cidade": "Curitiba", "bairro": "Ecoville", "preco": 700000, "garagem": 3},
        
        # Porto Alegre
        {"nome": "Apartamento Moinhos", "tipo": "apartamento", "cidade": "Porto Alegre", "bairro": "Moinhos de Vento", "preco": 420000, "garagem": 1},
        {"nome": "Casa Bela Vista", "tipo": "casa", "cidade": "Porto Alegre", "bairro": "Bela Vista", "preco": 680000, "garagem": 2},
    ]
    
    conn = db.conectar()
    cur = conn.cursor()
    
    for casa in casas:
        cur.execute("""
            INSERT INTO casas (nome, tipo, cidade, bairro, preco, cofre, decoracao, garagem, vendido, criado_em)
            VALUES (?, ?, ?, ?, ?, 0, 'basica', ?, 0, ?)
        """, (casa["nome"], casa["tipo"], casa["cidade"], casa["bairro"], casa["preco"], casa["garagem"], agora))
    
    conn.commit()
    conn.close()
    
    log_acao("CASAS_POPULADAS", f"total={len(casas)}")
    return len(casas)
