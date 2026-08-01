"""
Comandos de interação social entre personagens.
Todos vinculados ao CPF de 3 dígitos (000-999).
"""
import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_aviso
from utils.verificar_personagem import verificar_personagem
from utils.comando_ajuda import mostrar_ajuda_cpf, validar_cpf
import database as db


class InteracoesSociais(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="atacar")
    async def atacar_cmd(self, ctx: commands.Context, cpf_id: str = None):
        """Ataca outro personagem."""
        if cpf_id is None:
            await ctx.reply(embed=mostrar_ajuda_cpf(ctx, "?atacar", "Ataca outro personagem."), ephemeral=True)
            return
        
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        personagem = await verificar_personagem(ctx)
        if not personagem:
            return
        
        alvo = db.obter_personagem_por_cpf(cpf_id)
        if not alvo:
            await ctx.reply(embed=embed_erro("Alvo não encontrado", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        if alvo['id'] == personagem['id']:
            await ctx.reply(embed=embed_erro("Auto-ataque", "Você não pode atacar a si mesmo!"), ephemeral=True)
            return
        
        await ctx.reply(embed=embed_sucesso(
            "Ataque realizado!",
            f"Você atacou **{alvo['nome']}** (CPF: {cpf_id})."
        ), ephemeral=True)

    @commands.command(name="ajudar")
    async def ajudar_cmd(self, ctx: commands.Context, cpf_id: str = None):
        """Ajuda outro personagem."""
        if cpf_id is None:
            await ctx.reply(embed=mostrar_ajuda_cpf(ctx, "?ajudar", "Ajuda outro personagem."), ephemeral=True)
            return
        
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        personagem = await verificar_personagem(ctx)
        if not personagem:
            return
        
        alvo = db.obter_personagem_por_cpf(cpf_id)
        if not alvo:
            await ctx.reply(embed=embed_erro("Alvo não encontrado", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        await ctx.reply(embed=embed_sucesso(
            "Ajuda oferecida!",
            f"Você ajudou **{alvo['nome']}** (CPF: {cpf_id})."
        ), ephemeral=True)

    @commands.command(name="transferir")
    async def transferir_cmd(self, ctx: commands.Context, cpf_id: str = None, valor: float = None):
        """Transferir dinheiro para outro personagem."""
        if cpf_id is None or valor is None:
            await ctx.reply(embed=embed_aviso(
                "Uso do comando",
                "Use: `?transferir <cpf/id> <valor>`\n\n"
                "Exemplo: `?transferir 123 500`\n\n"
                "Transfere dinheiro para outro personagem."
            ), ephemeral=True)
            return
        
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        personagem = await verificar_personagem(ctx)
        if not personagem:
            return
        
        alvo = db.obter_personagem_por_cpf(cpf_id)
        if not alvo:
            await ctx.reply(embed=embed_erro("Alvo não encontrado", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        if personagem['saldo'] < valor:
            await ctx.reply(embed=embed_erro("Saldo insuficiente", f"Você só tem ${personagem['saldo']}."), ephemeral=True)
            return
        
        db.atualizar_saldo_personagem(personagem['id'], -valor)
        db.atualizar_saldo_personagem(alvo['id'], valor)
        
        await ctx.reply(embed=embed_sucesso(
            "Transferência realizada!",
            f"Você transferiu **${valor}** para **{alvo['nome']}** (CPF: {cpf_id})."
        ), ephemeral=True)

    @commands.command(name="doar")
    async def doar_cmd(self, ctx: commands.Context, cpf_id: str = None, valor: float = None):
        """Doa dinheiro para outro personagem."""
        if cpf_id is None or valor is None:
            await ctx.reply(embed=embed_aviso(
                "Uso do comando",
                "Use: `?doar <cpf/id> <valor>`\n\n"
                "Exemplo: `?doar 123 100`"
            ), ephemeral=True)
            return
        
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        personagem = await verificar_personagem(ctx)
        if not personagem:
            return
        
        alvo = db.obter_personagem_por_cpf(cpf_id)
        if not alvo:
            await ctx.reply(embed=embed_erro("Alvo não encontrado", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        if personagem['saldo'] < valor:
            await ctx.reply(embed=embed_erro("Saldo insuficiente", f"Você só tem ${personagem['saldo']}."), ephemeral=True)
            return
        
        db.atualizar_saldo_personagem(personagem['id'], -valor)
        db.atualizar_saldo_personagem(alvo['id'], valor)
        
        await ctx.reply(embed=embed_sucesso(
            "Doação realizada!",
            f"Você doou **${valor}** para **{alvo['nome']}** (CPF: {cpf_id})."
        ), ephemeral=True)

    @commands.command(name="subornar")
    async def subornar_cmd(self, ctx: commands.Context, cpf_id: str = None, valor: float = None):
        """Tenta subornar outro personagem."""
        if cpf_id is None or valor is None:
            await ctx.reply(embed=embed_aviso(
                "Uso do comando",
                "Use: `?subornar <cpf/id> <valor>`\n\n"
                "Exemplo: `?subornar 123 1000`"
            ), ephemeral=True)
            return
        
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        personagem = await verificar_personagem(ctx)
        if not personagem:
            return
        
        alvo = db.obter_personagem_por_cpf(cpf_id)
        if not alvo:
            await ctx.reply(embed=embed_erro("Alvo não encontrado", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        if personagem['saldo'] < valor:
            await ctx.reply(embed=embed_erro("Saldo insuficiente", f"Você só tem ${personagem['saldo']}."), ephemeral=True)
            return
        
        db.atualizar_saldo_personagem(personagem['id'], -valor)
        db.atualizar_saldo_personagem(alvo['id'], valor)
        
        await ctx.reply(embed=embed_sucesso(
            "Suborno realizado!",
            f"Você subornou **{alvo['nome']}** (CPF: {cpf_id}) com **${valor}**."
        ), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(InteracoesSociais(bot))
