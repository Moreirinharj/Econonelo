"""Deterioração automática de status baseada no tempo."""
import time
import database as db
from data import balanceamento as bal
from services.clima_service import aplicar_modificadores_clima
from services.relacionamento_service import verificar_descoberta
from utils.logger import log_acao


def aplicar_deterioracao_global():
    """Aplica deterioração em todos os personagens ativos baseado no tempo passado."""
    personagens = db.listar_todos_personagens()
    agora = time.time()
    afetados = 0
    
    for p in personagens:
        ultimo_trabalho = p.get("ultimo_trabalho", p.get("criado_em", agora))
        horas_passadas = (agora - ultimo_trabalho) / 3600
        
        if horas_passadas < 1:
            continue  # Não deteriora se trabalhou há menos de 1h
        
        # Limita a 24h de deterioração (pra não matar o personagem)
        horas_passadas = min(horas_passadas, 24)
        
        # Aplica deterioração em cada status
        # Aplica deterioração base
        delta_fome_base = int(bal.DETERIORACAO_FOME * horas_passadas)
        delta_energia_base = int(bal.DETERIORACAO_ENERGIA * horas_passadas)
        delta_higiene = int(bal.DETERIORACAO_HIGIENE * horas_passadas)
        delta_felicidade = int(bal.DETERIORACAO_FELICIDADE * horas_passadas)
        
        # Aplica modificadores do clima
        delta_fome_final, delta_energia_final = aplicar_modificadores_clima(p["id"], delta_fome_base, delta_energia_base)
        
        for campo, delta in [("fome", delta_fome_final), ("energia", delta_energia_final), 
                             ("higiene", delta_higiene), ("felicidade", delta_felicidade)]:
            if delta != 0:
                db.modificar_status_personagem(p["id"], campo, delta)
        
        # Atualiza ultimo_trabalho pra não aplicar de novo
        conn = db.conectar()
        cur = conn.cursor()
        cur.execute("UPDATE personagens SET ultimo_trabalho = ? WHERE id = ?", (agora, p["id"]))
        conn.commit()
        conn.close()
        
        afetados += 1
        
        # Verifica se foi descoberto traindo (5% de chance por hora)
        if random.random() < 0.05:
            resultado = verificar_descoberta(p["id"])
            if resultado.get("descoberto"):
                log_acao("TRAICAO_DESCOBERTA_AUTOMATICA", f"personagem={p['id']}")
    
    if afetados > 0:
        log_acao("DETERIORACAO_GLOBAL", f"afetados={afetados}")
    
    return afetados
