"""Lógica de NPCs: criação, interação, comportamento."""
import random
import database as db
from utils.logger import log_acao

NOMES_MASCULINOS = [
    "João", "Pedro", "Carlos", "Lucas", "Marcos", "Rafael", "Bruno", "Diego",
    "Fernando", "Gabriel", "Henrique", "Igor", "Jorge", "Leonardo", "Matheus",
]

NOMES_FEMININOS = [
    "Maria", "Ana", "Juliana", "Camila", "Fernanda", "Patrícia", "Beatriz",
    "Carla", "Daniela", "Eduarda", "Gabriela", "Helena", "Isabela", "Larissa",
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa",
    "Rodrigues", "Almeida", "Nascimento", "Araújo", "Melo", "Barbosa",
]

PROFISSOES_NPC = [
    "comerciante", "motorista", "professor", "médico", "advogado",
    "engenheiro", "jornalista", "artista", "político", "agricultor",
]

CIDADES = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre", "Salvador"]

PERSONALIDADES = ["amigável", "sério", "nervoso", "alegre", "reservado", "tagarela"]


def gerar_nome_completo() -> str:
    primeiro = random.choice(NOMES_MASCULINOS + NOMES_FEMININOS)
    sobrenome = random.choice(SOBRENOMES)
    return f"{primeiro} {sobrenome}"


def criar_npc_aleatorio(cidade: str = None) -> int:
    """Cria um NPC aleatório."""
    nome = gerar_nome_completo()
    idade = random.randint(18, 70)
    profissao = random.choice(PROFISSOES_NPC)
    cidade_real = cidade or random.choice(CIDADES)
    dinheiro = random.randint(500, 5000)
    personalidade = random.choice(PERSONALIDADES)
    
    npc_id = db.criar_npc(nome, idade, profissao, cidade_real, dinheiro, personalidade)
    log_acao("NPC_ALEATORIO_CRIADO", f"id={npc_id} nome={nome}")
    return npc_id


def popular_cidade(cidade: str, quantidade: int = 20):
    """Popula uma cidade com NPCs."""
    ids = []
    for _ in range(quantidade):
        npc_id = criar_npc_aleatorio(cidade)
        ids.append(npc_id)
    log_acao("CIDADE_POPULADA", f"cidade={cidade} quantidade={quantidade}")
    return ids


def conversar_com_npc(npc_id: int) -> dict:
    """Simula conversa com NPC. Retorna resposta baseada no humor."""
    npc = db.obter_npc(npc_id)
    if npc is None:
        return {"sucesso": False, "mensagem": "NPC não encontrado."}
    
    humor = npc["humor"]
    personalidade = npc["personalidade"]
    
    if humor >= 70:
        respostas = [
            f"Olá! Como vai? Estou tendo um ótimo dia!",
            f"E aí! Tudo tranquilo por aqui.",
            f"Que bom te ver! Posso ajudar em algo?",
        ]
    elif humor >= 40:
        respostas = [
            f"Oi. Tudo bem, e você?",
            f"Olá. Em que posso ajudar?",
            f"E aí. Beleza?",
        ]
    else:
        respostas = [
            f"Hmm... oi.",
            f"Não estou num bom dia...",
            f"O que você quer?",
        ]
    
    resposta = random.choice(respostas)
    
    if personalidade == "tagarela":
        resposta += " Aliás, você sabia que..."
    elif personalidade == "reservado":
        resposta += " (olha pro lado)"
    
    return {"sucesso": True, "resposta": resposta, "npc": npc}


