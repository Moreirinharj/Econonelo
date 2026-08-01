"""Sistema de herança e testamento."""
import json
import time
import database as db
from utils.logger import log_acao

IMPOSTO_HERANCA = 0.10  # 10% de imposto sobre herança


def criar_testamento(personagem_id: int, herdeiros: dict) -> dict:
    """
    Cria ou atualiza testamento.
    herdeiros: dict {personagem_id: porcentagem} — soma deve ser 100
    """
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    if not personagem.get("vivo", 1):
        return {"sucesso": False, "msg": "Personagem morto não pode fazer testamento."}
    
    # Valida herdeiros
    if not herdeiros:
        return {"sucesso": False, "msg": "Testamento precisa ter pelo menos um herdeiro."}
    
    total_porcentagem = sum(herdeiros.values())
    if total_porcentagem != 100:
        return {
            "sucesso": False,
            "msg": f"Soma das porcentagens deve ser 100%. Atual: {total_porcentagem}%"
        }
    
    # Valida se herdeiros existem e estão vivos
    for herdeiro_id in herdeiros.keys():
        herdeiro = db.obter_personagem_por_id(herdeiro_id)
        if not herdeiro:
            return {"sucesso": False, "msg": f"Herdeiro ID {herdeiro_id} não encontrado."}
        if not herdeiro.get("vivo", 1):
            return {"sucesso": False, "msg": f"Herdeiro {herdeiro['nome']} está morto."}
        if herdeiro_id == personagem_id:
            return {"sucesso": False, "msg": "Você não pode deixar herança pra si mesmo! 😂"}
    
    # Salva testamento
    conn = db.conectar()
    cur = conn.cursor()
    agora = time.time()
    cur.execute("""
        INSERT INTO testamentos (personagem_id, herdeiros, criado_em, atualizado_em)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(personagem_id) DO UPDATE SET
            herdeiros = excluded.herdeiros,
            atualizado_em = excluded.atualizado_em
    """, (personagem_id, json.dumps(herdeiros), agora, agora))
    conn.commit()
    conn.close()
    
    log_acao("TESTAMENTO_CRIADO", f"personagem={personagem_id} herdeiros={len(herdeiros)}")
    
    return {
        "sucesso": True,
        "msg": f"📜 **Testamento registrado!**\n\nSeus bens serão distribuídos conforme tua vontade quando partir.\n\n💡 Usa `?verherdeiros` pra ver quem vai receber o quê."
    }


def ver_testamento(personagem_id: int) -> dict:
    """Mostra o testamento do personagem."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("SELECT herdeiros FROM testamentos WHERE personagem_id = ?", (personagem_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return {"sucesso": False, "msg": "Você não tem testamento registrado.\n\n💡 Usa `?testamento` pra criar um."}
    
    herdeiros = json.loads(row["herdeiros"])
    linhas = []
    for herdeiro_id, porcentagem in herdeiros.items():
        herdeiro = db.obter_personagem_por_id(herdeiro_id)
        nome = herdeiro["nome"] if herdeiro else f"ID {herdeiro_id}"
        linhas.append(f"• **{nome}** — {porcentagem}%")
    
    return {
        "sucesso": True,
        "msg": "📜 **Teu Testamento:**\n\n" + "\n".join(linhas)
    }


def cancelar_testamento(personagem_id: int) -> dict:
    """Cancela o testamento."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM testamentos WHERE personagem_id = ?", (personagem_id,))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    
    if sucesso:
        return {"sucesso": True, "msg": "🗑️ Testamento cancelado. Herança seguirá ordem legal."}
    return {"sucesso": False, "msg": "Você não tem testamento pra cancelar."}


