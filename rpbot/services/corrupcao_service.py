"""Lógica de corrupção: subornos, propinas, denúncias."""
import random
import database as db
from utils.logger import log_acao


def tentar_subornar(subornador_id: int, subornado_id: int, valor: int, tipo: str = "propina") -> dict:
    subornador = db.obter_personagem_por_id(subornador_id)
    subornado = db.obter_personagem_por_id(subornado_id)
    
    if not subornador or not subornado:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    if subornador["saldo"] < valor:
        return {"sucesso": False, "msg": "Saldo insuficiente pra subornar, mano."}
    
    cid = db.registrar_tentativa_suborno(subornador_id, subornado_id, valor, tipo)
    
    db.atualizar_saldo_personagem(subornador_id, -valor)
    db.registrar_transacao(subornador_id, "suborno_enviado", valor, f"Tentativa de suborno para {subornado['nome']}")
    
    if random.random() < 0.10:
        db.prender_personagem(subornador_id)
        db.adicionar_registro_criminal(subornador_id, "Tentativa de suborno em flagrante")
        return {
            "sucesso": False,
            "msg": "🚔 Você foi pego tentando subornar! Preso em flagrante!",
            "preso": True,
            "corrupcao_id": cid,
        }
    
    return {
        "sucesso": True,
        "msg": f"💰 Você ofereceu ${valor} pra {subornado['nome']}. Agora espera a resposta...",
        "preso": False,
        "corrupcao_id": cid,
    }


def processar_decisao_suborno(corrupcao_id: int, aceitar: bool) -> dict:
    tentativa = db.obter_tentativa_suborno(corrupcao_id)
    if not tentativa:
        return {"sucesso": False, "msg": "Tentativa não encontrada."}
    
    if tentativa["aceito"] or tentativa["denunciado"]:
        return {"sucesso": False, "msg": "Essa tentativa já foi resolvida."}
    
    subornador = db.obter_personagem_por_id(tentativa["subornador_id"])
    subornado = db.obter_personagem_por_id(tentativa["subornado_id"])
    valor = tentativa["valor"]
    
    if aceitar:
        db.aceitar_suborno(corrupcao_id)
        db.atualizar_saldo_personagem(tentativa["subornado_id"], valor)
        db.registrar_transacao(tentativa["subornado_id"], "suborno_recebido", valor, f"Suborno de {subornador['nome']}")
        db.atualizar_reputacao_corrupta(tentativa["subornador_id"], 10)
        db.atualizar_reputacao_corrupta(tentativa["subornado_id"], 15)
        db.modificar_status_personagem(tentativa["subornado_id"], "reputacao", -10)
        
        return {
            "sucesso": True,
            "aceito": True,
            "msg": f"💰 {subornado['nome']} aceitou o suborno de ${valor}! Ambos ganharam reputação corrupta.",
        }
    else:
        db.denunciar_suborno(corrupcao_id)
        db.atualizar_saldo_personagem(tentativa["subornador_id"], valor)
        db.registrar_transacao(tentativa["subornador_id"], "suborno_devolvido", valor, f"Suborno recusado por {subornado['nome']}")
        db.adicionar_registro_criminal(tentativa["subornador_id"], f"Tentativa de subornar {subornado['nome']}")
        db.modificar_status_personagem(tentativa["subornador_id"], "reputacao", -15)
        
        return {
            "sucesso": True,
            "aceito": False,
            "msg": f"🚫 {subornado['nome']} recusou o suborno e te denunciou! Tua reputação caiu.",
        }


def denunciar_corrupcao(denunciante_id: int, acusado_id: int) -> dict:
    """✅ CORREÇÃO: Denuncia TODOS os subornos aceitos, não só o primeiro."""
    subornos = db.listar_subornos_envolvidos(acusado_id)
    
    subornos_aceitos = [s for s in subornos if s["subornado_id"] == acusado_id and s["aceito"] and not s["denunciado"]]
    
    if not subornos_aceitos:
        return {"sucesso": False, "msg": "Não há provas de corrupção contra essa pessoa."}
    
    # Denuncia TODOS os subornos aceitos
    for suborno in subornos_aceitos:
        db.denunciar_suborno(suborno["id"])
    
    # Acusado perde reputação proporcional ao número de subornos
    perda_reputacao = 20 * len(subornos_aceitos)
    db.modificar_status_personagem(acusado_id, "reputacao", -perda_reputacao)
    db.adicionar_registro_criminal(acusado_id, f"Denunciado por {len(subornos_aceitos)} casos de corrupção")
    
    # Chance de ser preso aumenta com o número de subornos
    chance_preso = min(0.90, 0.50 + (len(subornos_aceitos) * 0.10))
    
    if random.random() < chance_preso:
        db.prender_personagem(acusado_id)
        return {
            "sucesso": True,
            "msg": f"🚔 Denúncia aceita! O acusado foi preso por {len(subornos_aceitos)} casos de corrupção!",
            "preso": True,
            "total_subornos": len(subornos_aceitos),
        }
    else:
        return {
            "sucesso": True,
            "msg": f"📋 Denúncia registrada. {len(subornos_aceitos)} caso(s) de corrupção sendo investigado(s).",
            "preso": False,
            "total_subornos": len(subornos_aceitos),
        }


def historico_corrupcao(personagem_id: int) -> list:
    return db.listar_subornos_envolvidos(personagem_id)
