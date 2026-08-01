import database as db
from utils.logger import log_acao

def criar_denuncia(reu_id: int, acusador_id: int, crime: str, descricao: str) -> dict:
    reu = db.obter_personagem_por_id(reu_id)
    if not reu:
        return {"sucesso": False, "msg": "Réu não encontrado."}
    
    # Fiança base calculada pela gravidade (simplificado: 500 a 5000)
    fianca = 1000
    
    pid = db.abrir_processo(reu_id, acusador_id, crime, descricao, fianca)
    return {"sucesso": True, "pid": pid, "fianca": fianca}

def calcular_fianca_restante(processo_id: int) -> int:
    p = db.obter_processo(processo_id)
    if not p:
        return 0
    return max(0, p["fianca_valor"] - p["fianca_paga"])
