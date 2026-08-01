"""Lógica de concursos públicos para professores."""
import random
import database as db
from data.professor_data import ESPECIALIDADES_PROFESSOR, MODELOS_CONCURSO, QUESTOES_CONCURSO
from utils.logger import log_acao


def abrir_concursos_aleatorios(quantidade: int = 5) -> int:
    """Abre concursos aleatórios."""
    from data.professor_data import gerar_concursos_disponiveis
    
    # Fecha concursos antigos
    concursos_antigos = db.listar_concursos_abertos()
    for c in concursos_antigos:
        db.abrir_concurso  # só pra ter a referência
    
    modelos = gerar_concursos_disponiveis()
    random.shuffle(modelos)
    
    count = 0
    for modelo in modelos[:quantidade]:
        esp = modelo["especialidade"]
        materias = ESPECIALIDADES_PROFESSOR[esp]["materias"]
        if db.abrir_concurso(
            concurso_id=modelo["id"],
            universidade=modelo["universidade"],
            especialidade=esp,
            vagas=modelo["vagas"],
            salario=modelo["salario"],
            materias=materias,
            nivel="superior",
            duracao_horas=48,
        ):
            count += 1
    
    log_acao("CONCURSOS_GERADOS", f"total={count}")
    return count


def escolher_especialidade_professor(personagem_id: int, especialidade: str) -> dict:
    """Escolhe especialidade pra um professor."""
    if especialidade not in ESPECIALIDADES_PROFESSOR:
        return {"sucesso": False, "msg": f"Especialidade inválida. Opções: {', '.join(ESPECIALIDADES_PROFESSOR.keys())}"}
    
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    if personagem.get("profissao") != "professor":
        return {"sucesso": False, "msg": "Você precisa ser professor primeiro. Usa `?escolherprofissao professor`."}
    
    # Verifica escolaridade mínima
    escolaridade = personagem.get("escolaridade", "nenhuma")
    if escolaridade not in ["superior", "pos"]:
        return {
            "sucesso": False,
            "msg": f"Você precisa ter ensino superior ou pós pra ser professor. Sua escolaridade atual: {escolaridade}.",
            "helper": "💡 Usa `?universidades` pra ver cursos e `?estudar` pra se formar."
        }
    
    # Atualiza especialidade
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET especialidade_professor = ? WHERE id = ?", (especialidade, personagem_id))
    conn.commit()
    conn.close()
    
    nome_esp = ESPECIALIDADES_PROFESSOR[especialidade]["nome"]
    log_acao("ESPECIALIDADE_ESCOLHIDA", f"personagem={personagem_id} especialidade={especialidade}")
    
    return {
        "sucesso": True,
        "msg": f"✅ Você agora é professor de **{nome_esp}**!\n\n💡 Próximo passo: fazer um concurso público. Usa `?concursos` pra ver os disponíveis."
    }


def gerar_prova_concurso(especialidade: str, num_questoes: int = 5) -> dict:
    """Gera uma prova de concurso."""
    if especialidade not in QUESTOES_CONCURSO:
        return {"sucesso": False, "msg": "Sem questões pra essa especialidade."}
    
    todas = QUESTOES_CONCURSO[especialidade].copy()
    random.shuffle(todas)
    questoes = todas[:num_questoes]
    
    return {
        "sucesso": True,
        "questoes": questoes,
        "total": len(questoes),
    }


def avaliar_prova(respostas: list, questoes: list) -> dict:
    """Avalia uma prova e retorna nota."""
    acertos = 0
    total = len(questoes)
    
    for i, questao in enumerate(questoes):
        if i < len(respostas) and respostas[i] == questao["correta"]:
            acertos += 1
    
    nota = round((acertos / total) * 10, 1)
    aprovado = nota >= 7.0
    
    return {
        "acertos": acertos,
        "total": total,
        "nota": nota,
        "aprovado": aprovado,
    }


