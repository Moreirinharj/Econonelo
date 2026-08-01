import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
from services.relacionamento_service import (
    adicionar_amante, terminar_amante, verificar_descoberta, ver_amante
)
from services.acao_privada import registrar_acao_privada, gerar_mensagem_publica_neutra
import database as db


class Relacionamentos(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="adicionaramante", aliases=["amante"])
    async def adicionaramante_cmd(self, ctx: commands.Context, membro: discord.Member):
        """Adiciona um amante secreto (ação privada)."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        alvo = db.obter_personagem_ativo(str(membro.id))
        if not alvo:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo.", ephemeral=True))
            return
        
        resultado = adicionar_amante(personagem["id"], alvo["id"])
        
        if resultado["sucesso"]:
            acao_id = registrar_acao_privada(
                executor_id=ctx.author.id,
                vitima_id=membro.id,
                titulo="💕 Relacionamento Secreto",
                descricao_executor=f"Você iniciou um relacionamento secreto com **{membro.display_name}**!\n\n{resultado['msg']}",
                descricao_vitima=f"**{ctx.author.display_name}** te adicionou como amante!\n\n{resultado['msg']}"
            )
            
            embed_executor = discord.Embed(
                title="💕 Amante Adicionado (Privado)",
                description=f"Você iniciou um relacionamento secreto com **{membro.display_name}**!\n\n{resultado['msg']}",
                color=discord.Color.pink()
            )
            embed_executor.set_footer(text=f"ID: {acao_id}")
            
            await ctx.reply(embed=embed_executor, ephemeral=True)
            await ctx.send(gerar_mensagem_publica_neutra(membro.mention, acao_id))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True), ephemeral=True)

    @commands.command(name="terminaramante")
    async def terminaramante_cmd(self, ctx: commands.Context):
        """Termina o relacionamento com o amante."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        resultado = terminar_amante(personagem["id"])
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("💔 Amante terminado", resultado["msg"], ephemeral=True), ephemeral=True)
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True), ephemeral=True)

    @commands.command(name="veramante")
    async def veramante_cmd(self, ctx: commands.Context):
        """Mostra informações sobre teu amante."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        resultado = ver_amante(personagem["id"])
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_info("💕 Seu Amante", resultado["msg"], ephemeral=True), ephemeral=True)
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True), ephemeral=True)

    @commands.command(name="verificartraicao")
    async def verificartraicao_cmd(self, ctx: commands.Context):
        """Verifica se você foi descoberto traindo."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        resultado = verificar_descoberta(personagem["id"])
        
        if resultado.get("descoberto"):
            await ctx.reply(embed=embed_erro("🚨 TRAÍÇÃO DESCOBERTA!", resultado["msg"], ephemeral=True), ephemeral=True)
        else:
            if personagem.get("amante_id"):
                await ctx.reply(embed=embed_info("🤫 Tudo tranquilo", "Ninguém descobriu seu segredo ainda. Continua discreto!", ephemeral=True), ephemeral=True)
            else:
                await ctx.reply(embed=embed_info("👻 Sem segredos", "Você não tem nenhum amante no momento.", ephemeral=True), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Relacionamentos(bot))
