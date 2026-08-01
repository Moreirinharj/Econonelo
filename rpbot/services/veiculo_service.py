"""Lógica de veículos: compra, venda, manutenção, acidentes."""
import database as db
from utils.logger import log_acao

PRECO_LITRO = 6
CUSTO_REPARO_BASE = 500
CUSTO_SEGURO_MENSAL = 200

MODELOS_DISPONIVEIS = {
    "popular": {"nome": "Carro Popular", "valor": 35000},
    "sedan": {"nome": "Sedan Médio", "valor": 60000},
    "suv": {"nome": "SUV", "valor": 90000},
    "esportivo": {"nome": "Carro Esportivo", "valor": 150000},
    "moto": {"nome": "Motocicleta", "valor": 15000},
}


def comprar_veiculo_service(personagem_id: int, veiculo_id: int) -> dict:
    veiculo = db.obter_veiculo(veiculo_id=veiculo_id)
    if not veiculo:
        return {"sucesso": False, "mensagem": "Veículo não encontrado."}
    if veiculo["vendido"]:
        return {"sucesso": False, "mensagem": "Este veículo já foi vendido."}
    
    personagem = db.obter_personagem_por_id(personagem_id)
    saldo_total = personagem["saldo"] + db.obter_saldo_banco(personagem_id)
    
    if saldo_total < veiculo["valor"]:
        return {"sucesso": False, "mensagem": f"Saldo insuficiente. Você tem ${saldo_total}, o veículo custa ${veiculo['valor']}."}
    
    # Deduz do bolso primeiro, depois do banco
    valor_restante = veiculo["valor"]
    if personagem["saldo"] >= valor_restante:
        db.atualizar_saldo_personagem(personagem_id, -valor_restante)
    else:
        db.atualizar_saldo_personagem(personagem_id, -personagem["saldo"])
        valor_restante -= personagem["saldo"]
        db.modificar_saldo_banco(personagem_id, -valor_restante)
    
    db.comprar_veiculo(veiculo_id, personagem_id)
    db.registrar_transacao(personagem_id, "compra_veiculo", veiculo["valor"], f"Compra de {veiculo['modelo']} ({veiculo['placa']})")
    
    return {"sucesso": True, "mensagem": f"Você comprou o {veiculo['modelo']} ({veiculo['placa']}) por ${veiculo['valor']}!"}


def vender_veiculo_service(personagem_id: int, veiculo_id: int) -> dict:
    veiculo = db.obter_veiculo(veiculo_id=veiculo_id)
    if not veiculo:
        return {"sucesso": False, "mensagem": "Veículo não encontrado."}
    if veiculo["proprietario_id"] != personagem_id:
        return {"sucesso": False, "mensagem": "Este veículo não é seu."}
    
    # Depreciação de 20%
    valor_venda = int(veiculo["valor"] * 0.8)
    db.atualizar_saldo_personagem(personagem_id, valor_venda)
    db.vender_veiculo(veiculo_id)
    db.registrar_transacao(personagem_id, "venda_veiculo", valor_venda, f"Venda de {veiculo['modelo']} ({veiculo['placa']})")
    
    return {"sucesso": True, "mensagem": f"Você vendeu o {veiculo['modelo']} por ${valor_venda}."}


def abastecer_service(personagem_id: int, placa: str, litros: int) -> dict:
    veiculo = db.obter_veiculo(placa=placa)
    if not veiculo or veiculo["proprietario_id"] != personagem_id:
        return {"sucesso": False, "mensagem": "Veículo não encontrado ou não é seu."}
    
    if veiculo["combustivel"] >= 100:
        return {"sucesso": False, "mensagem": "O tanque já está cheio."}
    
    litros_reais = min(litros, 100 - veiculo["combustivel"])
    custo = int(litros_reais * PRECO_LITRO)
    
    personagem = db.obter_personagem_por_id(personagem_id)
    if personagem["saldo"] < custo:
        return {"sucesso": False, "mensagem": f"Dinheiro insuficiente no bolso. Custo: ${custo}."}
    
    db.atualizar_saldo_personagem(personagem_id, -custo)
    novo_combustivel = db.abastecer_veiculo(veiculo["id"], litros_reais)
    
    return {"sucesso": True, "mensagem": f"Abastecido {litros_reais}L por ${custo}. Tanque: {novo_combustivel}%"}


