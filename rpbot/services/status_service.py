"""Lógica de deterioração e recuperação de status."""
import time
import database as db
from utils.logger import log_acao


# Taxas de deterioração por hora
TAXAS_DETERIORACAO = {
    "fome": -5,        # perde 5 de fome por hora
    "energia": -3,     # perde 3 de energia por hora
    "higiene": -2,     # perde 2 de higiene por hora
    "felicidade": -1,  # perde 1 de felicidade por hora
}


def aplicar_deterioracao(personagem_id: int, horas_passadas: float):
    """Aplica deterioração de status baseada no tempo passado."""
    personagem = db.obter_personagem_por_id(personagem_id)
    if personagem is None:
        return
    
    for campo, taxa in TAXAS_DETERIORACAO.items():
        delta = int(taxa * horas_passadas)
        if delta != 0:
            db.modificar_status_personagem(personagem_id, campo, delta)
    
    log_acao("DETERIORACAO_APLICADA", f"personagem_id={personagem_id} horas={horas_passadas:.2f}")


def comer(personagem_id: int, quantidade: int = 30) -> dict:
    """Personagem come e recupera fome."""
    nova_fome = db.modificar_status_personagem(personagem_id, "fome", quantidade)
    log_acao("PERSONAGEM_COMEU", f"personagem_id={personagem_id} fome={nova_fome}")
    return {"fome": nova_fome, "mensagem": f"Você comeu e recuperou {quantidade} de fome!"}


def dormir(personagem_id: int, horas: int = 8) -> dict:
    """Personagem dorme e recupera energia."""
    recuperacao = horas * 10
    nova_energia = db.modificar_status_personagem(personagem_id, "energia", recuperacao)
    nova_felicidade = db.modificar_status_personagem(personagem_id, "felicidade", 5)
    log_acao("PERSONAGEM_DORMIU", f"personagem_id={personagem_id} horas={horas}")
    return {
        "energia": nova_energia,
        "felicidade": nova_felicidade,
        "mensagem": f"Você dormiu {horas}h e recuperou {recuperacao} de energia!",
    }


def tomar_banho(personagem_id: int) -> dict:
    """Personagem toma banho e recupera higiene."""
    nova_higiene = db.modificar_status_personagem(personagem_id, "higiene", 50)
    nova_felicidade = db.modificar_status_personagem(personagem_id, "felicidade", 5)
    log_acao("PERSONAGEM_TOMOU_BANHO", f"personagem_id={personagem_id}")
    return {
        "higiene": nova_higiene,
        "felicidade": nova_felicidade,
        "mensagem": "Você tomou banho e está limpo!",
    }


def relaxar(personagem_id: int) -> dict:
    """Personagem relaxa e reduz estresse."""
    novo_estresse = db.modificar_status_personagem(personagem_id, "estresse", -20)
    nova_felicidade = db.modificar_status_personagem(personagem_id, "felicidade", 10)
    log_acao("PERSONAGEM_RELAXOU", f"personagem_id={personagem_id}")
    return {
        "estresse": novo_estresse,
        "felicidade": nova_felicidade,
        "mensagem": "Você relaxou e se sentiu melhor!",
    }


def verificar_status_criticos(personagem_id: int) -> list:
    """Verifica se algum status está crítico (< 20)."""
    personagem = db.obter_personagem_por_id(personagem_id)
    if personagem is None:
        return []
    
    criticos = []
    if personagem.get("saude", 100) < 20:
        criticos.append("saude")
    if personagem.get("energia", 100) < 20:
        criticos.append("energia")
    if personagem.get("fome", 100) < 20:
        criticos.append("fome")
    
    return criticos
