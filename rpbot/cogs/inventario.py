import discord
from discord.ext import commands

from data.constantes import (
    COR_PADRAO, COR_SUCESSO, COR_ERRO,
    MSG_SEM_PERSONAGEM,
)
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info
from services.personagem_service import obter_dados_personagem
from services.inventario_service import (
    dar_item, usar_item, obter_peso_maximo,
)
import database as db


class Inventario(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="inventario", aliases=["inv", "mochila"])
    async def inventario(self, ctx: commands.Context, tipo: str = None):
        """Mostra o inventário do personagem."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        itens = db.listar_inventario(personagem["id"], tipo)
        peso_atual = db.calcular_peso_total(personagem["id"])
        peso_max = obter_peso_maximo(personagem["id"])
        
        embed = embed_padrao(
            f"🎒 Inventário de {personagem['nome']}",
            cor=COR_PADRAO,
        )
        embed.add_field(
            name="⚖️ Peso",
            value=f"{peso_atual:.1f} / {peso_max:.1f} kg",
            inline=False,
        )
        
        if not itens:
            embed.description = "Seu inventário está vazio."
        else:
            itens_por_tipo = {}
            for item in itens:
                tipo = item["item_tipo"]
                if tipo not in itens_por_tipo:
                    itens_por_tipo[tipo] = []
                itens_por_tipo[tipo].append(item)
            
            emojis = {
                "comida": "🍔",
                "bebida": "🥤",
                "medicamento": "💊",
                "equipamento": "🔧",
                "documento": "📄",
                "chave": "🔑",
            }
            
            for tipo, lista_itens in itens_por_tipo.items():
                emoji = emojis.get(tipo, "📦")
                linhas = []
                for item in lista_itens:
                    equipado = " ⭐" if item["equipado"] else ""
                    linhas.append(f"• {item['item_nome']} x{item['quantidade']}{equipado} ({item['peso']}kg)")
                embed.add_field(
                    name=f"{emoji} {tipo.title()}",
                    value="\n".join(linhas),
                    inline=False,
                )
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="daritem")
    async def daritem(self, ctx: commands.Context, item_tipo: str, quantidade: int = 1):
        """Dá um item ao personagem (comando de teste)."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        resultado = dar_item(personagem["id"], item_tipo, quantidade)
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Item recebido", resultado["mensagem"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["mensagem"], ephemeral=True))

    @commands.command(name="usaritem")
    async def usaritem(self, ctx: commands.Context, item_id: int):
        """Usa um item do inventário."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        resultado = usar_item(personagem["id"], item_id)
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Item usado", resultado["mensagem"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["mensagem"], ephemeral=True))

    @commands.command(name="equipar")
    async def equipar(self, ctx: commands.Context, item_id: int):
        """Equipa um item."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        sucesso = db.equipar_item(personagem["id"], item_id)
        if sucesso:
            await ctx.reply(embed=embed_sucesso("Item equipado", "O item foi equipado com sucesso!", ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", "Item não encontrado.", ephemeral=True))

    @commands.command(name="desequipar")
    async def desequipar(self, ctx: commands.Context, item_id: int):
        """Desequipa um item."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        sucesso = db.desequipar_item(personagem["id"], item_id)
        if sucesso:
            await ctx.reply(embed=embed_sucesso("Item desequipado", "O item foi guardado na mochila.", ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", "Item não encontrado.", ephemeral=True))


async def setup(bot: commands.Bot):
    await bot.add_cog(Inventario(bot))
