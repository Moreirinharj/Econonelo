import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

import database as db
from data.config import PREFIXO

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
    "cogs.profissoes",
    "cogs.tarefas",
    "cogs.economia",
    "cogs.eventos",
]


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    print(f"Prefixo ativo: {PREFIXO}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("Você não tem permissão pra usar esse comando.")
        return
    if isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
        await ctx.reply("Não encontrei esse usuário. Marque com @ ou use o ID correto.")
        return
    print(f"Erro no comando {ctx.command}: {error}")
    await ctx.reply("Deu um erro ao executar esse comando.")


async def main():
    db.iniciar_banco()
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
        await bot.start(TOKEN)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN não encontrado. Configure o arquivo .env")
    asyncio.run(main())
