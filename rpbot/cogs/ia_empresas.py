import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
import database as db


class IAEmpresas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="popularempresas")
    @commands.is_owner()
    async def popularempresas_cmd(self, ctx: commands.Context):
        """Popula o mundo com empresas reais (apenas owner)."""
        try:
            from services.empresa_service import popular_empresas
            resultado = popular_empresas()
            await ctx.reply(embed=embed_sucesso("✅ Empresas populadas", f"{resultado} empresas foram criadas/atualizadas."), ephemeral=True)
        except Exception as e:
            await ctx.reply(embed=embed_erro("Erro ao popular empresas", str(e)), ephemeral=True)

    @commands.command(name="simularempresas")
    @commands.is_owner()
    async def simularempresas_cmd(self, ctx: commands.Context):
        """Simula um dia de operação das empresas (apenas owner)."""
        try:
            from services.empresa_service import simular_dia_empresas
            resultado = simular_dia_empresas()
            await ctx.reply(embed=embed_sucesso("✅ Simulação concluída", f"Empresas processadas: {resultado}"), ephemeral=True)
        except Exception as e:
            await ctx.reply(embed=embed_erro("Erro na simulação", str(e)), ephemeral=True)

    @commands.command(name="gerarnoticiaempresa")
    @commands.is_owner()
    async def gerarnoticiaempresa_cmd(self, ctx: commands.Context):
        """Gera uma notícia aleatória sobre empresas (apenas owner)."""
        try:
            from services.empresa_service import gerar_noticia_empresa
            noticia = gerar_noticia_empresa()
            await ctx.reply(embed=embed_info("📰 Notícia Gerada", noticia), ephemeral=True)
        except Exception as e:
            await ctx.reply(embed=embed_erro("Erro ao gerar notícia", str(e)), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(IAEmpresas(bot))
