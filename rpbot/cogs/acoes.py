import discord
from discord.ext import commands

from data.constantes import COR_SUCESSO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_sucesso, embed_erro
from services.personagem_service import obter_dados_personagem
from services.status_service import comer, dormir, tomar_banho, relaxar, verificar_status_criticos
from services.mensagens_service import mensagem_status_baixo


class Acoes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="comer")
    async def comer_cmd(self, ctx: commands.Context):
        """Come e recupera fome."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.")
            return
        
        if personagem.get("fome", 100) >= 100:
            await ctx.reply(embed=embed_erro("Tá de barriga cheia!", "Não precisa comer agora, parceiro. 🍔"))
            return
        
        resultado = comer(personagem["id"])
        await ctx.reply(embed=embed_sucesso("🍔 Encheu a pança!", resultado["mensagem"]))

    @commands.command(name="dormir")
    async def dormir_cmd(self, ctx: commands.Context, horas: int = 8):
        """Dorme e recupera energia (padrão: 8h)."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.")
            return
        
        if horas < 1 or horas > 12:
            await ctx.reply(embed=embed_erro("Horas inválidas", "Escolhe entre 1 e 12 horas, parceiro."))
            return
        
        if personagem.get("energia", 100) >= 100:
            await ctx.reply(embed=embed_erro("Tá cheio de energia!", "Não tá cansado, mano. Vai trabalhar! 💪"))
            return
        
        resultado = dormir(personagem["id"], horas)
        await ctx.reply(embed=embed_sucesso("💤 Dormiu que uma beleza!", resultado["mensagem"]))

    @commands.command(name="banho", aliases=["banhar"])
    async def banho_cmd(self, ctx: commands.Context):
        """Toma banho e recupera higiene."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.")
            return
        
        if personagem.get("higiene", 100) >= 100:
            await ctx.reply(embed=embed_erro("Já tá limpinho!", "Cheiroso que nem sabão, parceiro. 🧼"))
            return
        
        resultado = tomar_banho(personagem["id"])
        await ctx.reply(embed=embed_sucesso("🚿 Banho tomado!", resultado["mensagem"]))

    @commands.command(name="relaxar")
    async def relaxar_cmd(self, ctx: commands.Context):
        """Relaxa e reduz estresse."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.")
            return
        
        if personagem.get("estresse", 0) <= 0:
            await ctx.reply(embed=embed_erro("Tá relax já!", "Zen que nem monge, parceiro. 🧘"))
            return
        
        resultado = relaxar(personagem["id"])
        await ctx.reply(embed=embed_sucesso("😌 Relaxou geral!", resultado["mensagem"]))

    @commands.command(name="verificar")
    async def verificar_cmd(self, ctx: commands.Context):
        """Verifica se há status críticos e dá dicas."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.")
            return
        
        criticos = verificar_status_criticos(personagem["id"])
        
        if not criticos:
            await ctx.reply(embed=embed_sucesso("✅ Tudo em cima!", "Tu tá de boa, parceiro. Continua assim! 💪"))
            return
        
        nomes = {
            "saude": "❤️ Saúde",
            "energia": "⚡ Energia",
            "fome": "🍔 Fome",
        }
        
        lista = "\n".join(f"• {nomes.get(c, c)}" for c in criticos)
        dica = mensagem_status_baixo(personagem)
        await ctx.reply(embed=embed_erro("⚠️ Status críticos!", f"Tu precisa cuidar de:\n{lista}\n\n{dica}"))


async def setup(bot: commands.Bot):
    await bot.add_cog(Acoes(bot))
