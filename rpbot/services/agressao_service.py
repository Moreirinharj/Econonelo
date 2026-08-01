"""Sistema de agressão, combate e ferimentos."""
import random
import time
import database as db
from data.agressao_data import TIPOS_AGRESSAO, MENSAGENS_ACERTO, MENSAGENS_ERRO, MENSAGENS_MORTE
from utils.logger import log_acao

COOLDOWN_AGRESSAO = 60  # 1 minuto entre agressões


def verificar_cooldown(personagem_id: int) -> dict:
    """Verifica se o personagem pode agredir."""
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return {"pode": False, "msg": "Personagem não encontrado."}
    
    if not personagem.get("vivo", 1):
        return {"pode": False, "msg": "Você está morto, mano. Não pode agredir ninguém."}
    
    if personagem.get("preso"):
        return {"pode": False, "msg": "Você tá preso. Não pode agredir ninguém daqui."}
    
    ultimo = personagem.get("ultima_agressao", 0)
    if time.time() - ultimo < COOLDOWN_AGRESSAO:
        resto = int(COOLDOWN_AGRESSAO - (time.time() - ultimo))
        return {"pode": False, "msg": f"⏳ Espera mais {resto}s antes de agredir de novo."}
    
    if personagem.get("energia", 100) < 20:
        return {"pode": False, "msg": "⚡ Energia muito baixa pra agredir alguém. Descansa primeiro."}
    
    return {"pode": True}


def verificar_arma(personagem_id: int, tipo_agressao: str) -> dict:
    """Verifica se tem a arma necessária."""
    tipo = TIPOS_AGRESSAO.get(tipo_agressao)
    if not tipo:
        return {"tem": False, "msg": "Tipo de agressão inválido."}
    
    if "requer_item" not in tipo:
        return {"tem": True}
    
    inventario = db.listar_inventario(personagem_id)
    nome_arma = tipo["requer_item"]
    
    for item in inventario:
        if item["item_nome"] == nome_arma:
            return {"tem": True, "item": item}
    
    return {
        "tem": False,
        "msg": f"Você precisa de **{nome_arma}** no inventário pra usar esse tipo de agressão.\n\n💡 Usa `?loja` pra encontrar onde comprar."
    }


