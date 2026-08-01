"""Sistema de viagens e imersão por estado."""
import database as db
from utils.logger import log_acao

ESTADOS_DISPONIVEIS = {
    "SP": {"nome": "São Paulo", "aeroporto": "GRU", "custo_base": 300},
    "RJ": {"nome": "Rio de Janeiro", "aeroporto": "GIG", "custo_base": 350},
    "MG": {"nome": "Minas Gerais", "aeroporto": "CNF", "custo_base": 250},
    "PR": {"nome": "Paraná", "aeroporto": "CWB", "custo_base": 400},
    "RS": {"nome": "Rio Grande do Sul", "aeroporto": "POA", "custo_base": 450},
    "BA": {"nome": "Bahia", "aeroporto": "SSA", "custo_base": 500},
}

def obter_estados_disponiveis(estado_origem: str) -> list:
    """Retorna lista de estados para viajar (exceto o atual)."""
    destinos = []
    for uf, dados in ESTADOS_DISPONIVEIS.items():
        if uf != estado_origem:
            destinos.append({
                "uf": uf,
                "nome": dados["nome"],
                "aeroporto": dados["aeroporto"],
                "custo": dados["custo_base"]
            })
    return destinos

def viajar(personagem_id: int, estado_destino: str) -> dict:
    """Realiza a viagem, cobrando e mudando o estado."""
    estado_destino = estado_destino.upper()
    
    if estado_destino not in ESTADOS_DISPONIVEIS:
        return {"sucesso": False, "msg": "Estado inválido ou sem aeroporto comercial."}
    
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    estado_atual = personagem.get("estado_atual") or personagem.get("estado")
    if estado_atual == estado_destino:
        return {"sucesso": False, "msg": f"Você já está em {ESTADOS_DISPONIVEIS[estado_destino]['nome']}, mano!"}
    
    custo = ESTADOS_DISPONIVEIS[estado_destino]["custo_base"]
    
    if personagem["saldo"] < custo:
        return {
            "sucesso": False,
            "msg": f"💸 Grana curta! A passagem pra {ESTADOS_DISPONIVEIS[estado_destino]['nome']} custa ${custo}.",
            "helper": "💡 Usa `?trabalhar` pra fazer uma grana ou `?sacar` do banco."
        }
    
    # Desconta e muda o estado
    db.atualizar_saldo_personagem(personagem_id, -custo)
    
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET estado_atual = ? WHERE id = ?", (estado_destino, personagem_id))
    conn.commit()
    conn.close()
    
    db.registrar_transacao(personagem_id, "viagem", custo, f"Passagem aérea para {ESTADOS_DISPONIVEIS[estado_destino]['nome']}")
    
    nome_destino = ESTADOS_DISPONIVEIS[estado_destino]["nome"]
    log_acao("VIAGEM_REALIZADA", f"personagem={personagem_id} de={estado_atual} para={estado_destino}")
    
    return {
        "sucesso": True,
        "msg": f"✈️ **Voo confirmado!**\n\nVocê embarcou e agora está em **{nome_destino}** ({estado_destino}).\nBoa viagem, mano! Aproveita as oportunidades locais.",
        "novo_estado": estado_destino
    }

def voltar_para_casa(personagem_id: int) -> dict:
    """Volta para o estado de origem do personagem."""
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    estado_origem = personagem.get("estado")
    estado_atual = personagem.get("estado_atual") or estado_origem
    
    if estado_atual == estado_origem:
        return {"sucesso": False, "msg": "Você já tá na sua terra natal, mano!"}
    
    return viajar(personagem_id, estado_origem)
