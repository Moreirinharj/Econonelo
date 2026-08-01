"""Dados de especialidades, universidades e concursos com questões balanceadas."""

ESPECIALIDADES_PROFESSOR = {
    "direito": {"nome": "Direito", "materias": ["Direito Constitucional", "Direito Civil", "Direito Penal", "Direito Processual", "Direito Administrativo"], "descricao": "Professor de Direito em universidades"},
    "medicina": {"nome": "Medicina", "materias": ["Anatomia", "Fisiologia", "Patologia", "Clínica Médica", "Cirurgia"], "descricao": "Professor de Medicina em universidades"},
    "engenharia": {"nome": "Engenharia", "materias": ["Cálculo", "Física", "Mecânica", "Resistência dos Materiais", "Termodinâmica"], "descricao": "Professor de Engenharia em universidades"},
    "administracao": {"nome": "Administração", "materias": ["Gestão Empresarial", "Marketing", "Finanças", "Contabilidade", "Recursos Humanos"], "descricao": "Professor de Administração em universidades"},
    "psicologia": {"nome": "Psicologia", "materias": ["Psicologia Clínica", "Psicologia Social", "Neuropsicologia", "Psicanálise", "Psicologia do Desenvolvimento"], "descricao": "Professor de Psicologia em universidades"},
    "computacao": {"nome": "Ciência da Computação", "materias": ["Algoritmos", "Estrutura de Dados", "Banco de Dados", "Redes", "Inteligência Artificial"], "descricao": "Professor de Computação em universidades"},
    "matematica": {"nome": "Matemática", "materias": ["Cálculo", "Álgebra Linear", "Geometria", "Estatística", "Análise Real"], "descricao": "Professor de Matemática em universidades"},
    "historia": {"nome": "História", "materias": ["História do Brasil", "História Mundial", "História Antiga", "História Medieval", "Historiografia"], "descricao": "Professor de História em universidades"},
    "biologia": {"nome": "Biologia", "materias": ["Genética", "Ecologia", "Zoologia", "Botânica", "Microbiologia"], "descricao": "Professor de Biologia em universidades"},
    "economia": {"nome": "Economia", "materias": ["Microeconomia", "Macroeconomia", "Econometria", "História Econômica", "Economia Internacional"], "descricao": "Professor de Economia em universidades"},
    "jornalismo": {"nome": "Jornalismo", "materias": ["Redação Jornalística", "Teoria da Comunicação", "Jornalismo Investigativo", "Mídia Digital", "Ética Jornalística"], "descricao": "Professor de Jornalismo em universidades"},
    "arquitetura": {"nome": "Arquitetura", "materias": ["Projeto Arquitetônico", "História da Arte", "Urbanismo", "Design de Interiores", "Construção Civil"], "descricao": "Professor de Arquitetura em universidades"},
}