def aplicar_agressao(atacante_id: int, alvo_id: int, tipo_agressao: str, legítima_defesa: bool = False) -> dict:
    """Aplica uma agressão de um personagem em outro."""
    # Verificações
    cooldown = verificar_cooldown(atacante_id)
    if not cooldown["pode"]:
        return {"sucesso": False, "msg": cooldown["msg"]}
    
    arma = verificar_arma(atacante_id, tipo_agressao)
    if not arma["tem"]:
        return {"sucesso": False, "msg": arma["msg"]}
    
    atacante = db.obter_personagem_por_id(atacante_id)
    alvo = db.obter_personagem_por_id(alvo_id)
    
    if not atacante or not alvo:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    if atacante_id == alvo_id:
        return {"sucesso": False, "msg": "🤡 Você não pode se agredir, mano! Tá doido?"}
    
    if not alvo.get("vivo", 1):
        return {"sucesso": False, "msg": "Essa pessoa já tá morta. Deixa ela em paz."}
    
    tipo = TIPOS_AGRESSAO[tipo_agressao]
    
    # Calcula chance de acerto (modificada por energia e nível)
    chance_acerto = tipo["chance_acerto"]
    chance_acerto += (atacante.get("nivel", 1) - 1) * 0.02  # +2% por nível
    chance_acerto += (atacante.get("energia", 100) - 50) / 500  # +/- 10% baseado em energia
    chance_acerto = max(0.20, min(0.95, chance_acerto))
    
    # Alvo pode desviar (chance baseada em energia e nível)
    chance_defesa = 0.10 + (alvo.get("energia", 100) - 50) / 500 + (alvo.get("nivel", 1) - 1) * 0.02
    chance_defesa = max(0.05, min(0.50, chance_defesa))
    
    # Legítima defesa dá bônus pro alvo
    if legítima_defesa:
        chance_defesa += 0.30
    
    # Rolagem de acerto
    acertou = random.random() < chance_acerto and random.random() > chance_defesa
    
    # Atualiza cooldown
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET ultima_agressao = ? WHERE id = ?", (time.time(), atacante_id))
    conn.commit()
    conn.close()
    
    # Consome energia do atacante
    db.modificar_status_personagem(atacante_id, "energia", -10)
    db.modificar_status_personagem(atacante_id, "estresse", 5)
    
    if not acertou:
        msg = random.choice(MENSAGENS_ERRO).format(
            atacante=atacante["nome"], alvo=alvo["nome"]
        )
        log_acao("AGRESSAO_ERROU", f"atacante={atacante_id} alvo={alvo_id} tipo={tipo_agressao}")
        
        return {
            "sucesso": True,
            "acertou": False,
            "msg": f"{msg}\n\n💨 {alvo['nome']} desviou do teu ataque!",
            "tipo": tipo,
        }
    
    # Acertou! Calcula dano
    dano = random.randint(tipo["dano_min"], tipo["dano_max"])
    
    # Bônus de arma equipada
    if arma.get("item"):
        dano += 5
    
    # Aplica ferimento no alvo
    ferimento_atual = alvo.get("ferido", 0)
    novo_ferimento = min(100, ferimento_atual + dano)
    
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET ferido = ? WHERE id = ?", (novo_ferimento, alvo_id))
    conn.commit()
    conn.close()
    
    # Reduz saúde baseado no ferimento
    db.modificar_status_personagem(alvo_id, "saude", -dano // 2)
    db.modificar_status_personagem(alvo_id, "estresse", 10)
    
    msg_acerto = random.choice(MENSAGENS_ACERTO).format(
        atacante=atacante["nome"], alvo=alvo["nome"]
    )
    
    # Verifica se morreu
    morreu = False
    if random.random() < tipo["chance_morte"] or novo_ferimento >= 100:
        morreu = True
        msg_morte = random.choice(MENSAGENS_MORTE).format(
            atacante=atacante["nome"], alvo=alvo["nome"]
        )
        
        # Mata o alvo
        from services.cpf_service import matar_personagem
        causa = f"Assassinato por {atacante['nome']} ({tipo['nome']})"
        matar_personagem(alvo_id, causa)
        
        # Atacante é processado por homicídio
        from services.justica_service import criar_denuncia
        # O assassino (atacante) é o réu, a vítima (alvo) é quem denuncia
        criar_denuncia(atacante_id, alvo_id, "Homicídio", f"{atacante['nome']} matou {alvo['nome']} com {tipo['nome']}")
        
        log_acao("AGRESSAO_LETAL", f"atacante={atacante_id} alvo={alvo_id} tipo={tipo_agressao}")
        
        return {
            "sucesso": True,
            "acertou": True,
            "matou": True,
            "dano": dano,
            "ferimento": novo_ferimento,
            "msg": f"{msg_acerto}\n\n{msg_morte}\n\n**Dano:** {dano}\n**Crime:** {tipo['crime']}\n\n🚔 Um processo foi aberto contra você automaticamente.",
            "tipo": tipo,
        }
    
    # Não morreu, mas gerou B.O. automático
    from database.oab import salvar_boletim
    salvar_boletim(
        alvo_id,
        f"Fui agredido(a) por {atacante['nome']} com {tipo['nome']}",
        f"Vítima relata agressão física perpetrada por {atacante['nome']} mediante uso de {tipo['nome'].lower()}. Lesões constatadas."
    )
    
    # Chance de flagrante
    if random.random() < tipo["chance_flagrante"]:
        # Policial NPC "aparece" e prende o atacante
        db.prender_personagem(atacante_id)
        db.adicionar_registro_criminal(atacante_id, f"Preso em flagrante: {tipo['crime']}")
        
        log_acao("AGRESSAO_FLAGRANTE", f"atacante={atacante_id} alvo={alvo_id}")
        
        return {
            "sucesso": True,
            "acertou": True,
            "matou": False,
            "preso": True,
            "dano": dano,
            "ferimento": novo_ferimento,
            "msg": f"{msg_acerto}\n\n**Dano:** {dano}\n**Ferimento do alvo:** {novo_ferimento}/100\n\n🚔 **PRESO EM FLAGRANTE!** Uma viatura chegou e te prendeu!\n**Crime:** {tipo['crime']}",
            "tipo": tipo,
        }
    
    log_acao("AGRESSAO_ACERTOU", f"atacante={atacante_id} alvo={alvo_id} dano={dano}")
    
    return {
        "sucesso": True,
        "acertou": True,
        "matou": False,
        "preso": False,
        "dano": dano,
        "ferimento": novo_ferimento,
        "msg": f"{msg_acerto}\n\n**Dano:** {dano}\n**Ferimento do alvo:** {novo_ferimento}/100\n\n📝 Um B.O. foi registrado automaticamente contra você.\n**Crime:** {tipo['crime']}",
        "tipo": tipo,
    }


def defender_de_agressao(defensor_id: int, agressor_id: int) -> dict:
    """Alvo se defende de uma agressão."""
    defensor = db.obter_personagem_por_id(defensor_id)
    agressor = db.obter_personagem_por_id(agressor_id)
    
    if not defensor or not agressor:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    # Chance de defesa bem-sucedida
    chance = 0.40 + (defensor.get("energia", 100) - 50) / 500 + (defensor.get("nivel", 1) - 1) * 0.03
    chance = max(0.20, min(0.80, chance))
    
    if random.random() < chance:
        # Defesa bem-sucedida — contra-ataque
        dano_contra = random.randint(5, 15)
        db.modificar_status_personagem(agressor_id, "saude", -dano_contra)
        db.modificar_status_personagem(agressor_id, "ferido", dano_contra)
        
        msg = random.choice(MENSAGENS_DEFESA).format(
            defensor=defensor["nome"], agressor=agressor["nome"]
        )
        
        return {
            "sucesso": True,
            "defendeu": True,
            "msg": f"{msg}\n\n💥 Contra-ataque! Causou {dano_contra} de dano em {agressor['nome']}!"
        }
    else:
        return {
            "sucesso": True,
            "defendeu": False,
            "msg": f"❌ {defensor['nome']} tentou se defender mas não conseguiu!"
        }


def curar_ferimento(medico_id: int, paciente_id: int) -> dict:
    """Médico cura ferimento de alguém."""
    medico = db.obter_personagem_por_id(medico_id)
    paciente = db.obter_personagem_por_id(paciente_id)
    
    if not medico or not paciente:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    if medico.get("profissao") not in ["medico", "samu"]:
        return {"sucesso": False, "msg": "Apenas médicos e SAMU podem curar ferimentos."}
    
    if medico.get("energia", 100) < 15:
        return {"sucesso": False, "msg": "⚡ Energia insuficiente pra atender o paciente."}
    
    ferimento = paciente.get("ferido", 0)
    if ferimento == 0:
        return {"sucesso": False, "msg": "Esse paciente não tá ferido."}
    
    # Cura parcial (30-60% do ferimento)
    cura = int(ferimento * random.uniform(0.30, 0.60))
    novo_ferimento = max(0, ferimento - cura)
    
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET ferido = ? WHERE id = ?", (novo_ferimento, paciente_id))
    conn.commit()
    conn.close()
    
    db.modificar_status_personagem(paciente_id, "saude", cura // 2)
    db.modificar_status_personagem(medico_id, "energia", -15)
    db.modificar_status_personagem(medico_id, "reputacao", 2)
    
    # Médico ganha dinheiro
    pagamento = 200 + cura * 5
    db.atualizar_saldo_personagem(medico_id, pagamento)
    db.registrar_transacao(medico_id, "servico_medico", pagamento, f"Tratamento de {paciente['nome']}")
    
    return {
        "sucesso": True,
        "cura": cura,
        "novo_ferimento": novo_ferimento,
        "pagamento": pagamento,
        "msg": f"🏥 **Paciente tratado!**\n\n**Ferimento:** {ferimento} → {novo_ferimento}\n**Cura:** {cura} pontos\n**Pagamento:** ${pagamento}\n\n💡 Usa `?curar <id>` pra tratar mais pacientes."
    }


def ver_ferimento(personagem_id: int) -> dict:
    """Mostra o nível de ferimento."""
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    ferimento = personagem.get("ferido", 0)
    
    if ferimento == 0:
        status = "✅ Sem ferimentos"
        cor = "verde"
    elif ferimento < 30:
        status = "🟡 Ferimento leve"
        cor = "amarelo"
    elif ferimento < 60:
        status = "🟠 Ferimento moderado"
        cor = "laranja"
    elif ferimento < 90:
        status = "🔴 Ferimento grave"
        cor = "vermelho"
    else:
        status = "💀 À beira da morte"
        cor = "preto"
    
    return {
        "sucesso": True,
        "ferimento": ferimento,
        "status": status,
        "cor": cor,
        "msg": f"**Ferimento:** {ferimento}/100\n**Status:** {status}"
    }