def processar_aprovacao(personagem_id: int, concurso_id: str, nota: float) -> dict:
    """Processa aprovação em concurso."""
    concurso = db.obter_concurso(concurso_id)
    if not concurso:
        return {"sucesso": False, "msg": "Concurso não encontrado."}
    
    aprovado = nota >= 7.0
    
    # Verifica se ainda tem vaga
    participacoes = db.listar_participacoes_personagem(personagem_id)
    aprovados_mesmo_concurso = [p for p in participacoes if p["concurso_id"] == concurso_id and p["aprovado"]]
    
    posicao = len(aprovados_mesmo_concurso) + 1 if aprovado else None
    dentro_vagas = aprovado and posicao <= concurso["vagas"]
    
    # Registra participação
    db.registrar_participacao(concurso_id, personagem_id, nota, dentro_vagas, posicao)
    
    if dentro_vagas:
        # Define cargo
        esp_nome = ESPECIALIDADES_PROFESSOR[concurso["especialidade"]]["nome"]
        cargo = f"Professor de {esp_nome} - {concurso['universidade']}"
        db.definir_cargo_professor(personagem_id, cargo, concurso["salario"], concurso_id)
        
        # Atualiza especialidade se não tiver
        personagem = db.obter_personagem_por_id(personagem_id)
        if not personagem.get("especialidade_professor"):
            conn = db.conectar()
            cur = conn.cursor()
            cur.execute("UPDATE personagens SET especialidade_professor = ? WHERE id = ?", (concurso["especialidade"], personagem_id))
            conn.commit()
            conn.close()
        
        return {
            "sucesso": True,
            "aprovado": True,
            "posicao": posicao,
            "cargo": cargo,
            "salario": concurso["salario"],
            "msg": f"🎉 APROVADO! Você ficou em {posicao}º lugar e agora é **{cargo}**!\n💰 Salário: ${concurso['salario']}/mês",
        }
    elif aprovado:
        return {
            "sucesso": True,
            "aprovado": False,
            "posicao": posicao,
            "msg": f"😕 Você passou na prova (nota {nota}/10) mas ficou em {posicao}º lugar e não tem vaga suficiente.\n💡 Tenta outro concurso!",
        }
    else:
        return {
            "sucesso": True,
            "aprovado": False,
            "msg": f"❌ REPROVADO! Nota {nota}/10 (mínimo 7.0).\n💡 Estuda mais e tenta de novo em outro concurso!",
        }


def simular_concurso_npc(npc_id: int) -> dict:
    """Simula um NPC professor fazendo concurso."""
    npc = db.obter_npc(npc_id)
    if not npc or npc["profissao"] != "professor":
        return {"sucesso": False, "msg": "NPC não é professor."}
    
    especialidade = npc.get("especialidade") or random.choice(list(ESPECIALIDADES_PROFESSOR.keys()))
    
    # Nota baseada em "inteligência" do NPC (aleatória)
    nota = round(random.uniform(5.0, 10.0), 1)
    aprovado = nota >= 7.0
    
    if aprovado:
        concursos = db.listar_concursos_abertos(especialidade=especialidade)
        if concursos:
            concurso = random.choice(concursos)
            cargo = f"Professor de {ESPECIALIDADES_PROFESSOR[especialidade]['nome']} - {concurso['universidade']}"
            
            # Atualiza NPC
            conn = db.conectar()
            cur = conn.cursor()
            cur.execute("UPDATE npcs SET concurso_aprovado = ? WHERE id = ?", (cargo, npc_id))
            conn.commit()
            conn.close()
            
            return {
                "sucesso": True,
                "npc": npc,
                "aprovado": True,
                "cargo": cargo,
                "nota": nota,
            }
    
    return {
        "sucesso": True,
        "npc": npc,
        "aprovado": False,
        "nota": nota,
    }


