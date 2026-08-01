"""Sistema de ações privadas — só envolvidos veem detalhes."""
import random
import string
import time
from utils.logger import log_acao

# Armazena ações privadas (expira em 30 min)
ACOES_PRIVADAS = {}


def gerar_id_acao() -> str:
    """Gera ID único pra ação privada."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def registrar_acao_privada(
    executor_id: int,
    vitima_id: int,
    titulo: str,
    descricao_executor: str,
    descricao_vitima: str,
    duracao_min: int = 30
) -> str:
    """
    Registra ação privada e retorna ID.
    
    Args:
        executor_id: ID do Discord de quem executou
        vitima_id: ID do Discord de quem sofreu
        titulo: Título da ação
        descricao_executor: Detalhes pro executor
        descricao_vitima: Detalhes pra vítima
        duracao_min: Quanto tempo fica disponível (minutos)
    
    Returns:
        ID da ação (ex: "A3F9K2L1")
    """
    acao_id = gerar_id_acao()
    
    ACOES_PRIVADAS[acao_id] = {
        "executor_id": executor_id,
        "vitima_id": vitima_id,
        "titulo": titulo,
        "descricao_executor": descricao_executor,
        "descricao_vitima": descricao_vitima,
        "timestamp": time.time(),
        "expira_em": time.time() + (duracao_min * 60),
    }
    
    log_acao("ACAO_PRIVADA_REGISTRADA", f"id={acao_id} executor={executor_id} vitima={vitima_id}")
    return acao_id


def obter_acao_privada(acao_id: str, user_id: int) -> dict:
    """
    Obtém detalhes de ação privada.
    Só executor ou vítima podem ver.
    """
    acao = ACOES_PRIVADAS.get(acao_id)
    
    if not acao:
        return {"sucesso": False, "msg": "❌ Ação não encontrada ou expirou."}
    
    # Verifica se expirou
    if time.time() > acao["expira_em"]:
        del ACOES_PRIVADAS[acao_id]
        return {"sucesso": False, "msg": "❌ Ação expirou (máximo 30 min)."}
    
    # Verifica se o usuário é executor ou vítima
    if user_id not in [acao["executor_id"], acao["vitima_id"]]:
        return {"sucesso": False, "msg": "🚫 Você não tem permissão pra ver essa ação."}
    
    # Determina qual mensagem mostrar
    if user_id == acao["executor_id"]:
        descricao = acao["descricao_executor"]
        papel = "executor"
    else:
        descricao = acao["descricao_vitima"]
        papel = "vítima"
    
    return {
        "sucesso": True,
        "titulo": acao["titulo"],
        "descricao": descricao,
        "papel": papel,
    }


def limpar_acoes_expiradas():
    """Remove ações expiradas."""
    agora = time.time()
    expiradas = [
        acao_id for acao_id, dados in ACOES_PRIVADAS.items()
        if agora > dados["expira_em"]
    ]
    for acao_id in expiradas:
        del ACOES_PRIVADAS[acao_id]
    
    if expiradas:
        log_acao("ACOES_EXPIRADAS_LIMPAS", f"total={len(expiradas)}")


def gerar_mensagem_publica_neutra(vitima_mention: str, acao_id: str) -> str:
    """
    Gera mensagem pública neutra que só menciona a vítima.
    Ex: "🔔 @Maria — Algo aconteceu. Use ?veracao A3F9K2L1 pra detalhes."
    """
    return f"🔔 {vitima_mention} — Algo aconteceu. Use `?veracao {acao_id}` pra detalhes."