def obter_herdeiros_legais(personagem_id: int) -> list:
    """
    Retorna herdeiros em ordem legal (sem testamento):
    Cônjuge > Filhos > Pais > Irmãos
    """
    relacionamentos = db.listar_familia(personagem_id)
    
    conjuge = None
    filhos = []
    pais = []
    irmaos = []
    
    for r in relacionamentos:
        alvo = db.obter_personagem_por_id(r["alvo_id"])
        if not alvo or not alvo.get("vivo", 1):
            continue
        
        tipo = r["tipo"]
        if tipo == "conjuge":
            conjuge = alvo
        elif tipo in ["filho", "filha"]:
            filhos.append(alvo)
        elif tipo in ["pai", "mae"]:
            pais.append(alvo)
        elif tipo in ["irmao", "irma"]:
            irmaos.append(alvo)
    
    # Monta lista de herdeiros com porcentagem
    herdeiros = []
    if conjuge:
        herdeiros.append({"personagem": conjuge, "porcentagem": 50})
        restante = 50
        if filhos:
            por_filho = restante // len(filhos)
            for f in filhos:
                herdeiros.append({"personagem": f, "porcentagem": por_filho})
        elif pais:
            por_pai = restante // len(pais)
            for p in pais:
                herdeiros.append({"personagem": p, "porcentagem": por_pai})
        elif irmaos:
            por_irmao = restante // len(irmaos)
            for i in irmaos:
                herdeiros.append({"personagem": i, "porcentagem": por_irmao})
    elif filhos:
        por_filho = 100 // len(filhos)
        for f in filhos:
            herdeiros.append({"personagem": f, "porcentagem": por_filho})
    elif pais:
        por_pai = 100 // len(pais)
        for p in pais:
            herdeiros.append({"personagem": p, "porcentagem": por_pai})
    elif irmaos:
        por_irmao = 100 // len(irmaos)
        for i in irmaos:
            herdeiros.append({"personagem": i, "porcentagem": por_irmao})
    
    return herdeiros


