import database as db
from utils.logger import log_acao


def criar_novo_personagem(user_id: str, dados: dict) -> int:
    """Cria um personagem e desativa os antigos do usuário."""
    quantidade = db.contar_personagens(user_id)
    if quantidade >= 3:
        raise ValueError("Você já tem 3 personagens. Exclua um antes de criar outro.")
    
    personagem_id = db.criar_personagem(user_id, dados)
    log_acao("SERVICE_PERSONAGEM_CRIADO", f"user_id={user_id} id={personagem_id}")
    return personagem_id


def ativar_personagem(user_id: str, personagem_id: int) -> bool:
    """Ativa um personagem específico."""
    sucesso = db.definir_personagem_ativo(user_id, personagem_id)
    if sucesso:
        log_acao("SERVICE_PERSONAGEM_ATIVADO", f"user_id={user_id} id={personagem_id}")
    return sucesso


def obter_dados_personagem(user_id: str):
    """Retorna o personagem ativo do usuário."""
    return db.obter_personagem_ativo(user_id)


def registrar_trabalho(personagem_id: int, ganho: int, xp: int):
    """Registra um trabalho e atualiza saldo/xp/nível."""
    resultado = db.registrar_trabalho_personagem(personagem_id, ganho, xp)
    log_acao("SERVICE_TRABALHO_REGISTRADO", f"personagem_id={personagem_id} ganho={ganho} xp={xp}")
    return resultado
