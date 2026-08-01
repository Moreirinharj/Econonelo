import os
import random
import asyncio
import traceback

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import database as db
from services.seed_mundo import popular_mundo_completo, mundo_esta_populado
from data.config import PREFIXO
from utils.logger import log_info, log_error, log_acao
from utils.sugestao_comandos import sugerir_comando, formatar_mensagem_sugestao

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIXO, intents=intents, help_command=None)

COGS = [
    "cogs.personagem",
    "cogs.familia",
    "cogs.oab",
    "cogs.provas",
    "cogs.emergencia",
    "cogs.profissoes",
    "cogs.comandos_faltantes",
    "cogs.interacoes_sociais",
    "cogs.criar_personagem",
    "cogs.economia",
    "cogs.eventos",
    "cogs.ajuda",
    "cogs.status",
    "cogs.acoes",
    "cogs.inventario",
    "cogs.npcs",
    "cogs.casas",
    "cogs.veiculos",
    "cogs.locais",
    "cogs.balanceamento",
    "cogs.minigames",
    "cogs.justica",
    "cogs.educacao",
    "cogs.ia_mundo",
    "cogs.profissional",
    "cogs.editar",
    "cogs.comandos_exclusivos",
    "cogs.corrupcao",
    "cogs.concursos",
    "cogs.aulas",
    "cogs.empresas",
    "cogs.viagem",
    "cogs.relacionamentos",
    "cogs.delivery",
    "cogs.ia_empresas",
    "cogs.clima",
    "cogs.cpf",
    "cogs.heranca",
    "cogs.menu",
    "cogs.agressao",
    "cogs.acao_privada",
    "cogs.news",
    "cogs.admin_ativacao",
    "cogs.imagens",
]




@tasks.loop(hours=6)
async def loop_ia_empresas():
    """Roda a cada 6 horas pra simular dia das empresas."""
    try:
        resultado = simular_dia_empresas()
        log_info(f"IA Empresas: {resultado['estoque_reposto']} repostos, {resultado['precos_ajustados']} preços ajustados, {resultado['pedidos_gerados']} pedidos gerados")
        
        # Gera notícia sobre empresas (30% de chance)
        if random.random() < 0.30:
            gerar_noticia_empresa()
    except Exception as e:
        log_error(f"Erro na IA das empresas: {e}")

@loop_ia_empresas.before_loop
async def before_loop_ia_empresas():
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    log_info(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    log_info(f"Prefixo ativo: {PREFIXO}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Extrair comando digitado
        comando_digitado = ctx.message.content.split()[0]
        if comando_digitado.startswith(PREFIXO):
            comando_digitado = comando_digitado[len(PREFIXO):]
        
        # Buscar sugestões
        comandos_disponiveis = [cmd.name for cmd in bot.commands]
        sugestoes = sugerir_comando(comando_digitado, comandos_disponiveis)
        
        mensagem = formatar_mensagem_sugestao(comando_digitado, sugestoes)
        await ctx.reply(mensagem)
        return
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("Você não tem permissão pra usar esse comando.")
        return
    
    if isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
        await ctx.reply("Não encontrei esse usuário. Marque com @ ou use o ID correto.")
        return
    
    if isinstance(error, commands.CheckFailure):
        return
    
    cmd = ctx.command.name if ctx.command else "desconhecido"
    log_error(f"Erro no comando {cmd} (user={ctx.author.id}): {error}")
    log_error(traceback.format_exc())
    log_acao("ERRO_COMANDO", f"cmd={cmd} user={ctx.author.id} error={error}")
    await ctx.reply("Deu um erro ao executar esse comando.")


async def main():
    log_acao("BOT_INICIANDO", "carregando banco e cogs")
    db.iniciar_banco()
    
    # Popular mundo automaticamente se ainda não foi populado
    if not mundo_esta_populado():
        popular_mundo_completo()
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                log_info(f"Cog carregada: {cog}")
            except Exception as e:
                log_error(f"Falha ao carregar cog {cog}: {e}")
                log_error(traceback.format_exc())
        await bot.start(TOKEN)


if __name__ == "__main__":
    if not TOKEN:
        log_error("DISCORD_TOKEN não encontrado. Configure o arquivo .env")
        raise RuntimeError("DISCORD_TOKEN não encontrado.")
    asyncio.run(main())