def processar_heranca(falecido_id: int) -> dict:
    """Processa herança quando personagem morre."""
    falecido = db.obter_personagem_por_id(falecido_id)
    if not falecido:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    # Calcula bens totais
    bens = {
        "saldo_banco": falecido.get("saldo_banco", 0),
        "cofres": 0,
        "casas": [],
        "veiculos": [],
    }
    
    # Soma cofres das casas
    casas = db.listar_casas_do_proprietario(falecido_id)
    for casa in casas:
        bens["cofres"] += casa.get("cofre", 0)
        bens["casas"].append(casa["id"])
    
    # Lista veículos
    veiculos = db.listar_veiculos_do_proprietario(falecido_id)
    bens["veiculos"] = [v["id"] for v in veiculos]
    
    # Valor total em dinheiro
    valor_total = bens["saldo_banco"] + bens["cofres"]
    
    # Determina herdeiros
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("SELECT herdeiros FROM testamentos WHERE personagem_id = ?", (falecido_id,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        # Usa testamento
        herdeiros_dict = json.loads(row["herdeiros"])
        herdeiros = []
        for herdeiro_id, porcentagem in herdeiros_dict.items():
            herdeiro = db.obter_personagem_por_id(herdeiro_id)
            if herdeiro and herdeiro.get("vivo", 1):
                herdeiros.append({"personagem": herdeiro, "porcentagem": porcentagem})
    else:
        # Usa ordem legal
        herdeiros = obter_herdeiros_legais(falecido_id)
    
    if not herdeiros:
        # Sem herdeiros — bens vão pro governo (perdidos)
        log_acao("HERANCA_SEM_HERDEIROS", f"falecido={falecido_id}")
        return {
            "sucesso": True,
            "msg": f"💀 **{falecido['nome']}** morreu sem herdeiros. Seus bens foram confiscados pelo governo.",
            "herdeiros": []
        }
    
    # Cria heranças pendentes
    herancas_criadas = []
    for h in herdeiros:
        herdeiro = h["personagem"]
        porcentagem = h["porcentagem"]
        
        valor_heranca = int(valor_total * porcentagem / 100)
        imposto = int(valor_heranca * IMPOSTO_HERANCA)
        valor_liquido = valor_heranca - imposto
        
        # Distribui casas e veículos proporcionalmente
        casas_herdeiro = []
        veiculos_herdeiro = []
        
        if porcentagem >= 50 and bens["casas"]:
            casas_herdeiro.append(bens["casas"][0])
        
        if porcentagem >= 50 and bens["veiculos"]:
            veiculos_herdeiro.append(bens["veiculos"][0])
        
        bens_dict = {
            "dinheiro": valor_liquido,
            "imposto": imposto,
            "casas": casas_herdeiro,
            "veiculos": veiculos_herdeiro,
        }
        
        conn = db.conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO herancas_pendentes (falecido_id, herdeiro_id, bens, valor_total, criado_em)
            VALUES (?, ?, ?, ?, ?)
        """, (falecido_id, herdeiro["id"], json.dumps(bens_dict), valor_liquido, time.time()))
        conn.commit()
        conn.close()
        
        herancas_criadas.append({
            "herdeiro": herdeiro,
            "valor": valor_liquido,
            "imposto": imposto,
            "casas": len(casas_herdeiro),
            "veiculos": len(veiculos_herdeiro),
        })
    
    log_acao("HERANCA_PROCESSADA", f"falecido={falecido_id} herdeiros={len(herancas_criadas)}")
    
    return {
        "sucesso": True,
        "msg": f"💀 **{falecido['nome']}** faleceu. {len(herancas_criadas)} herdeiro(s) foram notificados.",
        "herdeiros": herancas_criadas
    }


def listar_herancas_pendentes(herdeiro_id: int) -> list:
    """Lista heranças pendentes pra um herdeiro."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT h.*, p.nome as falecido_nome
        FROM herancas_pendentes h
        JOIN personagens p ON h.falecido_id = p.id
        WHERE h.herdeiro_id = ? AND h.status = 'pendente'
        ORDER BY h.criado_em DESC
    """, (herdeiro_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def receber_heranca(herdeiro_id: int, heranca_id: int) -> dict:
    """Herdeiro recebe herança pendente."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM herancas_pendentes 
        WHERE id = ? AND herdeiro_id = ? AND status = 'pendente'
    """, (heranca_id, herdeiro_id))
    heranca = cur.fetchone()
    conn.close()
    
    if not heranca:
        return {"sucesso": False, "msg": "Herança não encontrada ou já foi recebida."}
    
    bens = json.loads(heranca["bens"])
    
    # Transfere dinheiro
    db.modificar_saldo_banco(herdeiro_id, bens["dinheiro"])
    db.registrar_transacao(herdeiro_id, "heranca", bens["dinheiro"], 
                          f"Herança de ID {heranca['falecido_id']}")
    
    # Transfere casas
    for casa_id in bens.get("casas", []):
        conn = db.conectar()
        cur = conn.cursor()
        cur.execute("UPDATE casas SET proprietario_id = ? WHERE id = ?", (herdeiro_id, casa_id))
        conn.commit()
        conn.close()
    
    # Transfere veículos
    for veiculo_id in bens.get("veiculos", []):
        conn = db.conectar()
        cur = conn.cursor()
        cur.execute("UPDATE veiculos SET proprietario_id = ? WHERE id = ?", (herdeiro_id, veiculo_id))
        conn.commit()
        conn.close()
    
    # Marca como recebida
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE herancas_pendentes SET status = 'recebida' WHERE id = ?", (heranca_id,))
    conn.commit()
    conn.close()
    
    log_acao("HERANCA_RECEBIDA", f"heranca={heranca_id} herdeiro={herdeiro_id} valor={bens['dinheiro']}")
    
    return {
        "sucesso": True,
        "msg": f"💰 **Herança recebida!**\n\n"
               f"**Dinheiro:** +${bens['dinheiro']} (no banco)\n"
               f"**Imposto pago:** ${bens['imposto']}\n"
               f"**Casas:** {len(bens.get('casas', []))}\n"
               f"**Veículos:** {len(bens.get('veiculos', []))}\n\n"
               f"💡 Usa `?carteira` pra ver teu saldo atualizado."
    }
