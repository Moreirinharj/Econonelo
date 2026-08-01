"""IA que controla o mundo: gera notícias, ajusta economia e simula NPCs."""
import random
import database as db
from utils.logger import log_acao

TEMPLATES_NOTICIAS = {
    "economia": [
        ("Inflação dispara", "Especialistas alertam que o preço de {} subiu {}% esta semana em {}, afetando o bolso da população."),
        ("Mercado em alta", "Bolsa de valores de {} registra maior alta dos últimos meses, impulsionada pelo setor de {} em {}."),
        ("Desemprego cai", "Taxa de desemprego em {} atinge menor nível histórico, com {} novas vagas criadas no setor de {}."),
        ("Crise no varejo", "Lojas de {} em {} enfrentam queda de {}% nas vendas este mês."),
    ],
    "clima": [
        ("Frente fria avança", "Temperaturas em {} devem cair {}°C nas próximas 24 horas. População de {} deve se agasalhar."),
        ("Onda de calor", "Defesa civil emite alerta para {} devido a temperaturas que podem superar os {}°C em {}."),
        ("Chuvas intensas", "Previsão de tempestades com {}mm de chuva em {} pode causar alagamentos em {}."),
    ],
    "policial": [
        ("Operação de grande porte", "Polícia deflagra operação contra {} em {}, resultando em {} prisões."),
        ("Aumento de roubos", "Moradores de {} relatam aumento de {} nas últimas semanas. {} ocorrências registradas."),
        ("Acidente grave", "Colisão entre {} veículos deixa {} feridos na principal rodovia de {}."),
    ],
    "esportes": [
        ("Virada histórica", "Time de {} vence campeonato com {} gols de diferença em partida emocionante em {}."),
        ("Novo recorde", "Atleta de {} quebra recorde nacional de {} neste fim de semana."),
    ],
    "entretenimento": [
        ("Show esgotado", "Ingressos para show em {} esgotaram em {} minutos. {} fãs ficaram de fora."),
        ("Novo filme", "Estreia de filme nacional em {} bate recorde de {} espectadores no primeiro dia em {}."),
    ],
}

CIDADES = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre", "Salvador"]
ITENS_ECONOMIA = ["alimentos", "combustível", "aluguel", "eletrônicos", "roupas"]
SETORES = ["tecnologia", "agronegócio", "serviços", "indústria", "varejo"]
CRIMES = ["tráfico de drogas", "roubo de cargas", "lavagem de dinheiro", "fraude bancária", "contrabando"]
EVENTOS_ESPORTIVOS = ["futebol", "basquete", "vôlei", "atletismo"]


def _preencher_template(template: str, categoria: str) -> str:
    if categoria == "economia":
        arg1 = random.choice(ITENS_ECONOMIA + SETORES)
        arg2 = str(random.randint(2, 25))
        arg3 = random.choice(CIDADES)
    elif categoria == "clima":
        arg1 = random.choice(CIDADES)
        arg2 = str(random.randint(5, 15))
        arg3 = random.choice(CIDADES)
    elif categoria == "policial":
        arg1 = random.choice(CRIMES)
        arg2 = random.choice(CIDADES)
        arg3 = str(random.randint(3, 30))
    elif categoria == "esportes":
        arg1 = random.choice(CIDADES)
        arg2 = str(random.randint(1, 5))
        arg3 = random.choice(EVENTOS_ESPORTIVOS)
    elif categoria == "entretenimento":
        arg1 = random.choice(CIDADES)
        arg2 = str(random.randint(5, 60))
        arg3 = str(random.randint(500, 5000))
    else:
        arg1 = arg2 = arg3 = "algo"
    return template.format(arg1, arg2, arg3)


def gerar_noticia_ia() -> dict:
    categoria = random.choice(list(TEMPLATES_NOTICIAS.keys()))
    titulo, template = random.choice(TEMPLATES_NOTICIAS[categoria])
    corpo = _preencher_template(template, categoria)
    db.adicionar_noticia(titulo, corpo, categoria)
    return {"titulo": titulo, "corpo": corpo, "categoria": categoria}


def ajustar_economia_ia():
    inflacao_atual = float(db.obter_estado_mundo("inflacao"))
    variacao = random.uniform(-0.2, 0.3)
    nova_inflacao = round(max(0.5, min(15.0, inflacao_atual + variacao)), 1)
    db.atualizar_estado_mundo("inflacao", str(nova_inflacao))
    return nova_inflacao


def avancar_dia_mundo():
    dia_atual = int(db.obter_estado_mundo("dia"))
    db.atualizar_estado_mundo("dia", str(dia_atual + 1))
    noticia = gerar_noticia_ia()
    inflacao = ajustar_economia_ia()
    acoes_npcs = []
    for _ in range(3):
        acao = db.simular_acao_npc_aleatoria()
        if acao:
            acoes_npcs.append(acao)
    if random.random() < 0.3:
        climas = ["Ensolarado", "Nublado", "Chuvoso", "Frio", "Tempestade"]
        novo_clima = random.choice(climas)
        db.atualizar_estado_mundo("clima", novo_clima)
    return {
        "dia": dia_atual + 1,
        "noticia": noticia,
        "inflacao": inflacao,
        "clima": db.obter_estado_mundo("clima"),
        "acoes_npcs": acoes_npcs
    }


def gerar_evento_aleatorio():
    """Gera um evento aleatório."""
    from data.config import CHANCE_EVENTO_ALEATORIO
    if random.random() > CHANCE_EVENTO_ALEATORIO:
        return None
    return gerar_noticia_ia()


def aplicar_efeitos_eventos(personagem_id):
    """Aplica efeitos dos eventos ativos no personagem."""
    pass


def limpar_eventos_antigos():
    """Limpa eventos antigos."""
    pass
