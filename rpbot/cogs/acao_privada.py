import discord
from discord.ext import commands

from services.acao_privada import obter_acao_privada
from utils.embeds import embed_info, embed_erro


class AcaoPrivada(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="veracao", aliases=["acao", "detalhes"])
    async def veracao_cmd(self, ctx: commands.Context, acao_id: str):
        """
        Vê detalhes de uma ação privada (só pra envolvidos).
        
        Uso: ?veracao <ID>
        Ex: ?veracao A3F9K2L1
        """
        resultado = obter_acao_privada(acao_id.upper(), ctx.author.id)
        
        if not resultado["sucesso"]:
            await ctx.reply(embed=embed_erro("Ação não encontrada", resultado["msg"], ephemeral=True), ephemeral=True)
            return
        
        # Monta embed com cores diferentes pra executor/vítima
        if resultado["papel"] == "executor":
            cor = discord.Color.orange()
            titulo = f"🔒 {resultado['titulo']} (Tu executou)"
        else:
            cor = discord.Color.red()
            titulo = f"🔔 {resultado['titulo']} (Tu foi alvo)"
        
        embed = discord.Embed(
            title=titulo,
            description=resultado["descricao"],
            color=cor
        )
        embed.set_footer(text=f"ID: {acao_id.upper()} • Essa mensagem é privada")
        
        await ctx.reply(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AcaoPrivada(bot))