def popular_concursos() -> int:
    """Popula o mundo com concursos públicos abertos."""
    import database as db
    import time
    from utils.logger import log_acao
    
    # Verificar se já tem concursos
    concursos = db.listar_concursos_abertos()
    if len(concursos) >= 5:
        return 0
    
    agora = time.time()
    concursos = [
        {
            "id": "pm_sp_2026",
            "universidade": "Polícia Militar SP",
            "especialidade": "Policial Militar",
            "vagas": 50,
            "salario": 4500,
            "materias": "Português,Matemática,Direito,Ed. Física",
            "nivel": "medio",
        },
        {
            "id": "pc_rj_2026",
            "universidade": "Polícia Civil RJ",
            "especialidade": "Detetive",
            "vagas": 30,
            "salario": 8000,
            "materias": "Português,Direito Penal,Investigação,Criminologia",
            "nivel": "superior",
        },
        {
            "id": "juiz_sp_2026",
            "universidade": "TJSP",
            "especialidade": "Juiz",
            "vagas": 10,
            "salario": 30000,
            "materias": "Direito Civil,Direito Penal,Constitucional,Processual",
            "nivel": "superior",
        },
        {
            "id": "medico_samu_2026",
            "universidade": "SAMU Nacional",
            "especialidade": "Médico Emergencista",
            "vagas": 20,
            "salario": 12000,
            "materias": "Clínica Geral,Emergência,Trauma,Pediatria",
            "nivel": "superior",
        },
        {
            "id": "prof_usp_2026",
            "universidade": "USP",
            "especialidade": "Professor Universitário",
            "vagas": 15,
            "salario": 15000,
            "materias": "Didática,Especificidade da Área,Português,Legislação",
            "nivel": "superior",
        },
    ]
    
    conn = db.conectar()
    cur = conn.cursor()
    
    for conc in concursos:
        cur.execute("""
            INSERT OR IGNORE INTO concursos (id, universidade, especialidade, vagas, salario, materias, nivel, inscricao_aberta, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (conc["id"], conc["universidade"], conc["especialidade"], conc["vagas"], conc["salario"], conc["materias"], conc["nivel"], agora))
    
    conn.commit()
    conn.close()
    
    log_acao("CONCURSOS_POPULADOS", f"total={len(concursos)}")
    return len(concursos)


def popular_concursos() -> int:
    """Popula o mundo com concursos públicos abertos."""
    import database as db
    import json
    import time
    from utils.logger import log_acao
    
    # Verificar se já tem concursos
    try:
        concursos = db.listar_concursos_abertos()
        if len(concursos) >= 5:
            return 0
    except:
        pass
    
    agora = time.time()
    concursos = [
        {
            "id": "pm_sp_2026",
            "universidade": "Polícia Militar SP",
            "especialidade": "Policial Militar",
            "vagas": 50,
            "salario": 4500,
            "materias": ["Português", "Matemática", "Direito", "Ed. Física"],
            "nivel": "medio",
        },
        {
            "id": "pc_rj_2026",
            "universidade": "Polícia Civil RJ",
            "especialidade": "Detetive",
            "vagas": 30,
            "salario": 8000,
            "materias": ["Português", "Direito Penal", "Investigação", "Criminologia"],
            "nivel": "superior",
        },
        {
            "id": "juiz_sp_2026",
            "universidade": "TJSP",
            "especialidade": "Juiz",
            "vagas": 10,
            "salario": 30000,
            "materias": ["Direito Civil", "Direito Penal", "Constitucional", "Processual"],
            "nivel": "superior",
        },
        {
            "id": "medico_samu_2026",
            "universidade": "SAMU Nacional",
            "especialidade": "Médico Emergencista",
            "vagas": 20,
            "salario": 12000,
            "materias": ["Clínica Geral", "Emergência", "Trauma", "Pediatria"],
            "nivel": "superior",
        },
        {
            "id": "prof_usp_2026",
            "universidade": "USP",
            "especialidade": "Professor Universitário",
            "vagas": 15,
            "salario": 15000,
            "materias": ["Didática", "Especificidade da Área", "Português", "Legislação"],
            "nivel": "superior",
        },
    ]
    
    conn = db.conectar()
    cur = conn.cursor()
    
    for conc in concursos:
        # Converter lista pra JSON string
        materias_json = json.dumps(conc["materias"])
        
        cur.execute("""
            INSERT OR IGNORE INTO concursos 
            (id, universidade, especialidade, vagas, salario, materias, nivel, inscricao_aberta, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (conc["id"], conc["universidade"], conc["especialidade"], 
              conc["vagas"], conc["salario"], materias_json, conc["nivel"], agora))
    
    conn.commit()
    conn.close()
    
    log_acao("CONCURSOS_POPULADOS", f"total={len(concursos)}")
    return len(concursos)
