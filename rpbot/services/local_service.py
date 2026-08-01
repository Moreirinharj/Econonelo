"""Lógica de locais do mundo e seed inicial."""
import database as db
from utils.logger import log_acao

TIPOS_LOCAIS = {
    "hospital": {"emoji": "🏥", "nome": "Hospital"},
    "universidade": {"emoji": "🎓", "nome": "Universidade"},
    "restaurante": {"emoji": "🍽️", "nome": "Restaurante"},
    "mercado": {"emoji": "🛒", "nome": "Mercado"},
    "farmacia": {"emoji": "💊", "nome": "Farmácia"},
    "delegacia": {"emoji": "🚔", "nome": "Delegacia"},
    "forum": {"emoji": "⚖️", "nome": "Fórum"},
    "estadio": {"emoji": "🏟️", "nome": "Estádio"},
    "praia": {"emoji": "🏖️", "nome": "Praia"},
    "parque": {"emoji": "🌳", "nome": "Parque"},
    "banco": {"emoji": "🏦", "nome": "Banco"},
    "loterica": {"emoji": "🎰", "nome": "Lotérica"},
    "igreja": {"emoji": "⛪", "nome": "Igreja"},
    "shopping": {"emoji": "🛍️", "nome": "Shopping"},
}

SEED_LOCAIS = [
    # São Paulo
    ("Hospital das Clínicas", "hospital", "São Paulo", "Cerqueira César", "Hospital universitário da USP", "00:00", "23:59"),
    ("USP", "universidade", "São Paulo", "Butantã", "Universidade de São Paulo", "07:00", "23:00"),
    ("Restaurante Fasano", "restaurante", "São Paulo", "Itaim Bibi", "Alta gastronomia italiana", "12:00", "00:00"),
    ("Pão de Açúcar Jardins", "mercado", "São Paulo", "Jardins", "Supermercado premium", "07:00", "22:00"),
    ("Drogasil Paulista", "farmacia", "São Paulo", "Paulista", "Farmácia 24h", "00:00", "23:59"),
    ("1º DP Consolação", "delegacia", "São Paulo", "Consolação", "Delegacia de polícia", "00:00", "23:59"),
    ("Fórum João Mendes", "forum", "São Paulo", "Centro", "Fórum central da comarca", "09:00", "18:00"),
    ("Allianz Parque", "estadio", "São Paulo", "Perdizes", "Estádio do Palmeiras", "09:00", "22:00"),
    ("Parque Ibirapuera", "parque", "São Paulo", "Moema", "Maior parque da cidade", "05:00", "00:00"),
    ("Banco do Brasil Paulista", "banco", "São Paulo", "Paulista", "Agência central", "10:00", "16:00"),
    ("Lotérica Paulista", "loterica", "São Paulo", "Paulista", "Loterias e apostas", "08:00", "20:00"),
    ("Catedral da Sé", "igreja", "São Paulo", "Sé", "Catedral metropolitana", "08:00", "18:00"),
    ("Shopping Ibirapuera", "shopping", "São Paulo", "Moema", "Shopping center premium", "10:00", "22:00"),
    
    # Rio de Janeiro
    ("Hospital Copa D'Or", "hospital", "Rio de Janeiro", "Copacabana", "Hospital de referência", "00:00", "23:59"),
    ("UFRJ", "universidade", "Rio de Janeiro", "Fundão", "Universidade Federal do RJ", "07:00", "22:00"),
    ("Restaurante Aprazível", "restaurante", "Rio de Janeiro", "Santa Teresa", "Gastronomia brasileira", "12:00", "23:00"),
    ("Pão de Açúcar Copacabana", "mercado", "Rio de Janeiro", "Copacabana", "Supermercado", "07:00", "22:00"),
    ("Drogaria Pacheco Ipanema", "farmacia", "Rio de Janeiro", "Ipanema", "Farmácia de bairro", "07:00", "22:00"),
    ("16ª DP Copacabana", "delegacia", "Rio de Janeiro", "Copacabana", "Delegacia turística", "00:00", "23:59"),
    ("Fórum da Capital RJ", "forum", "Rio de Janeiro", "Centro", "Fórum central", "09:00", "18:00"),
    ("Maracanã", "estadio", "Rio de Janeiro", "Maracanã", "Estádio histórico", "09:00", "22:00"),
    ("Praia de Copacabana", "praia", "Rio de Janeiro", "Copacabana", "Praia famosa mundialmente", "00:00", "23:59"),
    ("Praia de Ipanema", "praia", "Rio de Janeiro", "Ipanema", "Praia icônica", "00:00", "23:59"),
    ("Parque Lage", "parque", "Rio de Janeiro", "Jardim Botânico", "Parque histórico com palacete", "08:00", "17:00"),
    ("Bradesco Ipanema", "banco", "Rio de Janeiro", "Ipanema", "Agência bancária", "10:00", "16:00"),
    ("Igreja de Candelária", "igreja", "Rio de Janeiro", "Centro", "Igreja histórica", "09:00", "17:00"),
    ("Shopping Rio Sul", "shopping", "Rio de Janeiro", "Botafogo", "Shopping tradicional", "10:00", "22:00"),
    
    # Belo Horizonte
    ("Hospital Biocor", "hospital", "Belo Horizonte", "Sion", "Hospital particular", "00:00", "23:59"),
    ("UFMG", "universidade", "Belo Horizonte", "Pampulha", "Universidade Federal de MG", "07:00", "22:00"),
    ("1ª Delegacia Regional", "delegacia", "Belo Horizonte", "Centro", "Delegacia central", "00:00", "23:59"),
    ("Mineirão", "estadio", "Belo Horizonte", "Pampulha", "Estádio Governador Magalhães Pinto", "09:00", "22:00"),
    ("Parque Municipal", "parque", "Belo Horizonte", "Centro", "Parque no coração da cidade", "06:00", "22:00"),
    ("Igreja São Francisco", "igreja", "Belo Horizonte", "São Francisco", "Igreja tradicional", "08:00", "18:00"),
    ("Shopping Diamond Mall", "shopping", "Belo Horizonte", "Lourdes", "Shopping premium", "10:00", "22:00"),
    
    # Curitiba
    ("Hospital de Clínicas UFPR", "hospital", "Curitiba", "Centro Politécnico", "Hospital universitário", "00:00", "23:59"),
    ("UFPR", "universidade", "Curitiba", "Centro", "Universidade Federal do PR", "07:00", "22:00"),
    ("Arena da Baixada", "estadio", "Curitiba", "Água Verde", "Estádio do Athletico-PR", "09:00", "22:00"),
    ("Parque Tanguá", "parque", "Curitiba", "São Lourenço", "Parque com mirante", "06:00", "20:00"),
    ("Jardim Botânico", "parque", "Curitiba", "Jardim Botânico", "Cartão-postal da cidade", "06:00", "20:00"),
    ("Shopping Curitiba", "shopping", "Curitiba", "Água Verde", "Shopping center", "10:00", "22:00"),
    
    # Porto Alegre
    ("Hospital São Lucas PUC", "hospital", "Porto Alegre", "Santa Cecília", "Hospital universitário", "00:00", "23:59"),
    ("UFRGS", "universidade", "Porto Alegre", "Centro", "Universidade Federal do RS", "07:00", "22:00"),
    ("Arena do Grêmio", "estadio", "Porto Alegre", "Humenaitá", "Arena do Grêmio FBPA", "09:00", "22:00"),
    ("Beira-Rio", "estadio", "Porto Alegre", "Menino Deus", "Estádio do Inter", "09:00", "22:00"),
    ("Parque Farroupilha", "parque", "Porto Alegre", "Farroupilha", "Parque da Redenção", "05:00", "23:00"),
    ("Shopping Iguatemi POA", "shopping", "Porto Alegre", "Petrópolis", "Shopping premium", "10:00", "22:00"),
    
    # Salvador
    ("Hospital Espanhol", "hospital", "Salvador", "Graça", "Hospital tradicional", "00:00", "23:59"),
    ("UFBA", "universidade", "Salvador", "Ondina", "Universidade Federal da Bahia", "07:00", "22:00"),
    ("Praia do Porto da Barra", "praia", "Salvador", "Barra", "Uma das praias mais bonitas", "00:00", "23:59"),
    ("Farol da Barra", "praia", "Salvador", "Barra", "Praia histórica com farol", "00:00", "23:59"),
    ("Pelourinho", "parque", "Salvador", "Centro Histórico", "Centro histórico tombado", "00:00", "23:59"),
    ("Igreja São Francisco", "igreja", "Salvador", "Pelourinho", "Igreja barroca histórica", "09:00", "17:00"),
    ("Shopping Barra", "shopping", "Salvador", "Barra", "Shopping à beira-mar", "10:00", "22:00"),
]


def popular_mundo():
    """Popula o mundo com locais reais pré-definidos."""
    if db.contar_locais() > 0:
        log_acao("MUNDO_JA_POPULADO", f"locais_existentes={db.contar_locais()}")
        return 0
    
    count = 0
    for nome, tipo, cidade, bairro, descricao, abertura, fechamento in SEED_LOCAIS:
        db.criar_local(nome, tipo, cidade, bairro, descricao, abertura, fechamento)
        count += 1
    
    log_acao("MUNDO_POPULADO", f"locais_criados={count}")
    return count


def locais_por_tipo(cidade: str = None) -> dict:
    """Retorna locais agrupados por tipo."""
    locais = db.listar_locais(cidade=cidade)
    agrupados = {}
    for local in locais:
        tipo = local["tipo"]
        if tipo not in agrupados:
            agrupados[tipo] = []
        agrupados[tipo].append(local)
    return agrupados
