"""
Helper para verificar se o usuário tem personagem vinculado ao CPF/discord_id.
Usado em todos os comandos de profissão.
"""
import discord
from discord.ext import commands
from services.personagem_service import obter_dados_personagem
from data.constantes import MSG_SEM_PERSONAGEM
from utils.embeds import embed_erro


async def verificar_personagem(ctx: commands.Context) -> dict | None:
    """
    Verifica se o usuário tem um personagem ativo vinculado ao seu discord_id.
    
    Retorna:
        - dict com dados do personagem se existir
        - None e envia mensagem de erro se não existir
    """
    personagem = obter_dados_personagem(str(ctx.author.id))
    
    if not personagem:
        await ctx.reply(
            embed=embed_erro(
                "Personagem não encontrado",
                "Você precisa criar um personagem primeiro.\n\n"
                "Use `?criar <nome> <cpf>` para criar seu personagem."
            ),
            ephemeral=True
        )
        return None
    
    return personagem


async def verificar_personagem_e_profissao(
    ctx: commands.Context, 
    profissoes_permitidas: list[str]
) -> dict | None:
    """
    Verifica se o usuário tem personagem E se a profissão dele está na lista permitida.
    
    Args:
        ctx: Contexto do comando
        profissoes_permitidas: Lista de profissões que podem usar este comando
            Ex: ["policial_militar", "policial_civil", "samu"]
    
    Retorna:
        - dict com dados do personagem se tudo OK
        - None e envia mensagem de erro
    """
    personagem = await verificar_personagem(ctx)
    if not personagem:
        return None
    
    profissao_atual = personagem.get("profissao", "").lower()
    
    if profissao_atual not in profissoes_permitidas:
        profissoes_formatadas = ", ".join([f"`{p}`" for p in profissoes_permitidas])
        await ctx.reply(
            embed=embed_erro(
                "Profissão não autorizada",
                f"Este comando só pode ser usado por: {profissoes_formatadas}\n\n"
                f"Sua profissão atual: `{profissao_atual or 'nenhuma'}`"
            ),
            ephemeral=True
        )
        return None
    
    return personagem
