import discord
from discord.ext import commands

from data.constantes import (
    COR_PADRAO, COR_SUCESSO, COR_ERRO,
    MSG_SEM_PERSONAGEM,
)
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info
from services.personagem_service import obter_dados_personagem
from services.npc_service import (
    criar_npc_aleatorio, popular_cidade, conversar_com_npc,
    dar_dinheiro_para_npc,
)
import database as db


def barra_humor(valor: int) -> str:
    """Cria barra visual de humor."""
    preenchido = int((valor / 100) * 10)
    vazio = 10 - preenchido
    
    if valor >= 70:
        emoji = "😊"
    elif valor >= 40:
        emoji = "😐"
    else:
        emoji = "😠"
    
    return f"{emoji} {'█' * preenchido}{'░' * vazio} {valor}/100"


class NPCs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="npcs")
    async def npcs_cmd(self, ctx: commands.Context, cidade: str = None):
        """Lista NPCs de uma cidade."""
        npcs = db.listar_npcs(cidade=cidade, limite=10)
        
        if not npcs:
            await ctx.reply(embed=embed_erro("Nenhum NPC encontrado", "Tente popular uma cidade primeiro.", ephemeral=True))
            return
        
        embed = embed_padrao(f"👥 NPCs{' em ' + cidade if cidade else ''}", cor=COR_PADRAO)
        
        for npc in npcs[:10]:
            humor_barra = barra_humor(npc["humor"])
            embed.add_field(
                name=f"{npc['nome']} (ID: {npc['id']})",
                value=f"**Profissão:** {npc['profissao']}\n**Cidade:** {npc['cidade']}\n**Humor:** {humor_barra}",
                inline=True,
            )
        
        embed.set_footer(text=f"Total: {db.contar_npcs()} NPCs ativos")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="npc")
    async def npc_cmd(self, ctx: commands.Context, npc_id: int):
        """Mostra detalhes de um NPC específico."""
        npc = db.obter_npc(npc_id)
        if npc is None:
            await ctx.reply(embed=embed_erro("NPC não encontrado", ephemeral=True))
            return
        
        humor_barra = barra_humor(npc["humor"])
        
        embed = embed_info(
            f"👤 {npc['nome']}",
            f"**ID:** {npc['id']}\n"
            f"**Idade:** {npc['idade']} anos\n"
            f"**Profissão:** {npc['profissao']}\n"
            f"**Cidade:** {npc['cidade']}\n"
            f"**Dinheiro:** ${npc['dinheiro']}\n"
            f"**Personalidade:** {npc['personalidade']}\n"
            f"**Humor:** {humor_barra}"
        )
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="conversar")
    async def conversar_cmd(self, ctx: commands.Context, npc_id: int):
        """Conversa com um NPC."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        resultado = conversar_com_npc(npc_id)
        if not resultado["sucesso"]:
            await ctx.reply(embed=embed_erro("Erro", resultado["mensagem"], ephemeral=True))
            return
        
        npc = resultado["npc"]
        await ctx.reply(embed=embed_info(
            f"💬 Conversa com {npc['nome']}",
            f"**{npc['nome']}:** {resultado['resposta']}\n\n"
            f"*Humor: {barra_humor(npc['humor'], ephemeral=True)}*"
        ))

    @commands.command(name="darnpc")
    async def darnpc_cmd(self, ctx: commands.Context, npc_id: int, valor: int):
        """Dá dinheiro pra um NPC (melhora humor)."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        if personagem["saldo"] < valor:
            await ctx.reply(embed=embed_erro("Saldo insuficiente", "Você não tem dinheiro suficiente no bolso.", ephemeral=True))
            return
        
        db.atualizar_saldo_personagem(personagem["id"], -valor)
        resultado = dar_dinheiro_para_npc(npc_id, valor)
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Dinheiro dado", resultado["mensagem"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["mensagem"], ephemeral=True))

    @commands.command(name="populacidade")
    @commands.has_permissions(administrator=True)
    async def populacidade_cmd(self, ctx: commands.Context, cidade: str, quantidade: int = 20):
        """Popula uma cidade com NPCs (só admin)."""
        if quantidade > 100:
            await ctx.reply(embed=embed_erro("Limite", "Máximo 100 NPCs por vez.", ephemeral=True))
            return
        
        ids = popular_cidade(cidade, quantidade)
        await ctx.reply(embed=embed_sucesso(
            "Cidade populada",
            f"{quantidade} NPCs foram criados em {cidade}!"
        , ephemeral=True))

    @commands.command(name="criarnpc")
    @commands.has_permissions(administrator=True)
    async def criarnpc_cmd(self, ctx: commands.Context, *, cidade: str = None):
        """Cria um NPC aleatório (só admin)."""
        npc_id = criar_npc_aleatorio(cidade)
        npc = db.obter_npc(npc_id)
        await ctx.reply(embed=embed_sucesso(
            "NPC criado",
            f"**{npc['nome']}** (ID: {npc_id}, ephemeral=True)\n"
            f"Profissão: {npc['profissao']}\n"
            f"Cidade: {npc['cidade']}"
        ))


async def setup(bot: commands.Bot):
    await bot.add_cog(NPCs(bot))