# ===== UNIVERSIDADES COM DESCRIÇÃO E CURSOS =====
MODELOS_CONCURSO = {
    "usp": {
        "universidade": "USP",
        "nome_completo": "Universidade de São Paulo",
        "descricao": "A maior e mais prestigiada universidade da América Latina, referência mundial em pesquisa, inovação e ensino de excelência.",
        "cursos_destaque": ["Medicina", "Direito", "Engenharia", "Ciência da Computação", "Administração"],
        "salario_base": 15000, "vagas_base": 3, "nivel": "superior"
    },
    "ufrj": {
        "universidade": "UFRJ",
        "nome_completo": "Universidade Federal do Rio de Janeiro",
        "descricao": "Tradição e excelência acadêmica no Rio de Janeiro, com forte atuação em ciências da saúde, humanas e tecnologia.",
        "cursos_destaque": ["Medicina", "Arquitetura", "Jornalismo", "Engenharia Civil", "Biologia"],
        "salario_base": 14000, "vagas_base": 2, "nivel": "superior"
    },
    "ufmg": {
        "universidade": "UFMG",
        "nome_completo": "Universidade Federal de Minas Gerais",
        "descricao": "Uma das principais universidades do país, reconhecida pela qualidade do ensino e pela forte produção científica em exatas e saúde.",
        "cursos_destaque": ["Engenharia Civil", "Economia", "Odontologia", "Medicina", "Direito"],
        "salario_base": 13500, "vagas_base": 2, "nivel": "superior"
    },
    "ufpr": {
        "universidade": "UFPR",
        "nome_completo": "Universidade Federal do Paraná",
        "descricao": "A universidade mais antiga do Brasil, polo de conhecimento no Sul do país com tradição em ciências agrárias, biológicas e humanas.",
        "cursos_destaque": ["Medicina Veterinária", "Biologia", "Direito", "Engenharia Florestal", "História"],
        "salario_base": 13000, "vagas_base": 2, "nivel": "superior"
    },
    "ufrgs": {
        "universidade": "UFRGS",
        "nome_completo": "Universidade Federal do Rio Grande do Sul",
        "descricao": "Excelência acadêmica no RS, com destaque nacional em pesquisa nas áreas de ciências exatas, saúde e engenharias.",
        "cursos_destaque": ["Física", "Química", "Engenharia", "Medicina", "Psicologia"],
        "salario_base": 13500, "vagas_base": 2, "nivel": "superior"
    },
    "ufba": {
        "universidade": "UFBA",
        "nome_completo": "Universidade Federal da Bahia",
        "descricao": "O maior polo cultural e acadêmico do Nordeste, com forte identidade regional e excelência em artes, saúde e ciências sociais.",
        "cursos_destaque": ["Artes Cênicas", "Serviço Social", "Medicina", "Jornalismo", "Direito"],
        "salario_base": 12500, "vagas_base": 2, "nivel": "superior"
    },
    "fgv": {
        "universidade": "FGV",
        "nome_completo": "Fundação Getulio Vargas",
        "descricao": "Instituição de elite focada em ciências sociais aplicadas, referência absoluta em negócios, economia e direito no Brasil.",
        "cursos_destaque": ["MBA Executivo", "Economia", "Direito", "Administração Pública"],
        "salario_base": 18000, "vagas_base": 1, "nivel": "pos"
    },
    "puc": {
        "universidade": "PUC",
        "nome_completo": "Pontifícia Universidade Católica",
        "descricao": "Tradição humanista e excelência acadêmica, com forte atuação em direito, saúde, engenharias e ciências sociais.",
        "cursos_destaque": ["Psicologia", "Direito", "Engenharia", "Medicina", "Jornalismo"],
        "salario_base": 16000, "vagas_base": 2, "nivel": "superior"
    },
}

# (Aqui continuam as QUESTOES_CONCURSO e QUESTOES_CONCURSO_PROFISSAO exatamente como estavam na v39)
# Para não ficar gigante, vou manter apenas a estrutura, mas no seu arquivo real, 
# cole as questões da v39 logo abaixo desta linha.

QUESTOES_CONCURSO = {
    "direito": [
        {"pergunta": "Qual é o princípio fundamental da Constituição Federal de 1988?", "opcoes": ["Soberania nacional", "Dignidade da pessoa humana", "Separação dos poderes", "Federalismo"], "correta": 1},
        {"pergunta": "O que é o princípio da legalidade?", "opcoes": ["A lei pode retroagir para beneficiar", "Ninguém é obrigado a fazer ou deixar de fazer algo senão em virtude de lei", "Todos são iguais perante a lei sem distinção", "O Estado é soberano em suas decisões"], "correta": 1},
        {"pergunta": "Qual a diferença entre direito público e privado?", "opcoes": ["Público regula relações do Estado, privado entre particulares", "Não há diferença prática entre eles", "Público é criminal, privado é civil", "Público é federal, privado é estadual"], "correta": 0},
        {"pergunta": "O que é habeas corpus?", "opcoes": ["Ação trabalhista", "Ação de divórcio", "Ação para proteger liberdade de locomoção", "Ação tributária"], "correta": 2},
        {"pergunta": "Quem pode propor ADI (Ação Direta de Inconstitucionalidade)?", "opcoes": ["Qualquer cidadão brasileiro", "Apenas o STF", "Presidente da República, partidos políticos, entre outros legitimados", "Apenas o Ministério Público"], "correta": 2},
    ],
    # ... (COLE O RESTANTE DAS QUESTOES_CONCURSO DA V39 AQUI) ...
}

