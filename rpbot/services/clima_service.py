"""Lógica do sistema de clima e estações do ano."""
import random
import time
import database as db
from data.clima_data import ESTACOES, CLIMAS, EVENTOS_CLIMATICOS
from utils.logger import log_acao


def obter_clima_atual() -> dict:
    """Retorna o clima e estação atuais."""
    clima_nome = db.obter_estado_mundo("clima") or "Ensolarado"
    estacao = db.obter_estado_mundo("estacao") or "Primavera"
    temperatura = db.obter_estado_mundo("temperatura")
    
    if not temperatura:
        temperatura = str(CLIMAS.get(clima_nome, {}).get("temperatura", 25))
        db.atualizar_estado_mundo("temperatura", temperatura)
    
    dados_clima = CLIMAS.get(clima_nome, CLIMAS["Ensolarado"])
    dados_clima["nome"] = clima_nome
    dados_clima["estacao"] = estacao
    dados_clima["temperatura"] = int(temperatura)
    
    return dados_clima


def avancar_clima() -> dict:
    """Avança o clima. Pode mudar de estação ou gerar evento raro."""
    clima_atual = db.obter_estado_mundo("clima") or "Ensolarado"
    estacao_atual = db.obter_estado_mundo("estacao") or "Primavera"
    
    # 10% de chance de mudar de estação
    if random.random() < 0.10:
        estacoes = ESTACOES
        idx_atual = estacoes.index(estacao_atual)
        nova_estacao = estacoes[(idx_atual + 1) % len(estacoes)]
        db.atualizar_estado_mundo("estacao", nova_estacao)
        estacao_atual = nova_estacao
        log_acao("MUDANCA_ESTACAO", f"para {nova_estacao}")
    
    # 30% de chance de mudar o clima, ou 100% se for evento
    mudar_clima = random.random() < 0.30
    
    if mudar_clima:
        # Verifica se vai rolar evento climático raro (15% de chance)
        if random.random() < 0.15:
            evento = random.choice(EVENTOS_CLIMATICOS)
            novo_clima = evento["clima"]
            db.adicionar_noticia(evento["nome"], evento["mensagem"], "clima")
            log_acao("EVENTO_CLIMATICO", evento["nome"])
        else:
            # Clima normal baseado na estação
            if estacao_atual == "Verão":
                pesos = {"Ensolarado": 40, "Nublado": 20, "Chuvoso": 20, "Calor": 20}
            elif estacao_atual == "Inverno":
                pesos = {"Frio": 50, "Nublado": 20, "Chuvoso": 20, "Ensolarado": 10}
            else:
                pesos = {"Ensolarado": 30, "Nublado": 30, "Chuvoso": 30, "Frio": 10}
            
            novo_clima = random.choices(list(pesos.keys()), weights=list(pesos.values()))[0]
        
        db.atualizar_estado_mundo("clima", novo_clima)
        db.atualizar_estado_mundo("temperatura", str(CLIMAS[novo_clima]["temperatura"]))
        log_acao("MUDANCA_CLIMA", f"para {novo_clima}")
        
        return {"mudou": True, "novo_clima": novo_clima, "estacao": estacao_atual}
    
    return {"mudou": False, "clima_atual": clima_atual, "estacao": estacao_atual}


def aplicar_modificadores_clima(personagem_id: int, delta_fome: int, delta_energia: int) -> tuple:
    """Aplica modificadores de fome e energia baseados no clima."""
    clima = obter_clima_atual()
    
    fome_final = delta_fome + clima.get("mod_fome", 0)
    energia_final = delta_energia + clima.get("mod_energia", 0)
    
    return fome_final, energia_final


def obter_bonus_motoboy() -> float:
    """Retorna o multiplicador de salário para motoboys baseado no clima."""
    clima = obter_clima_atual()
    return clima.get("mod_motoboy", 1.0)


def forcar_clima(clima_nome: str) -> dict:
    """Admin força um clima específico."""
    if clima_nome not in CLIMAS:
        return {"sucesso": False, "msg": f"Clima inválido. Opções: {', '.join(CLIMAS.keys())}"}
    
    db.atualizar_estado_mundo("clima", clima_nome)
    db.atualizar_estado_mundo("temperatura", str(CLIMAS[clima_nome]["temperatura"]))
    
    return {
        "sucesso": True,
        "msg": f"⛈️ Clima alterado para **{clima_nome}** ({CLIMAS[clima_nome]['emoji']})!",
        "dados": CLIMAS[clima_nome]
    }
