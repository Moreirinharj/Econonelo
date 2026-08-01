"""
Filtro de nomes pejorativos ou com referências a criminosos.
Usado na criação de personagem pra barrar nomes inapropriados.
"""

# Palavras proibidas (pejorativos, ofensas, etc)
PALAVRAS_PROIBIDAS = [
    # Ofensas gerais
    "idiota", "burro", "otario", "otário", "babaca", "desgraçado", "desgracado",
    "merda", "porra", "caralho", "foda", "fdp", "vsf", "vsc", "cuzao", "cuzão",
    "puta", "puto", "bicha", "viado", "viadinho", "baitola", "traveco",
    "retardado", "mongol", "down", "aleijado", "gordo", "magro",
    
    # Referências a criminosos famosos
    "escobar", "pablo", "capone", "bin laden", "hitler", "stalin",
    "mandela", "chico bandido", "marcola", "nem da rocinha",
    "beira mar", "presidio", "faccao", "facção", "trafico", "tráfico",
    
    # Termos criminosos
    "assassino", "assasino", "matador", "ladrão", "ladrao", "bandido",
    "marginal", "criminoso", "crackudo", "maconheiro", "traficante",
    "estuprador", "pedofilo", "pedófilo", "sequestrador", "sequestrador",
    
    # Palavrões e ofensas
    "arrombado", "arrombada", "corno", "cornudo", "vaca", "vadia",
    "vagabundo", "vagabunda", "piranha", "cachorra", "cachorro",
]

# Nomes de personagens fictícios criminosos
NOMES_FICTICIOS_PROIBIDOS = [
    "heisenberg", "walter white", "jesse pinkman",
    "michael corleone", "tony montana",
    "joker", "coringa", "palhaço",
]


def validar_nome(nome: str) -> dict:
    """
    Valida se um nome é apropriado.
    Retorna dict com:
    - valido: bool
    - motivo: str (se inválido)
    """
    nome_lower = nome.lower().strip()
    
    # Verifica tamanho
    if len(nome_lower) < 2:
        return {"valido": False, "motivo": "Nome muito curto (mínimo 2 caracteres)."}
    
    if len(nome_lower) > 30:
        return {"valido": False, "motivo": "Nome muito longo (máximo 30 caracteres)."}
    
    # Verifica palavras proibidas
    for palavra in PALAVRAS_PROIBIDAS:
        if palavra in nome_lower:
            return {
                "valido": False,
                "motivo": f"Nome contém palavra inapropriada: '{palavra}'"
            }
    
    # Verifica nomes fictícios proibidos
    for nome_ficticio in NOMES_FICTICIOS_PROIBIDOS:
        if nome_ficticio in nome_lower:
            return {
                "valido": False,
                "motivo": f"Nome contém referência a personagem criminoso: '{nome_ficticio}'"
            }
    
    # Verifica números (nomes não podem ter números)
    if any(char.isdigit() for char in nome_lower):
        return {"valido": False, "motivo": "Nome não pode conter números."}
    
    # Verifica caracteres especiais (só letras, espaços e hífens permitidos)
    if not all(char.isalpha() or char.isspace() or char == '-' for char in nome_lower):
        return {"valido": False, "motivo": "Nome só pode conter letras, espaços e hífens."}
    
    return {"valido": True, "motivo": ""}


def mensagem_nome_invalido() -> str:
    """Retorna mensagem Geração Z pra nome inválido."""
    return "Ai não hein, esse nome o padre não batiza 😇\n\n💡 Tenta um nome mais normal, mano. Nada de palavrão, ofensa ou referência a bandido, tá?"
