"""
Comando para criar personagem com CPF sequencial (001-999).
CPF é liberado quando o personagem morre.
"""
import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO
from utils.embeds import embed_padrao, embed_sucesso, embed_erro
import database as db


class CriarPersonagem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="criar")
    async def criar_cmd(self, ctx: commands.Context, nome: str, profissao: str = "desempregado"):
        """Cria um novo personagem com CPF sequencial."""
        # 1. Verificar se já tem personagem
        personagem_existente = db.obter_personagem_por_discord_id(str(ctx.author.id))
        if personagem_existente:
            await ctx.reply(embed=embed_erro(
                "Personagem já existe",
                f"Você já tem um personagem: **{personagem_existente['nome']}** (CPF: {personagem_existente['cpf']})\n\n"
                "Use `?perfil` para ver seus dados."
            ), ephemeral=True)
            return
        
        # 2. Gerar CPF sequencial (001-999)
        cpf = self._gerar_cpf_sequencial()
        if not cpf:
            await ctx.reply(embed=embed_erro(
                "Limite atingido",
                "Todos os 999 CPFs estão em uso. Aguarde alguém morrer para liberar um CPF."
            ), ephemeral=True)
            return
        
        # 3. Criar personagem
        personagem_id = db.criar_personagem(
            discord_id=str(ctx.author.id),
            nome=nome,
            cpf=cpf,
            profissao=profissao,
            saldo=1000,
            vida=100
        )
        
        if personagem_id:
            await ctx.reply(embed=embed_sucesso(
                "Personagem criado!",
                f"**Nome:** {nome}\n"
                f"**CPF:** {cpf}\n"
                f"**Profissão:** {profissao}\n"
                f"**Saldo inicial:** $1000\n"
                f"**Vida:** 100/100\n\n"
                f"Use `?perfil` para ver seus dados."
            ), ephemeral=True)
        else:
            await ctx.reply(embed=embed_erro("Erro ao criar", "Não foi possível criar o personagem."), ephemeral=True)

    def _gerar_cpf_sequencial(self) -> str:
        """Gera CPF sequencial de 001 a 999, pulando os que estão em uso."""
        # Buscar todos os CPFs em uso
        cpfs_em_uso = db.listar_cpfs_em_uso()
        
        # Tentar de 001 a 999
        for i in range(1, 1000):
            cpf = f"{i:03d}"
            if cpf not in cpfs_em_uso:
                return cpf
        
        return None  # Todos os 999 CPFs estão em uso


async def setup(bot: commands.Bot):
    await bot.add_cog(CriarPersonagem(bot))
