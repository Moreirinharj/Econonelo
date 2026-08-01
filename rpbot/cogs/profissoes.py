import os
import json
import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_erro, embed_aviso
from services.personagem_service import obter_dados_personagem
import database as db


class Profissoes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _mostrar_profissao(self, ctx: commands.Context, profissao_id: str):
        """Mostra informações sobre uma profissão."""
        conn = db.conectar()
        cur = conn.cursor()
        cur.execute("SELECT * FROM profissoes_info WHERE id = ?", (profissao_id,))
        row = cur.fetchone()
        conn.close()
        
        if not row:
            await ctx.reply(embed=embed_erro("Profissão não encontrada", f"A profissão '{profissao_id}' não existe."), ephemeral=True)
            return
        
        prof = dict(row)
        
        # Criar embed
        embed = embed_padrao(f"💼 {prof['nome']}", cor=COR_PADRAO)
        embed.description = f"{prof['descricao']}\n\n"
        
        # Adicionar comandos
        comandos = json.loads(prof['comandos']) if prof['comandos'] else []
        if comandos:
            embed.add_field(name="📋 Comandos Disponíveis", value="\n".join([f"`{cmd}`" for cmd in comandos]), inline=False)
        
        # Adicionar informações
        embed.add_field(name="💰 Salário Base", value=f"${prof['salario_base']:,.2f}", inline=True)
        embed.add_field(name="🎓 Requisitos", value=prof['requisitos'] or "Nenhum", inline=True)
        
        # Lógica de Imagem (Local ou URL)
        arquivo_local = None
        if prof.get('imagem_url'):
            if prof['imagem_url'].startswith('local:'):
                caminho = prof['imagem_url'].replace('local:', '')
                if os.path.exists(caminho):
                    arquivo_local = discord.File(caminho, filename="imagem_profissao.png")
                    embed.set_thumbnail(url="attachment://imagem_profissao.png")
                else:
                    embed.set_footer(text="️ Imagem não encontrada no servidor")
            else:
                embed.set_thumbnail(url=prof['imagem_url'])
        
        embed.set_footer(text="Use ?trabalhar para exercer esta profissão")
        
        await ctx.reply(embed=embed, file=arquivo_local, ephemeral=True)

    @commands.command(name="profissoes")
    async def profissoes_cmd(self, ctx: commands.Context):
        """Lista todas as profissões disponíveis."""
        conn = db.conectar()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, salario_base FROM profissoes_info ORDER BY nome")
        profissoes = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        if not profissoes:
            await ctx.reply(embed=embed_aviso("Sem profissões", "Nenhuma profissão cadastrada."), ephemeral=True)
            return
        
        embed = embed_padrao("💼 Profissões Disponíveis", cor=COR_PADRAO)
        embed.description = "**Use o comando da profissão para ver detalhes:**\n\n"
        
        for prof in profissoes:
            embed.description += f"• `?{prof['id']}` — **{prof['nome']}** (${prof['salario_base']:,.2f})\n"
        
        embed.set_footer(text="Exemplo: ?medico para ver detalhes da profissão")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="medico")
    async def medico_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "medico")

    @commands.command(name="policialmilitar", aliases=["pm"])
    async def policial_militar_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "policial_militar")

    @commands.command(name="policialcivil", aliases=["pc"])
    async def policial_civil_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "policial_civil")

    @commands.command(name="advogado")
    async def advogado_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "advogado")

    @commands.command(name="advogadocriminal")
    async def advogado_criminal_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "advogado_criminal")

    @commands.command(name="juiz")
    async def juiz_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "juiz")

    @commands.command(name="professor")
    async def professor_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "professor")

    @commands.command(name="samu")
    async def samu_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "samu")

    @commands.command(name="motoboy")
    async def motoboy_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "motoboy")

    @commands.command(name="vendedor")
    async def vendedor_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "vendedor")

    @commands.command(name="domestica")
    async def domestica_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "domestica")

    @commands.command(name="empresario")
    async def empresario_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "empresario")

    @commands.command(name="jogadorfutebol", aliases=["jogador"])
    async def jogador_futebol_cmd(self, ctx: commands.Context):
        await self._mostrar_profissao(ctx, "jogador_futebol")


async def setup(bot: commands.Bot):
    await bot.add_cog(Profissoes(bot))