def reparar_service(personagem_id: int, placa: str) -> dict:
    veiculo = db.obter_veiculo(placa=placa)
    if not veiculo or veiculo["proprietario_id"] != personagem_id:
        return {"sucesso": False, "mensagem": "Veículo não encontrado ou não é seu."}
    
    if veiculo["saude"] >= 100:
        return {"sucesso": False, "mensagem": "O veículo já está em perfeito estado."}
    
    dano = 100 - veiculo["saude"]
    custo = int(dano * CUSTO_REPARO_BASE)
    
    personagem = db.obter_personagem_por_id(personagem_id)
    if personagem["saldo"] < custo:
        return {"sucesso": False, "mensagem": f"Dinheiro insuficiente no bolso. Custo do reparo: ${custo}."}
    
    db.atualizar_saldo_personagem(personagem_id, -custo)
    db.reparar_veiculo(veiculo["id"])
    
    return {"sucesso": True, "mensagem": f"Veículo reparado por ${custo}. Saúde: 100%"}


def toggle_seguro_service(personagem_id: int, placa: str) -> dict:
    veiculo = db.obter_veiculo(placa=placa)
    if not veiculo or veiculo["proprietario_id"] != personagem_id:
        return {"sucesso": False, "mensagem": "Veículo não encontrado ou não é seu."}
    
    novo_status = db.toggle_seguro(veiculo["id"])
    status_texto = "ativado" if novo_status == 1 else "cancelado"
    
    return {"sucesso": True, "mensagem": f"Seguro do veículo {placa} foi {status_texto}."}


def simular_acidente_service(personagem_id: int, placa: str, severidade: int) -> dict:
    veiculo = db.obter_veiculo(placa=placa)
    if not veiculo or veiculo["proprietario_id"] != personagem_id:
        return {"sucesso": False, "mensagem": "Veículo não encontrado ou não é seu."}
    
    resultado = db.aplicar_acidente(veiculo["id"], severidade)
    
    msg = f"Acidente causado! Dano: {resultado['dano']}%. Saúde atual: {resultado['nova_saude']}%."
    if resultado["coberto_seguro"]:
        msg += " \n✅ O seguro cobriu os danos da oficina!"
        # Se tiver seguro, repara automaticamente (simplificação)
        db.reparar_veiculo(veiculo["id"])
        msg += " (Veículo reparado pelo seguro)"
    else:
        msg += " \n❌ Você não tem seguro. Leve à oficina para reparar."
        
    return {"sucesso": True, "mensagem": msg}


def popular_veiculos() -> int:
    """Popula o mundo com veículos disponíveis pra compra."""
    import database as db
    import random
    from utils.logger import log_acao
    
    # Verificar se já tem veículos
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM veiculos WHERE vendido = 0")
    total = cur.fetchone()["total"]
    conn.close()
    
    if total >= 10:
        return 0
    
    agora = time.time()
    veiculos = [
        {"modelo": "Honda Civic 2023", "valor": 150000},
        {"modelo": "Toyota Corolla 2023", "valor": 145000},
        {"modelo": "Volkswagen Polo 2022", "valor": 85000},
        {"modelo": "Chevrolet Onix 2023", "valor": 75000},
        {"modelo": "Fiat Argo 2022", "valor": 70000},
        {"modelo": "Hyundai HB20 2023", "valor": 80000},
        {"modelo": "BMW 320i 2023", "valor": 280000},
        {"modelo": "Mercedes C180 2023", "valor": 320000},
        {"modelo": "Honda CB 500 2023", "valor": 35000},
        {"modelo": "Yamaha MT-03 2023", "valor": 28000},
    ]
    
    conn = db.conectar()
    cur = conn.cursor()
    
    for veic in veiculos:
        # Gerar placa aleatória
        placa = f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(0,9)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}-{random.randint(1000,9999)}"
        
        cur.execute("""
            INSERT INTO veiculos (modelo, placa, combustivel, saude, seguro_ativo, documentacao, valor, vendido, criado_em)
            VALUES (?, ?, 100, 100, 0, 'regular', ?, 0, ?)
        """, (veic["modelo"], placa, veic["valor"], agora))
    
    conn.commit()
    conn.close()
    
    log_acao("VEICULOS_POPULADOS", f"total={len(veiculos)}")
    return len(veiculos)
