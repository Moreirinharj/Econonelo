"""
Helper para mostrar mensagem de ajuda quando comando é usado sem argumento.
"""
from utils.embeds import embed_aviso


def mostrar_ajuda_cpf(ctx, comando: str, descricao: str = None):
    """
    Retorna um embed de ajuda para comandos que exigem CPF/ID.
    
    Args:
        ctx: Contexto do comando
        comando: Nome do comando (ex: "?atender")
        descricao: Descrição opcional do que o comando faz
    """
    texto = f"**Como usar:**\n`{comando} <cpf/id>`\n\n"
    texto += "**Exemplos:**\n"
    texto += f"• `{comando} 123`\n"
    texto += f"• `{comando} 042`\n\n"
    texto += "ℹ️ O CPF deve ter 3 dígitos (000 a 999).\n\n"
    
    if descricao:
        texto += f"**O que faz:**\n{descricao}\n\n"
    
    texto += "Use `?personagens` para ver a lista de CPFs disponíveis."
    
    return embed_aviso("Uso do comando", texto)


def mostrar_ajuda_pedido(ctx, comando: str, descricao: str = None):
    """
    Retorna um embed de ajuda para comandos que exigem ID de pedido.
    """
    texto = f"**Como usar:**\n`{comando} <pedido_id>`\n\n"
    texto += "**Exemplo:**\n"
    texto += f"• `{comando} 5`\n\n"
    
    if descricao:
        texto += f"**O que faz:**\n{descricao}\n\n"
    
    texto += "Use `?pedidos` para ver os pedidos disponíveis."
    
    return embed_aviso("Uso do comando", texto)


def validar_cpf(cpf_str: str) -> bool:
    """
    Valida se o CPF tem 3 dígitos (000-999).
    """
    if not cpf_str.isdigit():
        return False
    if len(cpf_str) != 3:
        return False
    return True