CONCURSOS_PROFISSOES = {
    "policial_militar": {"nome": "Concurso PM", "orgao": "Polícia Militar", "salario_base": 5500, "vagas_base": 20, "requisito_escolaridade": "medio", "descricao": "Concurso pra entrar na Polícia Militar"},
    "policial_civil": {"nome": "Concurso PC", "orgao": "Polícia Civil", "salario_base": 7500, "vagas_base": 10, "requisito_escolaridade": "superior", "descricao": "Concurso pra entrar na Polícia Civil"},
    "samu": {"nome": "Concurso SAMU", "orgao": "SAMU", "salario_base": 4500, "vagas_base": 15, "requisito_escolaridade": "medio", "descricao": "Concurso pra trabalhar no SAMU"},
    "medico": {"nome": "Concurso Médico", "orgao": "SUS/Hospitais Públicos", "salario_base": 12000, "vagas_base": 5, "requisito_escolaridade": "superior", "descricao": "Concurso pra médico em hospitais públicos"},
    "juiz": {"nome": "Concurso Magistratura", "orgao": "Poder Judiciário", "salario_base": 25000, "vagas_base": 2, "requisito_escolaridade": "superior", "descricao": "Concurso pra juiz"},
}

QUESTOES_CONCURSO_PROFISSAO = {
    # ... (COLE O RESTANTE DAS QUESTOES_CONCURSO_PROFISSAO DA V39 AQUI) ...
    "policial_militar": [
        {"pergunta": "Qual o principal dever da Polícia Militar?", "opcoes": ["Investigar crimes complexos", "Policiamento ostensivo e preservação da ordem pública", "Julgar processos criminais", "Elaborar leis estaduais"], "correta": 1},
        {"pergunta": "O que é flagrante delito?", "opcoes": ["Crime cometido há mais de um ano", "Pessoa cometendo o crime ou logo após", "Tipo de multa de trânsito", "Documento oficial da polícia"], "correta": 1},
        {"pergunta": "Qual hierarquia imediatamente acima de Soldado na PM?", "opcoes": ["Cabo", "Sargento", "Tenente", "Capitão"], "correta": 0},
        {"pergunta": "O que é uso progressivo da força?", "opcoes": ["Usar força máxima sempre que necessário", "Aplicar força de forma gradativa conforme a resistência", "Nunca usar força física", "Só usar arma de fogo em qualquer situação"], "correta": 1},
        {"pergunta": "Qual o número de emergência da Polícia Militar?", "opcoes": ["192", "193", "190", "191"], "correta": 2},
    ],
    # ... (adicione as outras profissões aqui)
}

def gerar_concursos_disponiveis():
    import random
    import time
    concursos = []
    for cod_uni, dados_uni in MODELOS_CONCURSO.items():
        for esp in ESPECIALIDADES_PROFESSOR.keys():
            concurso_id = f"{cod_uni}_{esp}_{int(time.time())}"
            concursos.append({
                "id": concurso_id,
                "universidade": dados_uni["universidade"],
                "especialidade": esp,
                "vagas": dados_uni["vagas_base"] + random.randint(0, 2),
                "salario": dados_uni["salario_base"] + random.randint(-2000, 3000),
                "nivel": dados_uni["nivel"],
            })
    return concursos
