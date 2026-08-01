import discord
from utils.horario import formatar_data_hora
from discord.ext import commands, tasks

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_INFO
from utils.embeds import embed_padrao, embed_sucesso, embed_info
from services.ia_mundo_service import avancar_dia_mundo
import database as db

class IAMundo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loop_mundo.start()

    def cog_unload(self):
        self.loop_mundo.cancel()

    @tasks.loop(hours=12) # Roda a cada 12 horas reais
    async def loop_mundo(self):
        """Loop automático que mantém o mundo vivo."""
        print("[IA MUNDO] Executando simulação diária...")
        resultado = avancar_dia_mundo()
        
        # Opcional: Enviar notícia em um canal específico de notícias se configurado
        # canal = self.bot.get_channel(CANAL_NOTICIAS_ID)
        # if canal:
        #     await canal.send(f"📰 **ÚLTIMA HORA:** {resultado['noticia']['titulo']}\n{resultado['noticia']['corpo']}")

    @loop_mundo.before_loop
    async def before_loop_mundo(self):
        await self.bot.wait_until_ready()

    @commands.command(name="mundo")
    async def mundo_cmd(self, ctx: commands.Context):
        """Mostra o estado atual do mundo."""
        dia = db.obter_estado_mundo("dia")
        clima = db.obter_estado_mundo("clima")
        inflacao = db.obter_estado_mundo("inflacao")
        
        emojis_clima = {
            "Ensolarado": "☀️", "Nublado": "☁️", "Chuvoso": "🌧️", "Frio": "❄️", "Tempestade": "⛈️"
        }
        emoji = emojis_clima.get(clima, "🌍")
        
        embed = embed_padrao("🌍 Estado do Mundo", cor=COR_PADRAO)
        embed.add_field(name="📅 Dia", value=f"Dia {dia}", inline=True)
        embed.add_field(name="🌤️ Clima", value=f"{emoji} {clima}", inline=True)
        embed.add_field(name="📈 Inflação", value=f"{inflacao}%", inline=True)
        
        embed.set_footer(text="O mundo continua vivo, mesmo quando você não está online.")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="noticias")
    async def noticias_cmd(self, ctx: commands.Context):
        """Mostra as últimas notícias geradas pela IA."""
        noticias = db.listar_noticias_recentes(5)
        if not noticias:
            await ctx.reply(embed=embed_info("📰 Sem notícias", "Nenhuma notícia foi gerada ainda.", ephemeral=True))
            return
        
        # ✅ CORREÇÃO: Paginação nas notícias
        embed = embed_padrao("📰 Últimas Notícias", cor=COR_INFO)
        for n in noticias[:10]:
            data = formatar_data_hora(n["criado_em"])
            embed.add_field(
                name=f"[{n['categoria'].upper()}] {n['titulo']} ({data})",
                value=n["corpo"][:200] + ("..." if len(n["corpo"]) > 200 else ""),
                inline=False
            )
        embed.set_footer(text=f"Mostrando {min(10, len(noticias))} de {len(noticias)} notícias")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="simulardia")
    @commands.has_permissions(administrator=True)
    async def simulardia_cmd(self, ctx: commands.Context):
        """Força a simulação de um dia (só admin)."""
        await ctx.reply("⏳ Processando simulação do mundo...", ephemeral=True)
        resultado = avancar_dia_mundo()
        
        embed = embed_sucesso("Dia Simulado com Sucesso", f"**Dia atual:** {resultado['dia']}\n**Clima:** {resultado['clima']}\n**Inflação:** {resultado['inflacao']}%")
        embed.add_field(
            name="📰 Última Notícia",
            value=f"**{resultado['noticia']['titulo']}**\n{resultado['noticia']['corpo']}",
            inline=False
        )
        if resultado["acoes_npcs"]:
            embed.add_field(
                name="🎭 Ações de NPCs",
                value="\n".join(f"• {a}" for a in resultado["acoes_npcs"]),
                inline=False
            )
        await ctx.reply(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(IAMundo(bot))
