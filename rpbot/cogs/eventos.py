import discord
from discord.ext import commands
import json

from data.constantes import (
    COR_PADRAO, COR_SUCESSO, COR_ERRO,
    MSG_SEM_PERSONAGEM,
)
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info
from services.personagem_service import obter_dados_personagem
from services.evento_service import gerar_evento_aleatorio, aplicar_efeitos_eventos, limpar_eventos_antigos
import database as db


class Eventos(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="eventos")
    async def eventos_cmd(self, ctx: commands.Context):
        """Mostra eventos ativos no mundo."""
        limpar_eventos_antigos()
        eventos = db.listar_eventos_ativos()
        
        if not eventos:
            await ctx.reply(embed=embed_info("🌍 Mundo tranquilo", "Nenhum evento especial acontecendo no momento."))
            return
        
        embed = embed_padrao("🌍 Eventos Ativos", cor=COR_PADRAO)
        
        for evento in eventos[:10]:
            efeitos_texto = ""
            if evento["efeitos"]:
                try:
                    efeitos = json.loads(evento["efeitos"])
                    linhas = []
                    for campo, delta in efeitos.items():
                        emoji = "📈" if delta > 0 else "📉"
                        linhas.append(f"{emoji} {campo}: {delta:+}")
                    efeitos_texto = "\n".join(linhas)
                except json.JSONDecodeError:
                    efeitos_texto = "—"
            
            embed.add_field(
                name=f"📰 {evento['titulo']}",
                value=f"{evento['descricao']}\n\n**Efeitos:**\n{efeitos_texto}" if efeitos_texto else evento['descricao'],
                inline=False,
            )
        
        embed.set_footer(text=f"{len(eventos)} evento(s) ativo(s)")
        await ctx.reply(embed=embed)

    @commands.command(name="gerarevento")
    @commands.has_permissions(administrator=True)
    async def gerarevento_cmd(self, ctx: commands.Context):
        """Gera um evento aleatório (só admin)."""
        evento_id = gerar_evento_aleatorio()
        evento = db.obter_evento(evento_id)
        
        await ctx.reply(embed=embed_sucesso(
            "Evento gerado",
            f"📰 **{evento['titulo']}**\n{evento['descricao']}"
        ))

    @commands.command(name="aplicarefeitos")
    async def aplicarefeitos_cmd(self, ctx: commands.Context):
        """Aplica efeitos dos eventos ativos no seu personagem."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        eventos = db.listar_eventos_ativos()
        if not eventos:
            await ctx.reply(embed=embed_info("Nada acontecendo", "Não há eventos ativos no momento."))
            return
        
        aplicar_efeitos_eventos(personagem["id"])
        await ctx.reply(embed=embed_sucesso(
            "Efeitos aplicados",
            f"Os efeitos de {len(eventos)} evento(s) foram aplicados ao seu personagem.\n"
            f"Use `?status` pra ver como ficou."
        ))

    @commands.command(name="limpareventos")
    @commands.has_permissions(administrator=True)
    async def limpareventos_cmd(self, ctx: commands.Context):
        """Remove eventos expirados (só admin)."""
        limpar_eventos_antigos()
        await ctx.reply(embed=embed_sucesso("Eventos limpos", "Eventos expirados foram removidos."))


async def setup(bot: commands.Bot):
    await bot.add_cog(Eventos(bot))
