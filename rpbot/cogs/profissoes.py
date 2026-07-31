import discord
from discord.ext import commands

import database as db
from data.config import PROFISSOES, REQUISITO_TEXTO


class Profissoes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="profissoes")
    async def profissoes(self, ctx: commands.Context):
        embed = discord.Embed(title="📋 Profissões disponíveis", color=discord.Color.blurple())
        for chave, info in PROFISSOES.items():
            nome_bonito = chave.replace("_", " ").title()
            embed.add_field(
                name=f"{info['emoji']} {nome_bonito}",
                value=f"{info['descricao']}\n*Requisito:* {REQUISITO_TEXTO[info['requisito']]}",
                inline=False,
            )
        embed.set_footer(text="Use ?escolherprofissao <nome> (sem espaço, ex: jogador_futebol)")
        await ctx.reply(embed=embed)

    @commands.command(name="escolherprofissao")
    async def escolherprofissao(self, ctx: commands.Context, profissao: str = None):
        personagem = db.pegar_personagem_ativo(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("Você precisa de um personagem ativo. Use `?jogar`.")
            return

        if profissao is None or profissao.lower() not in PROFISSOES:
            opcoes = ", ".join(PROFISSOES.keys())
            await ctx.reply(f"Profissão inválida. Opções: {opcoes}")
            return

        profissao = profissao.lower()
        info = PROFISSOES[profissao]

        if info["requisito"] != "nenhum":
            await ctx.reply(
                f"⚠️ {REQUISITO_TEXTO[info['requisito']]} Esse fluxo ainda não está disponível "
                f"(chega na Fase 2, junto com concursos e faculdade)."
            )
            return

        db.definir_profissao_personagem(personagem["id"], profissao)
        nome_bonito = profissao.replace("_", " ").title()
        await ctx.reply(f"{info['emoji']} {personagem['nome']} agora é **{nome_bonito}**! Use `?trabalhar`.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Profissoes(bot))
