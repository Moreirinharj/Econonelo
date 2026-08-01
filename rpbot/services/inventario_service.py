"""Lógica de inventário e itens."""
import database as db
from utils.logger import log_acao

PESO_MAXIMO_BASE = 50.0

ITENS_PADRAO = {
    "agua": {"nome": "Garrafa de Água", "tipo": "bebida", "peso": 0.5},
    "comida": {"nome": "Marmita", "tipo": "comida", "peso": 1.0},
    "remedio": {"nome": "Remédio Básico", "tipo": "medicamento", "peso": 0.2},
    "celular": {"nome": "Celular", "tipo": "equipamento", "peso": 0.3},
    "documento": {"nome": "Documento", "tipo": "documento", "peso": 0.1},
    "chave": {"nome": "Chave", "tipo": "chave", "peso": 0.05},
}


def obter_peso_maximo(personagem_id: int) -> float:
    """Retorna peso máximo do personagem (pode ser expandido com mochilas)."""
    return PESO_MAXIMO_BASE


def pode_adicionar_item(personagem_id: int, peso_item: float, quantidade: int = 1) -> bool:
    """Verifica se há espaço no inventário."""
    peso_atual = db.calcular_peso_total(personagem_id)
    peso_max = obter_peso_maximo(personagem_id)
    return (peso_atual + peso_item * quantidade) <= peso_max


def dar_item(personagem_id: int, item_tipo: str, quantidade: int = 1) -> dict:
    """Dá um item padrão ao personagem."""
    if item_tipo not in ITENS_PADRAO:
        return {"sucesso": False, "mensagem": "Item inválido."}
    
    info = ITENS_PADRAO[item_tipo]
    
    if not pode_adicionar_item(personagem_id, info["peso"], quantidade):
        return {"sucesso": False, "mensagem": "Inventário cheio!"}
    
    db.adicionar_item(personagem_id, info["nome"], info["tipo"], quantidade, info["peso"])
    log_acao("ITEM_DADO", f"personagem_id={personagem_id} item={item_tipo} qtd={quantidade}")
    return {
        "sucesso": True,
        "mensagem": f"Você recebeu {quantidade}x {info['nome']}!",
        "item": info,
    }


def usar_item(personagem_id: int, item_id: int) -> dict:
    """Usa um item (consome se for comida/bebida/remédio)."""
    item = db.obter_item(personagem_id, item_id)
    if item is None:
        return {"sucesso": False, "mensagem": "Item não encontrado."}
    
    if item["item_tipo"] == "comida":
        db.modificar_status_personagem(personagem_id, "fome", 30)
        db.remover_item(personagem_id, item_id, 1)
        return {"sucesso": True, "mensagem": "Você comeu e recuperou fome!"}
    
    elif item["item_tipo"] == "bebida":
        db.modificar_status_personagem(personagem_id, "fome", 15)
        db.remover_item(personagem_id, item_id, 1)
        return {"sucesso": True, "mensagem": "Você bebeu e recuperou um pouco de fome!"}
    
    elif item["item_tipo"] == "medicamento":
        db.modificar_status_personagem(personagem_id, "saude", 20)
        db.remover_item(personagem_id, item_id, 1)
        return {"sucesso": True, "mensagem": "Você tomou remédio e recuperou saúde!"}
    
    else:
        return {"sucesso": False, "mensagem": "Esse item não pode ser usado assim."}
