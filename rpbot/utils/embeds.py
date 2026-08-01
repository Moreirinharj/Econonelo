import discord
from data.constantes import (
    COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, COR_INFO, COR_EMERGENCIA,
    EMOJI_ERRO, EMOJI_SUCESSO, EMOJI_AVISO, EMOJI_INFO,
)


def embed_padrao(titulo: str, descricao: str = "", cor: int = COR_PADRAO) -> discord.Embed:
    return discord.Embed(title=titulo, description=descricao, color=cor)


def embed_sucesso(titulo: str, descricao: str = "") -> discord.Embed:
    return discord.Embed(
        title=f"{EMOJI_SUCESSO} {titulo}",
        description=descricao,
        color=COR_SUCESSO,
    )


def embed_erro(titulo: str, descricao: str = "") -> discord.Embed:
    return discord.Embed(
        title=f"{EMOJI_ERRO} {titulo}",
        description=descricao,
        color=COR_ERRO,
    )


def embed_aviso(titulo: str, descricao: str = "") -> discord.Embed:
    return discord.Embed(
        title=f"{EMOJI_AVISO} {titulo}",
        description=descricao,
        color=COR_AVISO,
    )


def embed_info(titulo: str, descricao: str = "") -> discord.Embed:
    return discord.Embed(
        title=f"{EMOJI_INFO} {titulo}",
        description=descricao,
        color=COR_INFO,
    )


def embed_emergencia(titulo: str, descricao: str = "") -> discord.Embed:
    return discord.Embed(
        title=f"🚨 {titulo}",
        description=descricao,
        color=COR_EMERGENCIA,
    )
