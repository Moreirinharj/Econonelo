"""
Comandos de profissão que ainda não existiam.
Todos vinculados ao CPF de 3 dígitos (000-999).
"""
import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_aviso
from utils.verificar_personagem import verificar_personagem, verificar_personagem_e_profissao
from utils.comando_ajuda import mostrar_ajuda_cpf, validar_cpf
import database as db


class ComandosFaltantes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ===== POLÍCIA MILITAR =====
    @commands.command(name="prender")
    async def prender_cmd(self, ctx: commands.Context, cpf_id: str = None):
        """Prende um suspeito identificado pelo CPF."""
        if cpf_id is None:
            await ctx.reply(embed=mostrar_ajuda_cpf(ctx, "?prender", "Prende um suspeito identificado pelo CPF."), ephemeral=True)
            return
        
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        personagem = await verificar_personagem_e_profissao(ctx, ["policial_militar"])
        if not personagem:
            return
        
        # Buscar suspeito pelo CPF
        suspeito = db.obter_personagem_por_cpf(cpf_id)
        if not suspeito:
            await ctx.reply(embed=embed_erro("Suspeito não encontrado", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        # Verificar se já está preso
        if suspeito.get('preso', False):
            await ctx.reply(embed=embed_aviso("Já está preso", f"O personagem de CPF {cpf_id} já está preso."), ephemeral=True)
            return
        
        # Prender
        db.prender_personagem(suspeito['id'])
        
        await ctx.reply(embed=embed_sucesso(
            "Suspeito preso!",
            f"Você prendeu **{suspeito['nome']}** (CPF: {cpf_id}).\n\n"
            f"Ele foi levado para a delegacia."
        ), ephemeral=True)

    # ===== POLÍCIA CIVIL =====
    @commands.command(name="interrogar")
    async def interrogar_cmd(self, ctx: commands.Context, cpf_id: str = None):
        """Interroga um suspeito identificado pelo CPF."""
        if cpf_id is None:
            await ctx.reply(embed=mostrar_ajuda_cpf(ctx, "?interrogar", "Interroga um suspeito."), ephemeral=True)
            return
        
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        personagem = await verificar_personagem_e_profissao(ctx, ["policial_civil"])
        if not personagem:
            return
        
        suspeito = db.obter_personagem_por_cpf(cpf_id)
        if not suspeito:
            await ctx.reply(embed=embed_erro("Suspeito não encontrado", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        await ctx.reply(embed=embed_sucesso(
            "Interrogatório realizado",
            f"Você interrogou **{suspeito['nome']}** (CPF: {cpf_id}).\n\n"
            f"Ele confessou o crime."
        ), ephemeral=True)

    @commands.command(name="periciar")
    async def periciar_cmd(self, ctx: commands.Context, local: str = None):
        """Realiza perícia em um local."""
        if local is None:
            await ctx.reply(embed=embed_aviso(
                "Uso do comando",
                "Use: `?periciar <local>`\n\n"
                "Exemplo: `?periciar rua principal`\n\n"
                "Realiza perícia técnica em um local de crime."
            ), ephemeral=True)
            return
        
        personagem = await verificar_personagem_e_profissao(ctx, ["policial_civil"])
        if not personagem:
            return
        
        await ctx.reply(embed=embed_sucesso(
            "Perícia realizada",
            f"Você realizou perícia em **{local}**.\n\n"
            f"Encontrou digitais e vestígios de pólvora."
        ), ephemeral=True)

    # ===== ADVOGADO =====
    @commands.command(name="processar")
    async def processar_cmd(self, ctx: commands.Context, cpf_id: str = None):
        """Abre um processo contra alguém."""
        if cpf_id is None:
            await ctx.reply(embed=mostrar_ajuda_cpf(ctx, "?processar", "Abre um processo judicial contra alguém."), ephemeral=True)
            return
        
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        personagem = await verificar_personagem_e_profissao(ctx, ["advogado", "advogado_criminal"])
        if not personagem:
            return
        
        reu = db.obter_personagem_por_cpf(cpf_id)
        if not reu:
            await ctx.reply(embed=embed_erro("Réu não encontrado", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        # Criar processo
        processo_id = db.criar_processo("civil", personagem['id'], reu['id'], f"Processo movido por {personagem['nome']}")
        
        await ctx.reply(embed=embed_sucesso(
            "Processo aberto!",
            f"Você abriu um processo contra **{reu['nome']}** (CPF: {cpf_id}).\n\n"
            f"ID do processo: {processo_id}"
        ), ephemeral=True)

    # ===== SAMU =====
    @commands.command(name="resgatar")
    async def resgatar_cmd(self, ctx: commands.Context, cpf_id: str = None):
        """Resgata um paciente identificado pelo CPF."""
        if cpf_id is None:
            await ctx.reply(embed=mostrar_ajuda_cpf(ctx, "?resgatar", "Resgata um paciente em emergência."), ephemeral=True)
            return
        
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        personagem = await verificar_personagem_e_profissao(ctx, ["samu"])
        if not personagem:
            return
        
        paciente = db.obter_personagem_por_cpf(cpf_id)
        if not paciente:
            await ctx.reply(embed=embed_erro("Paciente não encontrado", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        await ctx.reply(embed=embed_sucesso(
            "Resgate realizado!",
            f"Você resgatou **{paciente['nome']}** (CPF: {cpf_id}).\n\n"
            f"Ele foi levado ao hospital."
        ), ephemeral=True)

    @commands.command(name="transportar")
    async def transportar_cmd(self, ctx: commands.Context, hospital: str = None):
        """Transporta um paciente para o hospital."""
        if hospital is None:
            await ctx.reply(embed=embed_aviso(
                "Uso do comando",
                "Use: `?transportar <hospital>`\n\n"
                "Exemplo: `?transportar Hospital Geral`\n\n"
                "Transporta paciente para o hospital especificado."
            ), ephemeral=True)
            return
        
        personagem = await verificar_personagem_e_profissao(ctx, ["samu"])
        if not personagem:
            return
        
        await ctx.reply(embed=embed_sucesso(
            "Transporte realizado",
            f"Paciente transportado para **{hospital}**.\n\n"
            f"Ele está em cuidados médicos."
        ), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ComandosFaltantes(bot))
