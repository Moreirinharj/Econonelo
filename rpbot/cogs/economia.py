import discord
from discord.ext import commands

import database as db
from utils import formatar_moeda


class Economia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="saldo")
    async def saldo(self, ctx: commands.Context):
        personagem = db.pegar_personagem_ativo(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("Você não tem um personagem ativo. Use `?jogar`.")
            return
        await ctx.reply(f"💰 {personagem['nome']} tem **{formatar_moeda(personagem['saldo'])}**.")

    @commands.command(name="pagar")
    async def pagar(self, ctx: commands.Context, membro: discord.Member = None, valor: int = None):
        if membro is None or valor is None:
            await ctx.reply("Use assim: `?pagar @usuario 100`")
            return
        if valor <= 0:
            await ctx.reply("O valor precisa ser positivo.")
            return
        if membro.id == ctx.author.id:
            await ctx.reply("Você não pode pagar a si mesmo.")
            return

        remetente = db.pegar_personagem_ativo(str(ctx.author.id))
        destinatario = db.pegar_personagem_ativo(str(membro.id))
        if remetente is None:
            await ctx.reply("Você não tem um personagem ativo.")
            return
        if destinatario is None:
            await ctx.reply(f"{membro.display_name} não tem um personagem ativo.")
            return
        if remetente["saldo"] < valor:
            await ctx.reply("Saldo insuficiente.")
            return

        db.atualizar_saldo_personagem(remetente["id"], -valor)
        db.atualizar_saldo_personagem(destinatario["id"], valor)

        await ctx.reply(
            f"💸 {remetente['nome']} pagou **{formatar_moeda(valor)}** para {destinatario['nome']}!"
        )

    @commands.command(name="ranking")
    async def ranking(self, ctx: commands.Context):
        top = db.top_saldos(10)
        if not top:
            await ctx.reply("Ainda não há personagens criados.")
            return

        linhas = [f"**{i}.** {p['nome']} — {formatar_moeda(p['saldo'])}" for i, p in enumerate(top, start=1)]
        embed = discord.Embed(
            title="🏆 Ranking de riqueza",
            description="\n".join(linhas),
            color=discord.Color.gold(),
        )
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Economia(bot))
