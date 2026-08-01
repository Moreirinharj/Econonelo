"""Utilitários de horário com timezone de Brasília (UTC-3)."""
from datetime import datetime, timezone, timedelta

# Timezone de Brasília (UTC-3)
BRASILIA_TZ = timezone(timedelta(hours=-3))


def agora_brasilia() -> datetime:
    """Retorna o horário atual de Brasília."""
    return datetime.now(BRASILIA_TZ)


def formatar_data_hora(timestamp: float = None, incluir_ano: bool = False) -> str:
    """
    Formata timestamp pra data/hora de Brasília.
    
    Args:
        timestamp: Unix timestamp (se None, usa agora)
        incluir_ano: Se True, inclui o ano
    
    Returns:
        String formatada como "31/07 15:30" ou "31/07/2026 15:30"
    """
    if timestamp is None:
        dt = agora_brasilia()
    else:
        dt = datetime.fromtimestamp(timestamp, tz=BRASILIA_TZ)
    
    if incluir_ano:
        return dt.strftime("%d/%m/%Y %H:%M")
    return dt.strftime("%d/%m %H:%M")


def formatar_data(timestamp: float = None, incluir_ano: bool = False) -> str:
    """Formata timestamp pra só a data de Brasília."""
    if timestamp is None:
        dt = agora_brasilia()
    else:
        dt = datetime.fromtimestamp(timestamp, tz=BRASILIA_TZ)
    
    if incluir_ano:
        return dt.strftime("%d/%m/%Y")
    return dt.strftime("%d/%m")


def formatar_hora(timestamp: float = None) -> str:
    """Formata timestamp pra só a hora de Brasília."""
    if timestamp is None:
        dt = agora_brasilia()
    else:
        dt = datetime.fromtimestamp(timestamp, tz=BRASILIA_TZ)
    return dt.strftime("%H:%M")


def tempo_restante_texto(segundos: float) -> str:
    """Formata segundos restantes em texto legível."""
    segundos = int(segundos)
    if segundos < 0:
        return "0s"
    
    dias, resto = divmod(segundos, 86400)
    horas, resto = divmod(resto, 3600)
    minutos, segs = divmod(resto, 60)
    
    partes = []
    if dias > 0:
        partes.append(f"{dias}d")
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0:
        partes.append(f"{minutos}min")
    if segs > 0 and not partes:
        partes.append(f"{segs}s")
    
    return " ".join(partes) or "0s"
