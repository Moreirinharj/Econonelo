"""Dados do sistema de agressão, armas e combate."""

# Tipos de agressão com dano, chance de acerto e consequências
TIPOS_AGRESSAO = {
    "soco": {
        "nome": "Soco",
        "dano_min": 5,
        "dano_max": 15,
        "chance_acerto": 0.70,
        "chance_morte": 0.02,
        "chance_flagrante": 0.30,
        "crime": "Lesão corporal",
        "pena_min": 0,
        "pena_max": 3,
        "descricao": "Um soco direto. Pode machucar, mas raramente mata.",
        "emoji": "👊"
    },
    "chute": {
        "nome": "Chute",
        "dano_min": 8,
        "dano_max": 20,
        "chance_acerto": 0.60,
        "chance_morte": 0.03,
        "chance_flagrante": 0.35,
        "crime": "Lesão corporal",
        "pena_min": 0,
        "pena_max": 4,
        "descricao": "Um chute forte. Mais dano que soco, mas mais fácil de desviar.",
        "emoji": "🦵"
    },
    "faca": {
        "nome": "Facada",
        "dano_min": 20,
        "dano_max": 50,
        "chance_acerto": 0.55,
        "chance_morte": 0.25,
        "chance_flagrante": 0.50,
        "crime": "Tentativa de homicídio",
        "pena_min": 5,
        "pena_max": 15,
        "descricao": "Golpe com faca. Alto risco de morte e prisão.",
        "emoji": "🔪",
        "requer_item": "Faca"
    },
    "arma_fogo": {
        "nome": "Tiro",
        "dano_min": 40,
        "dano_max": 80,
        "chance_acerto": 0.75,
        "chance_morte": 0.60,
        "chance_flagrante": 0.70,
        "crime": "Homicídio tentado",
        "pena_min": 10,
        "pena_max": 30,
        "descricao": "Disparo de arma de fogo. Altíssimo risco de morte.",
        "emoji": "🔫",
        "requer_item": "Pistola"
    },
    "taco": {
        "nome": "Bastão/Taco",
        "dano_min": 15,
        "dano_max": 35,
        "chance_acerto": 0.65,
        "chance_morte": 0.10,
        "chance_flagrante": 0.40,
        "crime": "Lesão corporal grave",
        "pena_min": 2,
        "pena_max": 8,
        "descricao": "Golpe com objeto contundente.",
        "emoji": "🏏",
        "requer_item": "Taco de Beisebol"
    },
}

# Armas disponíveis pra comprar/ter no inventário
ARMAS_DISPONIVEIS = {
    "Faca": {
        "nome": "Faca",
        "tipo": "arma_branca",
        "preco": 50,
        "ilegal": True,
        "descricao": "Arma branca simples. Fácil de esconder.",
        "dano_bonus": 10,
    },
    "Taco de Beisebol": {
        "nome": "Taco de Beisebol",
        "tipo": "contundente",
        "preco": 80,
        "ilegal": False,
        "descricao": "Objeto contundente. Legal pra esporte, perigoso pra briga.",
        "dano_bonus": 15,
    },
    "Pistola": {
        "nome": "Pistola",
        "tipo": "arma_fogo",
        "preco": 2000,
        "ilegal": True,
        "descricao": "Arma de fogo. Altamente ilegal sem porte.",
        "dano_bonus": 40,
    },
    "Spray de Pimenta": {
        "nome": "Spray de Pimenta",
        "tipo": "defesa",
        "preco": 30,
        "ilegal": False,
        "descricao": "Spray de defesa pessoal. Legal e não-letal.",
        "dano_bonus": 5,
    },
    "Colete": {
        "nome": "Colete",
        "tipo": "defesa",
        "preco": 500,
        "ilegal": False,
        "descricao": "Colete à prova de balas. Reduz dano recebido.",
        "protecao": 30,
    },
}

# Mensagens de combate
MENSAGENS_ACERTO = [
    "💥 {atacante} acertou {alvo} em cheio!",
    "🎯 Golpe certeiro de {atacante} em {alvo}!",
    "💢 {atacante} golpeou {alvo} com força!",
    "⚡ {atacante} desferiu um golpe em {alvo}!",
]

MENSAGENS_ERRO = [
    "💨 {alvo} desviou do ataque de {atacante}!",
    "🛡️ {alvo} bloqueou o golpe de {atacante}!",
    "❌ {atacante} errou o ataque em {alvo}!",
    "🤸 {alvo} escapou por pouco de {atacante}!",
]

MENSAGENS_MORTE = [
    "💀 {atacante} matou {alvo}! A vítima não resistiu aos ferimentos.",
    "⚰️ {alvo} faleceu após o ataque brutal de {atacante}.",
    "🪦 Tragédia: {alvo} morreu nas mãos de {atacante}.",
]

MENSAGENS_DEFESA = [
    "🛡️ {defensor} se defendeu com sucesso!",
    "💪 {defensor} contra-atacou {agressor}!",
    "🥋 {defensor} usou artes marciais contra {agressor}!",
]
