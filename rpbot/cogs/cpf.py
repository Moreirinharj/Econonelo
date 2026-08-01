import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.comando_ajuda import mostrar_ajuda_cpf, mostrar_ajuda_pedido, validar_cpf
from utils.comando_ajuda import mostrar_ajuda_cpf, validar_cpf
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
from services.cpf_service import (
    obter_cpf_personagem, buscar_personagem_por_cpf,
    investigar_cpf, matar_personagem
)
import database as db


class CPF(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="meucpf", aliases=["cpf"])
    async def meucpf_cmd(self, ctx: commands.Context):
        """Mostra teu CPF."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        cpf = obter_cpf_personagem(personagem["id"])
        
        if cpf:
            await ctx.reply(embed=embed_info(
                "🆔 Seu CPF",
                f"**CPF:** `{cpf}`\n\n"
                f"⚠️ **IMPORTANTE:** Guarde esse número! Autoridades e médicos podem investigar seu CPF.\n"
                f"Se você morrer, seu CPF será liberado e poderá ser usado por outro personagem."
            , ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", "Não foi possível gerar seu CPF. Tenta de novo.", ephemeral=True))

    @commands.command(name="investigar")
    async def investigar_cmd(self, ctx: commands.Context, cpf: str):
        """Investiga um CPF (só autoridades e médicos)."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        resultado = investigar_cpf(cpf, personagem["id"])
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("🔍 Investigação Concluída", resultado["msg"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))

    @commands.command(name="matarpersonagem")
    @commands.has_permissions(administrator=True)
    @commands.command(name="matarpersonagem")
    @commands.has_permissions(administrator=True)
    async def matarpersonagem_cmd(self, ctx: commands.Context, cpf_id: str = None, *, causa: str = "Desconhecida"):
        """Mata um personagem (apenas admin)."""
        # 1. Mostrar ajuda se não passar o CPF
        if cpf_id is None:
            await ctx.reply(embed=mostrar_ajuda_cpf(ctx, "?matarpersonagem", "Mata um personagem (apenas admin)."), ephemeral=True)
            return
        
        # 2. Validar CPF
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        # 3. Buscar personagem pelo CPF
        personagem = db.obter_personagem_por_cpf(cpf_id)
        if not personagem:
            await ctx.reply(embed=embed_erro("Personagem não encontrado", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        # 4. Matar personagem (vida = 0)
        db.atualizar_vida_personagem(personagem['id'], 0)
        
        await ctx.reply(embed=embed_sucesso(
            "Personagem morto!",
            f"**{personagem['nome']}** (CPF: {cpf_id}) morreu.\nCausa: {causa}"
        ), ephemeral=True)

    @commands.command(name="buscarcpf")
    @commands.has_permissions(administrator=True)
    async def buscarcpf_cmd(self, ctx: commands.Context, cpf: str):
        """Busca personagem pelo CPF (só admin)."""
        personagem = buscar_personagem_por_cpf(cpf)
        
        if not personagem:
            await ctx.reply(embed=embed_erro("Erro", "CPF não encontrado ou já foi liberado.", ephemeral=True))
            return
        
        embed = embed_padrao(f"🔍 Personagem com CPF {cpf}", cor=COR_PADRAO)
        embed.add_field(name="Nome", value=personagem["nome"], inline=True)
        embed.add_field(name="ID", value=str(personagem["id"]), inline=True)
        embed.add_field(name="Vivo", value="🟢 Sim" if personagem.get("vivo", 1) else "💀 Não", inline=True)
        embed.add_field(name="Profissão", value=personagem.get("profissao", "Desempregado"), inline=True)
        embed.add_field(name="Nível", value=str(personagem.get("nivel", 1)), inline=True)
        embed.add_field(name="Saldo", value=f"${personagem.get('saldo', 0)}", inline=True)
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="cpfsdisponiveis")
    @commands.has_permissions(administrator=True)
    async def cpfsdisponiveis_cmd(self, ctx: commands.Context):
        """Mostra quantos CPFs estão disponíveis (só admin)."""
        conn = db.conectar()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as total FROM personagens WHERE cpf IS NOT NULL")
        total = cur.fetchone()["total"]
        conn.close()
        
        disponiveis = 1000 - total
        
        await ctx.reply(embed=embed_info(
            "🆔 CPFs Disponíveis",
            f"**Em uso:** {total}/1000\n"
            f"**Disponíveis:** {disponiveis}/1000"
        , ephemeral=True))


async def setup(bot: commands.Bot):
    await bot.add_cog(CPF(bot))
