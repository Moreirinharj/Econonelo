import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info
from utils.admin_check import admin_only
from services.admin_service import (
    verificar_codigo, ativar_admin, desativar_admin,
    eh_admin, listar_admins
)
from utils.logger import log_acao


class AdminAtivacao(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ativaradmin", aliases=["admin", "viraradmin"])
    async def ativaradmin_cmd(self, ctx: commands.Context, *, codigo: str = None):
        """
        Ativa teu acesso admin com o código secreto.
        
        ⚠️ O código é confidencial — nunca compartilhe!
        """
        if not codigo:
            # Mensagem genérica — não revela que existe sistema de código
            await ctx.reply(
                embed=embed_erro(
                    "Acesso restrito",
                    "Esse comando requer um código de ativação especial.\n\n"
                    "💡 Se você recebeu um código, use: `?ativaradmin <código>`"
                , ephemeral=True),
                ephemeral=True
            )
            return
        
        # Log de tentativa (sem mostrar o código)
        log_acao("TENTATIVA_ATIVACAO", f"user={ctx.author.id} tamanho_codigo={len(codigo)}")
        
        # Verifica código
        if not verificar_codigo(codigo):
            # Log de falha
            log_acao("ATIVACAO_FALHOU", f"user={ctx.author.id}")
            
            # Mensagem genérica — não revela que o código estava errado
            await ctx.reply(
                embed=embed_erro(
                    "Acesso negado",
                    "Código inválido ou expirado.\n\n"
                    "🔒 Se você acredita que deveria ter acesso, contate o desenvolvedor."
                , ephemeral=True),
                ephemeral=True
            )
            return
        
        # Código correto — ativa admin
        resultado = ativar_admin(str(ctx.author.id))
        
        if resultado["sucesso"]:
            # Log de sucesso
            log_acao("ATIVACAO_SUCESSO", f"user={ctx.author.id} user_name={ctx.author.name}")
            
            await ctx.reply(embed=embed_sucesso("Admin Ativado!", resultado["msg"], ephemeral=True), ephemeral=True)
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True), ephemeral=True)

    @commands.command(name="adminhelp", aliases=["adminajuda", "cmdadmin"])
    @admin_only()
    async def adminhelp_cmd(self, ctx: commands.Context):
        """Mostra comandos administrativos disponíveis."""
        embed = embed_padrao("🔑 Comandos Administrativos", cor=COR_PADRAO)
        embed.description = "Aqui estão os comandos exclusivos pra admins:"
        
        embed.add_field(
            name="🏢 Empresas",
            value="`?popularempresas` `?simularempresas` `?gerarnoticiaempresa`",
            inline=False
        )
        
        embed.add_field(
            name="🎓 Educação",
            value="`?populacursos`",
            inline=False
        )
        
        embed.add_field(
            name="📋 Concursos",
            value="`?abrirconcursos [quantidade]`",
            inline=False
        )
        
        embed.add_field(
            name="🌤️ Clima",
            value="`?forcartempo <clima>` `?simularclima`",
            inline=False
        )
        
        embed.add_field(
            name="💀 Personagens",
            value="`?matarpersonagem <id> <causa>` `?buscarcpf <cpf>` `?cpfsdisponiveis`",
            inline=False
        )
        
        embed.add_field(
            name="🔑 Admin",
            value="`?adminlist` `?desativaradmin <@user>`",
            inline=False
        )
        
        embed.set_footer(text="Esses comandos são exclusivos pra admins")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="adminlist", aliases=["listadmins", "admins"])
    @admin_only()
    async def adminlist_cmd(self, ctx: commands.Context):
        """Lista todos os admins ativos (só admin vê)."""
        admins = listar_admins()
        
        if not admins:
            await ctx.reply(embed=embed_info("🔑 Sem admins", "Nenhum admin ativo no momento.", ephemeral=True), ephemeral=True)
            return
        
        embed = embed_padrao("🔑 Admins Ativos", cor=COR_PADRAO)
        
        for i, admin in enumerate(admins, 1):
            try:
                user = await self.bot.fetch_user(int(admin["user_id"]))
                nome = f"{user.name}#{user.discriminator}" if user.discriminator != "0" else user.name
            except:
                nome = f"ID: {admin['user_id']}"
            
            from utils.horario import formatar_data_hora
            data = formatar_data_hora(admin["ativado_em"])
            
            embed.add_field(
                name=f"{i}. {nome}",
                value=f"**ID:** `{admin['user_id']}`\n**Ativado em:** {data}",
                inline=True
            )
        
        embed.set_footer(text=f"Total: {len(admins)} admin(s)")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="desativaradmin")
    @admin_only()
    async def desativaradmin_cmd(self, ctx: commands.Context, membro: discord.Member):
        """Desativa um admin (só admin pode usar)."""
        if str(membro.id) == str(ctx.author.id):
            await ctx.reply(embed=embed_erro("Erro", "Você não pode desativar a si mesmo!", ephemeral=True), ephemeral=True)
            return
        
        resultado = desativar_admin(str(membro.id))
        
        if resultado["sucesso"]:
            await ctx.reply(
                embed=embed_sucesso("Admin Desativado", f"O admin {membro.mention} foi desativado.", ephemeral=True),
                ephemeral=True
            )
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminAtivacao(bot))
