import discord
from discord.ext import commands

from data.constantes import (
    COR_PADRAO, COR_SUCESSO, COR_ERRO, MSG_SEM_PERSONAGEM,
    NOMES_GENERO, NOMES_SEXUALIDADE, NOMES_PRONOMES,
)
from utils.embeds import embed_padrao, embed_erro, embed_info
from services.personagem_service import obter_dados_personagem


def barra_status(valor: int, maximo: int = 100, tamanho: int = 10) -> str:
    """Cria uma barra visual de status."""
    preenchido = int((valor / maximo) * tamanho)
    vazio = tamanho - preenchido
    
    if valor >= 70:
        emoji = "🟢"
    elif valor >= 40:
        emoji = "🟡"
    else:
        emoji = "🔴"
    
    return f"{emoji} {'█' * preenchido}{'░' * vazio} {valor}/{maximo}"


class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="status", aliases=["stats"])
    async def status(self, ctx: commands.Context):
        """Mostra todos os status do personagem ativo."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return

        embed = embed_padrao(
            f"📊 Status de {personagem['nome']}",
            cor=COR_PADRAO,
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        embed.add_field(name="❤️ Saúde", value=barra_status(personagem.get("saude", 100)), inline=True)
        embed.add_field(name="⚡ Energia", value=barra_status(personagem.get("energia", 100)), inline=True)
        embed.add_field(name="🍔 Fome", value=barra_status(personagem.get("fome", 100)), inline=True)
        embed.add_field(name="😊 Felicidade", value=barra_status(personagem.get("felicidade", 100)), inline=True)
        embed.add_field(name="😰 Estresse", value=barra_status(personagem.get("estresse", 0)), inline=True)
        embed.add_field(name="🚿 Higiene", value=barra_status(personagem.get("higiene", 100)), inline=True)
        embed.add_field(name="⭐ Reputação", value=barra_status(personagem.get("reputacao", 50)), inline=True)
        
        escolaridade = personagem.get("escolaridade", "nenhuma")
        escolaridade_bonito = {
            "nenhuma": "Sem escolaridade",
            "fundamental": "Ensino Fundamental",
            "medio": "Ensino Médio",
            "superior": "Ensino Superior",
            "pos": "Pós-Graduação",
        }.get(escolaridade, escolaridade)
        
        embed.add_field(name="🎓 Escolaridade", value=escolaridade_bonito, inline=True)
        
        ficha = personagem.get("ficha_criminal", "limpa")
        if ficha == "limpa":
            ficha_texto = "✅ Limpa"
        else:
            crimes = ficha.split("|")
            ficha_texto = f"❌ {len(crimes)} registro(s)"
        
        embed.add_field(name="📋 Ficha Criminal", value=ficha_texto, inline=True)
        
        # ✅ CORREÇÃO: Mostra data de nascimento
        data_nasc = personagem.get("data_nascimento")
        if data_nasc:
            embed.add_field(name="🎂 Nascimento", value=data_nasc, inline=True)
        
        objetivos = personagem.get("objetivos")
        if objetivos:
            embed.add_field(
                name="🎯 Objetivos",
                value=objetivos[:200] + ("..." if len(objetivos) > 200 else ""),
                inline=False,
            )
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="saude", aliases=["hp", "vida"])
    async def saude(self, ctx: commands.Context):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        valor = personagem.get("saude", 100)
        await ctx.reply(embed=embed_info("❤️ Saúde", barra_status(valor, ephemeral=True)))

    @commands.command(name="energia")
    async def energia(self, ctx: commands.Context):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        valor = personagem.get("energia", 100)
        await ctx.reply(embed=embed_info("⚡ Energia", barra_status(valor, ephemeral=True)))

    @commands.command(name="fome")
    async def fome(self, ctx: commands.Context):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        valor = personagem.get("fome", 100)
        await ctx.reply(embed=embed_info("🍔 Fome", barra_status(valor, ephemeral=True)))

    @commands.command(name="felicidade", aliases=["feliz"])
    async def felicidade(self, ctx: commands.Context):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        valor = personagem.get("felicidade", 100)
        await ctx.reply(embed=embed_info("😊 Felicidade", barra_status(valor, ephemeral=True)))

    @commands.command(name="estresse")
    async def estresse(self, ctx: commands.Context):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        valor = personagem.get("estresse", 0)
        await ctx.reply(embed=embed_info("😰 Estresse", barra_status(valor, ephemeral=True)))

    @commands.command(name="higiene")
    async def higiene(self, ctx: commands.Context):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        valor = personagem.get("higiene", 100)
        await ctx.reply(embed=embed_info("🚿 Higiene", barra_status(valor, ephemeral=True)))

    @commands.command(name="reputacao", aliases=["rep"])
    async def reputacao(self, ctx: commands.Context):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        valor = personagem.get("reputacao", 50)
        await ctx.reply(embed=embed_info("⭐ Reputação", barra_status(valor, ephemeral=True)))

    @commands.command(name="ficha")
    async def ficha(self, ctx: commands.Context):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        ficha = personagem.get("ficha_criminal", "limpa")
        if ficha == "limpa":
            texto = "✅ Sua ficha está limpa!"
        else:
            crimes = ficha.split("|")
            lista = "\n".join(f"• {crime}" for crime in crimes)
            texto = f"❌ **Registros criminais:**\n{lista}"
        
        await ctx.reply(embed=embed_info("📋 Ficha Criminal", texto, ephemeral=True))

    @commands.command(name="objetivos", aliases=["objetivo"])
    async def objetivos(self, ctx: commands.Context, *, texto: str = None):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        if texto is None:
            objetivos = personagem.get("objetivos")
            if objetivos:
                await ctx.reply(embed=embed_info("🎯 Objetivos de Vida", objetivos, ephemeral=True))
            else:
                await ctx.reply(embed=embed_erro("Sem objetivos", "Use `?objetivos <texto>` pra definir seus objetivos.", ephemeral=True))
            return
        
        import database as db
        db.atualizar_objetivos(personagem["id"], texto)
        await ctx.reply(embed=embed_info("✅ Objetivos atualizados", texto, ephemeral=True))


async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
