"""Sistema de sugestão de comandos quando o usuário digita errado."""
from difflib import get_close_matches


def sugerir_comando(comando_digitado: str, comandos_disponiveis: list, limite: int = 3) -> list:
    """
    Sugere comandos similares ao digitado.
    
    Args:
        comando_digitado: O comando que o usuário digitou (sem o prefixo)
        comandos_disponiveis: Lista de todos os comandos disponíveis
        limite: Número máximo de sugestões
    
    Returns:
        Lista de comandos sugeridos (mais similares primeiro)
    """
    if not comando_digitado or not comandos_disponiveis:
        return []
    
    # Remove prefixo se tiver
    comando = comando_digitado.lower().strip()
    if comando.startswith('?'):
        comando = comando[1:]
    
    # Busca correspondências mais próximas
    sugestoes = get_close_matches(
        comando,
        comandos_disponiveis,
        n=limite,
        cutoff=0.6  # 60% de similaridade mínima
    )
    
    return sugestoes


def formatar_mensagem_sugestao(comando_digitado: str, sugestoes: list) -> str:
    """Formata a mensagem de sugestão de comandos."""
    if not sugestoes:
        return f"❓ Não encontrei o comando `{comando_digitado}`.\n\n💡 Usa `?ajuda` pra ver todos os comandos disponíveis."
    
    if len(sugestoes) == 1:
        return f"❓ Você quis dizer `?{sugestoes[0]}`?\n\n💡 Usa `?ajuda {sugestoes[0]}` pra ver detalhes."
    
    lista = "\n".join(f"• `?{s}`" for s in sugestoes)
    return f"❓ Você quis dizer algum desses?\n\n{lista}\n\n💡 Usa `?ajuda` pra ver todos os comandos."
