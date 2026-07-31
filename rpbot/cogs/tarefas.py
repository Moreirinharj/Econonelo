import random
import time

import discord
from discord.ext import commands

import database as db
from utils import formatar_moeda
from data.config import PROFISSOES, COOLDOWN_TRABALHO


def formatar_tempo(segundos: int) -> str:
    minutos, seg = divmod(int(segundos), 60)
    horas, minutos = divmod(minutos, 60)
    if horas > 0:
        return f"{horas}h {minutos}min"
    return f"{minutos}min {seg}s"


class Tarefas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="trabalhar")
    async def trabalhar(self, ctx: commands.Context):
        personagem = db.pegar_personagem_ativo(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("Você precisa de um personagem ativo. Use `?jogar`.")
            return

        if not personagem["profissao"]:
            await ctx.reply("Você ainda não tem profissão. Use `?profissoes` e `?escolherprofissao`.")
            return

        info = PROFISSOES[personagem["profissao"]]
        if not info["tarefas"]:
            await ctx.reply(
                "Sua profissão ainda não tem tarefas automáticas implementadas "
                "(isso chega na Fase 2)."
            )
            return

        agora = time.time()
        tempo_restante = COOLDOWN_TRABALHO - (agora - personagem["ultimo_trabalho"])
        if tempo_restante > 0:
            await ctx.reply(f"⏳ Você está cansado. Descanse mais **{formatar_tempo(tempo_restante)}**.")
            return

        tarefa = random.choice(info["tarefas"])
        ganho = random.randint(tarefa["min"], tarefa["max"])

        # risco extra de algumas profissões (ex: motoboy)
        if "chance_acidente" in info and random.random() < info["chance_acidente"]:
            db.registrar_trabalho_personagem(personagem["id"], 0, 0)
            await ctx.reply(f"💥 Acidente na entrega! Você não ganhou nada dessa vez.")
            return

        resultado = db.registrar_trabalho_personagem(personagem["id"], ganho, tarefa["xp"])

        descricao = (
            f"{info['emoji']} Você fez: **{tarefa['nome']}**\n"
            f"💰 Ganhou **{formatar_moeda(ganho)}** (+{tarefa['xp']} XP)"
        )
        if resultado["subiu_nivel"]:
            descricao += f"\n🎉 Você subiu para o **nível {resultado['nivel']}**!"

        embed = discord.Embed(description=descricao, color=discord.Color.green())
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tarefas(bot))
