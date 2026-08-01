"""
Valores de balanceamento do jogo.
Tudo que afeta economia, progressão e chances está aqui.
Ajuste esses valores pra manter o jogo equilibrado.
"""

# ===== ECONOMIA =====
SALDO_INICIAL = 500
SALDO_BANCO_INICIAL = 0
LIMITE_CARTAO_INICIAL = 1000

# ===== SALÁRIOS POR PROFISSÃO (por trabalho) =====
SALARIOS = {
    "policial_militar": {"min": 150, "max": 300, "xp": 25, "cooldown_min": 15},
    "policial_civil": {"min": 200, "max": 400, "xp": 30, "cooldown_min": 20},
    "samu": {"min": 180, "max": 350, "xp": 28, "cooldown_min": 15},
    "medico": {"min": 250, "max": 500, "xp": 35, "cooldown_min": 20},
    "professor": {"min": 120, "max": 220, "xp": 20, "cooldown_min": 15},
    "juiz": {"min": 400, "max": 800, "xp": 50, "cooldown_min": 30},
    "advogado": {"min": 200, "max": 400, "xp": 30, "cooldown_min": 20},
    "advogado_criminal": {"min": 250, "max": 500, "xp": 35, "cooldown_min": 20},
    "motoboy": {"min": 80, "max": 150, "xp": 15, "cooldown_min": 10},
    "empresario": {"min": 300, "max": 1000, "xp": 40, "cooldown_min": 60},
    "jogador_futebol": {"min": 500, "max": 2000, "xp": 60, "cooldown_min": 120},
    "criminoso": {"min": 100, "max": 800, "xp": 20, "cooldown_min": 30},
}

# ===== PROGRESSÃO DE XP =====
XP_BASE_PROXIMO_NIVEL = 100
XP_MULTIPLICADOR_POR_NIVEL = 1.5

def xp_para_proximo_nivel(nivel_atual: int) -> int:
    """Calcula XP necessário pro próximo nível."""
    return int(XP_BASE_PROXIMO_NIVEL * (XP_MULTIPLICADOR_POR_NIVEL ** (nivel_atual - 1)))

# ===== PREÇOS DE ITENS/SERVIÇOS =====
PRECO_LITRO_COMBUSTIVEL = 6
CUSTO_REPARO_VEICULO_POR_DANO = 500
CUSTO_SEGURO_VEICULO_MENSAL = 200
PRECO_COMIDA_BASICA = 25
PRECO_REMEDIO_BASICO = 50

# ===== DECORACOES DE CASA =====
PRECO_DECORACOES = {
    "basica": 0,
    "rustica": 3000,
    "moderna": 5000,
    "luxo": 20000,
}

# ===== VEÍCULOS =====
PRECO_VEICULOS = {
    "moto": 15000,
    "popular": 35000,
    "sedan": 60000,
    "suv": 90000,
    "esportivo": 150000,
}

# ===== CASAS =====
PRECO_CASAS_BASE = {
    "apartamento": 50000,
    "casa": 80000,
    "cobertura": 200000,
    "mansao": 500000,
}

# ===== CHANCES DE SUCESSO =====
CHANCE_PRISAO_BASE = 0.40
CHANCE_PRISAO_INCREMENTO = 0.15
CHANCE_PRISAO_MAX = 0.95

CHANCE_ROUBO_SUCESSO = 0.35
CHANCE_ASSALTO_SUCESSO = 0.25
CHANCE_FUGIR_POLICIA = 0.50

# ===== STATUS =====
STATUS_MAXIMO = 100
STATUS_MINIMO = 0
STATUS_INICIAL_PADRAO = 100
ESTRESSE_INICIAL = 0
REPUTACAO_INICIAL = 50

# ===== DETERIORAÇÃO DE STATUS (por hora) =====
DETERIORACAO_FOME = -5
DETERIORACAO_ENERGIA = -3
DETERIORACAO_HIGIENE = -2
DETERIORACAO_FELICIDADE = -1

# ===== RECUPERAÇÃO DE STATUS =====
RECUPERACAO_COMIDA = 30
RECUPERACAO_AGUA = 15
RECUPERACAO_REMEDIO = 20
RECUPERACAO_BANHO = 50
RECUPERACAO_RELAXAR_ESTRESSE = -20
RECUPERACAO_RELAXAR_FELICIDADE = 10
RECUPERACAO_DORMIR_POR_HORA = 10

# ===== INVENTÁRIO =====
PESO_MAXIMO_BASE = 50.0
PESO_MAXIMO_POR_NIVEL_BONUS = 2.0

# ===== IMPOSTOS E TAXAS =====
IMPOSTO_RENDA_PERCENTUAL = 0.10
TAXA_TRANSACAO_PIX = 0
TAXA_VENDA_CASA = 0.20
TAXA_VENDA_VEICULO = 0.20

# ===== LIMITE DE PERSONAGENS =====
MAX_PERSONAGENS_POR_USUARIO = 3

# ===== COOLDOWN DE COMANDOS (segundos) =====
COOLDOWN_TRABALHAR_PADRAO = 3600
COOLDOWN_PROVA = 86400

# ===== EVENTOS =====
CHANCE_EVENTO_ALEATORIO = 0.10
DURACAO_MIN_EVENTO = 6
DURACAO_MAX_EVENTO = 168

# ===== NPCs =====
DINHEIRO_INICIAL_NPC_MIN = 500
DINHEIRO_INICIAL_NPC_MAX = 5000
IDADE_NPC_MIN = 18
IDADE_NPC_MAX = 70

# ===== REPUTAÇÃO =====
REPUTACAO_POR_TRABALHO = 1
REPUTACAO_POR_CRIME = -10
REPUTACAO_POR_ACAO_HEROICA = 15
REPUTACAO_MAX = 100
REPUTACAO_MIN = 0


def obter_salario(profissao: str) -> dict:
    """Retorna dados de salário de uma profissão."""
    return SALARIOS.get(profissao, {"min": 50, "max": 100, "xp": 10, "cooldown_min": 15})


def obter_peso_maximo(nivel: int = 1) -> float:
    """Calcula peso máximo baseado no nível."""
    return PESO_MAXIMO_BASE + (nivel - 1) * PESO_MAXIMO_POR_NIVEL_BONUS
