"""Service que escolhe mensagens contextuais baseadas no estado do jogador."""
import random
import database as db
from data import mensagens as msg


def mensagem_falha_economica(personagem: dict) -> str:
    """Mensagem quando o jogador tenta comprar algo mas não tem grana."""
    return msg.mensagem_com_helper("SEM_DINHEIRO_COMPRA")


def mensagem_status_baixo(personagem: dict) -> str:
    """Mensagem quando algum status tá crítico (< 30)."""
    criticos = []
    if personagem.get("energia", 100) < 30:
        criticos.append("SEM_ENERGIA")
    if personagem.get("fome", 100) < 30:
        criticos.append("SEM_FOME")
    if personagem.get("higiene", 100) < 30:
        criticos.append("SEM_HIGIENE")
    if personagem.get("estresse", 0) > 70:
        criticos.append("MUITO_ESTRESSADO")
    
    if not criticos:
        return ""
    
    categoria = random.choice(criticos)
    return msg.mensagem_com_helper(categoria)


def mensagem_sucesso_trabalho(subiu_nivel: bool = False, nivel: int = 1) -> str:
    """Mensagem de sucesso após trabalho."""
    base = msg.escolher_aleatorio(msg.SUCESSO_TRABALHO)
    if subiu_nivel:
        nivel_msg = random.choice(msg.SUBIU_NIVEL).format(nivel=nivel)
        return f"{base}\n\n{nivel_msg}"
    return base


def mensagem_falhou_minigame() -> str:
    """Mensagem quando falhou no minigame."""
    return msg.mensagem_com_helper("FALHOU_MINIGAME")


def mensagem_foi_preso() -> str:
    """Mensagem quando foi preso."""
    return msg.mensagem_com_helper("PRESO")


def mensagem_sem_personagem() -> str:
    """Mensagem quando não tem personagem."""
    return msg.mensagem_com_helper("SEM_PERSONAGEM")


def mensagem_sem_profissao() -> str:
    """Mensagem quando não tem profissão."""
    return msg.mensagem_com_helper("SEM_PROFISSAO")


def mensagem_item_nao_encontrado() -> str:
    """Mensagem quando item não existe."""
    return msg.mensagem_com_helper("ITEM_NAO_ENCONTRADO")


def dica_aleatoria() -> str:
    """Retorna uma dica aleatória."""
    return msg.escolher_aleatorio(msg.AJUDA_GENERICA)


def saude_personagem_com_dicas(personagem: dict) -> str:
    """Retorna resumo de saúde do personagem com dicas se tiver algo crítico."""
    linhas = []
    
    if personagem.get("energia", 100) < 30:
        linhas.append("⚡ Energia baixa — usa `?dormir`")
    if personagem.get("fome", 100) < 30:
        linhas.append("🍔 Fome baixa — usa `?comer`")
    if personagem.get("higiene", 100) < 30:
        linhas.append("🚿 Higiene baixa — usa `?banho`")
    if personagem.get("estresse", 0) > 70:
        linhas.append("😰 Estresse alto — usa `?relaxar`")
    if personagem.get("saude", 100) < 30:
        linhas.append("❤️ Saúde crítica — usa `?usaritem` com remédio")
    
    if not linhas:
        return "✅ Tu tá de boa, parceiro! Tudo em cima."
    
    return "⚠️ Atenção, mano:\n" + "\n".join(linhas)
