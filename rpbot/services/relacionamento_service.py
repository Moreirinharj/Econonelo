"""Sistema de relacionamentos secretos e traição."""
import random
import database as db
from utils.logger import log_acao


def adicionar_amante(personagem_id: int, amante_id: int) -> dict:
    """Adiciona um amante ao personagem."""
    personagem = db.obter_personagem_por_id(personagem_id)
    amante = db.obter_personagem_por_id(amante_id)
    
    if not personagem or not amante:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    if personagem_id == amante_id:
        return {"sucesso": False, "msg": "Você não pode ser seu próprio amante, mano! 😂"}
    
    # Verifica se já tem amante
    if personagem.get("amante_id"):
        return {"sucesso": False, "msg": "Você já tem um amante. Usa `?terminaramante` primeiro."}
    
    # Define como amante
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET amante_id = ? WHERE id = ?", (amante_id, personagem_id))
    conn.commit()
    conn.close()
    
    db.modificar_status_personagem(personagem_id, "felicidade", 10)
    db.modificar_status_personagem(personagem_id, "traindo", 1)
    
    log_acao("AMANTE_ADICIONADO", f"personagem={personagem_id} amante={amante_id}")
    
    return {
        "sucesso": True,
        "msg": f"💕 Você agora tem um relacionamento secreto com **{amante['nome']}**!\n\n⚠️ Cuidado: existe chance de ser descoberto!"
    }


def terminar_amante(personagem_id: int) -> dict:
    """Termina o relacionamento com o amante."""
    personagem = db.obter_personagem_por_id(personagem_id)
    
    if not personagem:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    if not personagem.get("amante_id"):
        return {"sucesso": False, "msg": "Você não tem nenhum amante pra terminar."}
    
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET amante_id = NULL, traindo = 0 WHERE id = ?", (personagem_id,))
    conn.commit()
    conn.close()
    
    db.modificar_status_personagem(personagem_id, "felicidade", -5)
    
    return {"sucesso": True, "msg": "💔 Você terminou com seu amante. Vida que segue..."}


def verificar_descoberta(personagem_id: int) -> dict:
    """Verifica se o personagem foi descoberto traindo."""
    personagem = db.obter_personagem_por_id(personagem_id)
    
    if not personagem or not personagem.get("amante_id"):
        return {"descoberto": False}
    
    # Chance de descoberta baseada em:
    # - Reputação baixa = mais chance
    # - Estresse alto = mais chance
    # - Higiene baixa = mais chance
    
    chance = 0.05  # 5% base
    
    # Reputação baixa aumenta chance
    reputacao = personagem.get("reputacao", 50)
    if reputacao < 30:
        chance += 0.10
    
    # Estresse alto aumenta chance
    estresse = personagem.get("estresse", 0)
    if estresse > 70:
        chance += 0.05
    
    # Higiene baixa aumenta chance
    higiene = personagem.get("higiene", 100)
    if higiene < 30:
        chance += 0.05
    
    if random.random() < chance:
        # Foi descoberto!
        conn = db.conectar()
        cur = conn.cursor()
        cur.execute("UPDATE personagens SET traindo = 0, amante_id = NULL WHERE id = ?", (personagem_id,))
        conn.commit()
        conn.close()
        
        # Consequências
        db.modificar_status_personagem(personagem_id, "felicidade", -30)
        db.modificar_status_personagem(personagem_id, "estresse", 20)
        db.modificar_status_personagem(personagem_id, "reputacao", -15)
        
        amante = db.obter_personagem_por_id(personagem.get("amante_id"))
        nome_amante = amante["nome"] if amante else "alguém"
        
        log_acao("TRAICAO_DESCOBERTA", f"personagem={personagem_id} amante={personagem.get('amante_id')}")
        
        return {
            "descoberto": True,
            "msg": f"🚨 **VOCÊ FOI DESCOBERTO!**\n\nSeu relacionamento secreto com **{nome_amante}** foi exposto!\n\n💔 -30 felicidade\n😰 +20 estresse\n⭐ -15 reputação\n\nO relacionamento foi encerrado automaticamente."
        }
    
    return {"descoberto": False}


def ver_amante(personagem_id: int) -> dict:
    """Mostra informações sobre o amante."""
    personagem = db.obter_personagem_por_id(personagem_id)
    
    if not personagem:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    if not personagem.get("amante_id"):
        return {"sucesso": False, "msg": "Você não tem nenhum amante no momento."}
    
    amante = db.obter_personagem_por_id(personagem["amante_id"])
    
    if not amante:
        return {"sucesso": False, "msg": "Amante não encontrado."}
    
    return {
        "sucesso": True,
        "amante": amante,
        "msg": f"💕 Seu amante é: **{amante['nome']}**\n**Profissão:** {amante.get('profissao', 'Desempregado')}\n**Nível:** {amante.get('nivel', 1)}"
    }
