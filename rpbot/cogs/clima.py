import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.clima_service import obter_clima_atual, forcar_clima, avancar_clima
import database as db


class Clima(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="clima", aliases=["tempo", "previsao"])
    async def clima_cmd(self, ctx: commands.Context):
        """Mostra a previsão do tempo atual e seus efeitos."""
        clima = obter_clima_atual()
        
        # Monta texto de efeitos
        efeitos = []
        if clima["mod_energia"] < 0:
            efeitos.append(f"⚡ Energia drena **{-clima['mod_energia']}% a mais** por hora")
        if clima["mod_fome"] > 0:
            efeitos.append(f"🍔 Fome aumenta **+{clima['mod_fome']}** por hora")
        if clima["mod_motoboy"] > 1.0:
            efeitos.append(f"🛵 Motoboys ganham **+{int((clima['mod_motoboy']-1)*100)}% de bônus** nas entregas!")
        elif clima["mod_motoboy"] < 1.0:
            efeitos.append(f"🛵 Motoboys ganham **-{int((1-clima['mod_motoboy'])*100)}% nas entregas** (menos pedidos)")
        
        if not efeitos:
            efeitos.append("✅ Clima estável. Sem modificadores de status.")
        
        embed = embed_padrao(f"{clima['emoji']} Previsão do Tempo", cor=COR_PADRAO)
        embed.add_field(name="🌡️ Temperatura", value=f"{clima['temperatura']}°C", inline=True)
        embed.add_field(name="📅 Estação", value=clima["estacao"], inline=True)
        embed.add_field(name="🌤️ Condição", value=clima["nome"], inline=True)
        
        embed.add_field(
            name="📝 Descrição",
            value=clima["descricao"],
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Efeitos no Gameplay",
            value="\n".join(efeitos),
            inline=False
        )
        
        embed.set_footer(text="O clima muda automaticamente e afeta tua sobrevivência!")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="forcartempo")
    @commands.has_permissions(administrator=True)
    async def forcartempo_cmd(self, ctx: commands.Context, clima: str):
        """Força um clima específico (só admin)."""
        resultado = forcar_clima(clima.capitalize())
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Clima Alterado", resultado["msg"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))

    @commands.command(name="simularclima")
    @commands.has_permissions(administrator=True)
    async def simularclima_cmd(self, ctx: commands.Context):
        """Força a mudança de clima/estação (só admin)."""
        resultado = avancar_clima()
        clima_atual = obter_clima_atual()
        
        if resultado["mudou"]:
            await ctx.reply(embed=embed_sucesso(
                "Clima Avançado",
                f"O tempo mudou para **{clima_atual['nome']}** {clima_atual['emoji']} ({clima_atual['temperatura']}°C, ephemeral=True)\n"
                f"Estação atual: **{clima_atual['estacao']}**"
            ))
        else:
            await ctx.reply(embed=embed_info(
                "Clima Estável",
                f"O clima continua o mesmo: **{clima_atual['nome']}** {clima_atual['emoji']}"
            , ephemeral=True))


async def setup(bot: commands.Bot):
    await bot.add_cog(Clima(bot))