def dar_dinheiro_para_npc(npc_id: int, valor: int) -> dict:
    """Dá dinheiro pra um NPC (melhora humor)."""
    npc = db.obter_npc(npc_id)
    if npc is None:
        return {"sucesso": False, "mensagem": "NPC não encontrado."}
    
    db.modificar_dinheiro_npc(npc_id, valor)
    melhoria_humor = min(20, valor // 10)
    novo_humor = db.modificar_humor_npc(npc_id, melhoria_humor)
    
    log_acao("NPC_DINHEIRO_DADO", f"npc_id={npc_id} valor={valor} humor={novo_humor}")
    return {
        "sucesso": True,
        "mensagem": f"Você deu ${valor} para {npc['nome']}. Humor: {novo_humor}/100",
        "novo_humor": novo_humor,
    }


def popular_npcs() -> int:
    """Popula o mundo com NPCs importantes (professores, médicos, policiais, etc.)."""
    import database as db
    from utils.logger import log_acao
    
    # Verificar se já tem NPCs
    npcs_existentes = db.listar_npcs()
    if len(npcs_existentes) >= 20:
        log_acao("NPCS_JA_POPULADOS", f"total={len(npcs_existentes)}")
        return 0
    
    # Limpar NPCs antigos
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM npcs")
    conn.commit()
    conn.close()
    
    agora = time.time()
    npcs = [
        # Professores universitários
        {"nome": "Dr. Carlos Silva", "idade": 45, "profissao": "professor", "cidade": "São Paulo", "especialidade": "Matemática", "dinheiro": 8000},
        {"nome": "Dra. Ana Souza", "idade": 50, "profissao": "professor", "cidade": "Rio de Janeiro", "especialidade": "Física", "dinheiro": 9000},
        {"nome": "Dr. Roberto Lima", "idade": 42, "profissao": "professor", "cidade": "Belo Horizonte", "especialidade": "Química", "dinheiro": 7500},
        {"nome": "Dra. Mariana Costa", "idade": 38, "profissao": "professor", "cidade": "Curitiba", "especialidade": "Biologia", "dinheiro": 7000},
        {"nome": "Dr. Paulo Santos", "idade": 55, "profissao": "professor", "cidade": "Porto Alegre", "especialidade": "História", "dinheiro": 8500},
        
        # Médicos
        {"nome": "Dr. João Pereira", "idade": 48, "profissao": "medico", "cidade": "São Paulo", "especialidade": "Cardiologia", "dinheiro": 15000},
        {"nome": "Dra. Fernanda Alves", "idade": 40, "profissao": "medico", "cidade": "Rio de Janeiro", "especialidade": "Pediatria", "dinheiro": 14000},
        {"nome": "Dr. Marcos Oliveira", "idade": 52, "profissao": "medico", "cidade": "Belo Horizonte", "especialidade": "Ortopedia", "dinheiro": 16000},
        
        # Policiais
        {"nome": "Cap. Ricardo Mendes", "idade": 45, "profissao": "policial_militar", "cidade": "São Paulo", "dinheiro": 6000},
        {"nome": "Det. Bruno Ferreira", "idade": 38, "profissao": "policial_civil", "cidade": "Rio de Janeiro", "dinheiro": 7000},
        {"nome": "Sgt. Lucas Gomes", "idade": 42, "profissao": "policial_militar", "cidade": "Curitiba", "dinheiro": 5500},
        
        # Advogados
        {"nome": "Dr. Eduardo Rocha", "idade": 47, "profissao": "advogado", "cidade": "São Paulo", "especialidade": "Direito Penal", "dinheiro": 20000},
        {"nome": "Dra. Camila Nunes", "idade": 39, "profissao": "advogado", "cidade": "Rio de Janeiro", "especialidade": "Direito Civil", "dinheiro": 18000},
        
        # Juízes
        {"nome": "Dr. Antônio Barbosa", "idade": 58, "profissao": "juiz", "cidade": "São Paulo", "dinheiro": 30000},
        {"nome": "Dra. Beatriz Moreira", "idade": 52, "profissao": "juiz", "cidade": "Rio de Janeiro", "dinheiro": 28000},
        
        # SAMU
        {"nome": "Enf. Pedro Henrique", "idade": 35, "profissao": "samu", "cidade": "São Paulo", "dinheiro": 4500},
        {"nome": "Enf. Juliana Castro", "idade": 32, "profissao": "samu", "cidade": "Belo Horizonte", "dinheiro": 4200},
        
        # Empresários
        {"nome": "Ricardo Almeida", "idade": 50, "profissao": "empresario", "cidade": "São Paulo", "dinheiro": 100000},
        {"nome": "Patrícia Duarte", "idade": 45, "profissao": "empresario", "cidade": "Rio de Janeiro", "dinheiro": 85000},
        
        # Jogadores de futebol
        {"nome": "Neymar Jr.", "idade": 28, "profissao": "jogador_futebol", "cidade": "Rio de Janeiro", "dinheiro": 500000},
        {"nome": "Gabriel Barbosa", "idade": 26, "profissao": "jogador_futebol", "cidade": "Rio de Janeiro", "dinheiro": 300000},
    ]
    
    conn = db.conectar()
    cur = conn.cursor()
    
    for npc in npcs:
        especialidade = npc.get("especialidade", "NULL")
        if especialidade != "NULL":
            especialidade = f"'{especialidade}'"
        
        cur.execute(f"""
            INSERT INTO npcs (nome, idade, profissao, cidade, dinheiro, especialidade, ativo, criado_em)
            VALUES (?, ?, ?, ?, ?, {especialidade}, 1, ?)
        """, (npc["nome"], npc["idade"], npc["profissao"], npc["cidade"], npc["dinheiro"], agora))
    
    conn.commit()
    conn.close()
    
    log_acao("NPCS_POPULADOS", f"total={len(npcs)}")
    return len(npcs)
