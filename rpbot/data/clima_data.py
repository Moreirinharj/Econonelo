"""Dados e modificadores do sistema de clima e estações do ano."""

ESTACOES = ["Primavera", "Verão", "Outono", "Inverno"]

# Climas e seus efeitos no gameplay
# mod_energia: quanto drena a mais por hora (negativo = drena mais)
# mod_fome: quanto aumenta a fome por hora
# mod_motoboy: multiplicador de salário pra motoboys
CLIMAS = {
    "Ensolarado": {
        "temperatura": 28,
        "mod_energia": 0,
        "mod_fome": 0,
        "mod_motoboy": 1.0,
        "descricao": "Dia lindo e ensolarado. Perfeito pra passear!",
        "emoji": "☀️"
    },
    "Nublado": {
        "temperatura": 22,
        "mod_energia": 0,
        "mod_fome": 0,
        "mod_motoboy": 1.0,
        "descricao": "Céu encoberto, clima agradável.",
        "emoji": "☁️"
    },
    "Chuvoso": {
        "temperatura": 18,
        "mod_energia": -5,
        "mod_fome": 0,
        "mod_motoboy": 1.5,  # 50% a mais de ganho
        "descricao": "Chuva constante. Cuidado nas ruas, mas os motoboys ganham mais!",
        "emoji": "🌧️"
    },
    "Tempestade": {
        "temperatura": 15,
        "mod_energia": -10,
        "mod_fome": 0,
        "mod_motoboy": 2.0,  # 100% a mais de ganho (alto risco)
        "descricao": "Tempestade forte! Perigo nas ruas. Motoboys ganham o dobro!",
        "emoji": "⛈️"
    },
    "Frio": {
        "temperatura": 8,
        "mod_energia": -5,
        "mod_fome": 5,  # Gasta mais energia pra manter o calor
        "mod_motoboy": 1.2,
        "descricao": "Frio intenso! Agasalhe-se ou sua energia vai cair rápido.",
        "emoji": "❄️"
    },
    "Calor": {
        "temperatura": 38,
        "mod_energia": -10,
        "mod_fome": 10,  # Desidrata e dá fome
        "mod_motoboy": 0.8,  # Menos gente pede delivery
        "descricao": "Calor extremo do cão! Hidrate-se ou vai desmaiar.",
        "emoji": "🥵"
    }
}

# Eventos climáticos raros que a IA pode gerar
EVENTOS_CLIMATICOS = [
    {"nome": "Onda de Calor", "clima": "Calor", "duracao_horas": 12, "mensagem": "🚨 ALERTA: Onda de calor extrema atingindo a região!"},
    {"nome": "Frente Fria", "clima": "Frio", "duracao_horas": 24, "mensagem": "🚨 ALERTA: Frente fria intensa chegando. Temperaturas vão despencar!"},
    {"nome": "Temporal", "clima": "Tempestade", "duracao_horas": 6, "mensagem": "🚨 ALERTA: Defensoria civil emite alerta de temporal com ventos fortes!"}
]
