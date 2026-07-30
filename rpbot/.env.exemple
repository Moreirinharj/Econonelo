# ==========================================================
# CONFIGURAÇÕES GERAIS
# ==========================================================
PREFIXO = "?"
MAX_PERSONAGENS = 3  # limite de personagens por usuário do Discord

SALDO_INICIAL = 500  # em reais (r)

COOLDOWN_TRABALHO = 60 * 30  # 30 minutos
TIMEOUT_CONFIRMACAO = 300  # 5 minutos pra aceitar/recusar pedidos de família

CANAL_EVENTOS_ID = None  # defina o ID do canal pra eventos automáticos
INTERVALO_EVENTOS = 60 * 20
CHANCE_EVENTO = 0.35

# ==========================================================
# CRIAÇÃO DE PERSONAGEM
# ==========================================================
IDADE_MINIMA = 18
IDADE_MAXIMA = 98

CORES_PELE = ["Branco", "Preto", "Pardo", "Amarelo"]
TIPOS_CABELO = ["Cacheado", "Ondulado", "Liso"]
CORES_CABELO = ["Preto", "Loiro", "Castanho", "Vermelho", "Platinado"]
IDADE_CABELO_BRANCO = 60  # a partir dessa idade, cabelo fica "X Esbranquiçado"

RELIGIOES = [
    "Católico", "Evangélico", "Ateu", "Umbandista",
    "Candomblecista", "Agnóstico", "Budista", "Judeu",
]

REGIOES = {
    "Norte": ["Acre", "Amapá", "Amazonas", "Pará", "Rondônia", "Roraima", "Tocantins"],
    "Nordeste": ["Alagoas", "Bahia", "Ceará", "Maranhão", "Paraíba", "Pernambuco",
                 "Piauí", "Rio Grande do Norte", "Sergipe"],
    "Centro-Oeste": ["Distrito Federal", "Goiás", "Mato Grosso", "Mato Grosso do Sul"],
    "Sudeste": ["Espírito Santo", "Minas Gerais", "Rio de Janeiro", "São Paulo"],
    "Sul": ["Paraná", "Rio Grande do Sul", "Santa Catarina"],
}

# ==========================================================
# PROFISSÕES
# requisito: "nenhum" | "concurso" | "universidade"
# ==========================================================
PROFISSOES = {
    "vendedor": {
        "emoji": "🛍️", "requisito": "nenhum",
        "descricao": "Vende itens de lojas para outros usuários.",
        "tarefas": [
            {"nome": "Atender um cliente", "min": 15, "max": 35, "xp": 8},
            {"nome": "Fechar uma grande venda", "min": 30, "max": 60, "xp": 15},
        ],
    },
    "motoboy": {
        "emoji": "🛵", "requisito": "nenhum",
        "descricao": "Entrega lanches e mercado pelo iFood. Risco de acidente (35%).",
        "chance_acidente": 0.35,
        "tarefas": [
            {"nome": "Entregar um pedido", "min": 20, "max": 40, "xp": 10},
        ],
    },
    "empresario": {
        "emoji": "💼", "requisito": "nenhum",
        "descricao": "Gerencia uma loja. Sonegar impostos dá 70% de chance de perder tudo.",
        "chance_perder_tudo": 0.70,
        "tarefas": [
            {"nome": "Fechar um contrato comercial", "min": 40, "max": 90, "xp": 18},
        ],
    },
    "criminoso": {
        "emoji": "🔫", "requisito": "nenhum",
        "descricao": "Rouba pessoas/lojas e pode formar facções. Alto risco de prisão.",
        "tarefas": [
            {"nome": "Pequeno furto", "min": 20, "max": 50, "xp": 12},
        ],
    },
    "jogador_futebol": {
        "emoji": "⚽", "requisito": "nenhum",
        "descricao": "Atua em times brasileiros. Ganhos variam com desempenho.",
        "tarefas": [
            {"nome": "Jogar uma partida", "min": 50, "max": 120, "xp": 20},
        ],
    },
    "domestica": {
        "emoji": "🧹", "requisito": "nenhum",
        "descricao": "Cuida da casa de quem te contratar.",
        "tarefas": [
            {"nome": "Limpar a casa", "min": 15, "max": 30, "xp": 8},
        ],
    },
    "policial_militar": {
        "emoji": "🚓", "requisito": "concurso",
        "descricao": "Atende ocorrências (?acionar190) e tenta prender criminosos.",
        "tarefas": [],
    },
    "policial_civil": {
        "emoji": "🕵️", "requisito": "concurso",
        "descricao": "Lê boletins de ocorrência, encaminha presos e investiga corrupção.",
        "tarefas": [],
    },
    "samu": {
        "emoji": "🚑", "requisito": "concurso",
        "descricao": "Socorre usuários feridos (?acionar192).",
        "tarefas": [],
    },
    "professor": {
        "emoji": "📖", "requisito": "concurso",
        "descricao": "Aplica as provas de concurso e de universidade.",
        "tarefas": [],
    },
    "juiz": {
        "emoji": "⚖️", "requisito": "universidade",
        "descricao": "Julga processos enviados pelos advogados.",
        "tarefas": [],
    },
    "advogado": {
        "emoji": "📜", "requisito": "universidade",
        "descricao": "Cuida de pedidos civis (ex: remoção de família via OAB).",
        "tarefas": [],
    },
    "advogado_criminal": {
        "emoji": "🔎", "requisito": "universidade",
        "descricao": "Encaminha casos criminais ao juiz.",
        "tarefas": [],
    },
    "medico": {
        "emoji": "⚕️", "requisito": "universidade",
        "descricao": "Atende pacientes no hospital.",
        "tarefas": [],
    },
}

REQUISITO_TEXTO = {
    "nenhum": "Não requer ensino superior nem concurso.",
    "concurso": "Requer aprovação em concurso público (ainda não implementado).",
    "universidade": "Requer ensino superior completo (ainda não implementado).",
}

# ==========================================================
# EVENTOS ALEATÓRIOS
# ==========================================================
EVENTOS = [
    {"nome": "🎉 Festival na cidade!", "tipo": "bonus", "min": 20, "max": 50,
     "mensagem": "Um festival animou a cidade e todos ganharam uma graninha extra!"},
    {"nome": "📈 Alta no mercado", "tipo": "bonus", "min": 10, "max": 40,
     "mensagem": "Os preços subiram e quem tinha produtos pra vender lucrou bem."},
    {"nome": "🐀 Praga de ratos", "tipo": "perda", "min": 10, "max": 30,
     "mensagem": "Uma praga estragou parte dos estoques da cidade."},
    {"nome": "🥷 Onda de furtos", "tipo": "perda", "min": 15, "max": 40,
     "mensagem": "Ladrões passaram pela cidade e limparam alguns bolsos."},
]

def xp_para_proximo_nivel(nivel: int) -> int:
    return nivel * 100
