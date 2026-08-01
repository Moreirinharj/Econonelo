import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
from services.viagem_service import obter_estados_disponiveis, viajar, voltar_para_casa, ESTADOS_DISPONIVEIS
import database as db


class Viagem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="aeroportos", aliases=["voos", "destinos"])
    async def aeroportos_cmd(self, ctx: commands.Context):
        """Mostra voos disponíveis a partir do seu estado atual."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        estado_atual = personagem.get("estado_atual") or personagem.get("estado")
        nome_estado = ESTADOS_DISPONIVEIS.get(estado_atual, {}).get("nome", estado_atual)
        
        destinos = obter_estados_disponiveis(estado_atual)
        
        embed = embed_padrao("✈️ Aeroportos Disponíveis", cor=COR_PADRAO)
        embed.description = f"📍 Você está em: **{nome_estado}** ({estado_atual})\n\nEscolha um destino:"
        
        for d in destinos:
            embed.add_field(
                name=f"🛫 {d['nome']} ({d['uf']})",
                value=f"**Aeroporto:** {d['aeroporto']}\n**Passagem:** ${d['custo']}\n💡 `?viajar {d['uf']}`",
                inline=True
            )
        
        embed.set_footer(text="Use ?voltarparacasa para retornar ao seu estado de origem.")
        await ctx.reply(embed=embed)

    @commands.command(name="viajar")
    async def viajar_cmd(self, ctx: commands.Context, estado: str = None):
        """Viaja para outro estado."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        if not estado:
            await ctx.reply(embed=embed_aviso(
                "Cadê o destino?",
                "Usa `?viajar <UF>` pra viajar.\n\n💡 Exemplo: `?viajar RJ`\nUse `?aeroportos` pra ver os destinos."
            ))
            return
        
        resultado = viajar(personagem["id"], estado)
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Viagem Realizada", resultado["msg"]))
        else:
            msg = resultado["msg"]
            if "helper" in resultado:
                msg += f"\n\n{resultado['helper']}"
            await ctx.reply(embed=embed_erro("Erro na viagem", msg))

    @commands.command(name="voltarparacasa", aliases=["voltar"])
    async def voltarparacasa_cmd(self, ctx: commands.Context):
        """Volta para o estado de origem do teu personagem."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        resultado = voltar_para_casa(personagem["id"])
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("De volta pra casa!", resultado["msg"]))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"]))

    @commands.command(name="meuestado")
    async def meuestado_cmd(self, ctx: commands.Context):
        """Mostra onde teu personagem está agora."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        estado_atual = personagem.get("estado_atual") or personagem.get("estado")
        estado_origem = personagem.get("estado")
        nome_atual = ESTADOS_DISPONIVEIS.get(estado_atual, {}).get("nome", estado_atual)
        nome_origem = ESTADOS_DISPONIVEIS.get(estado_origem, {}).get("nome", estado_origem)
        
        if estado_atual == estado_origem:
            msg = f"🏠 Você está na sua terra natal: **{nome_atual}** ({estado_atual})."
        else:
            msg = f"🧳 Você está viajando em: **{nome_atual}** ({estado_atual}).\n🏠 Sua terra natal é: **{nome_origem}** ({estado_origem})."
        
        await ctx.reply(embed=embed_info("📍 Localização Atual", msg))

    @commands.command(name="infoestado", aliases=["estado"])
    async def infoestado_cmd(self, ctx: commands.Context, uf: str = None):
        """Mostra informações sobre um estado."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        estado_atual = personagem.get("estado_atual") or personagem.get("estado")
        
        if uf:
            uf = uf.upper()
            if uf not in ESTADOS_DISPONIVEIS:
                await ctx.reply(embed=embed_erro(
                    "Estado inválido",
                    f"UF não encontrada. Use `?aeroportos` pra ver os disponíveis."
                ))
                return
            estado_info = ESTADOS_DISPONIVEIS[uf]
        else:
            uf = estado_atual
            estado_info = ESTADOS_DISPONIVEIS.get(uf, {})
        
        embed = embed_padrao(f"📍 {estado_info.get('nome', uf)} ({uf})", cor=COR_PADRAO)
        
        aeroporto = estado_info.get('aeroporto', 'N/A')
        custo = estado_info.get('custo_base', 0)
        
        embed.description = f"**Aeroporto:** {aeroporto}\n**Custo base de passagem:** ${custo}"
        
        if uf == estado_atual:
            embed.add_field(name="🏠 Status", value="Você está aqui agora!", inline=False)
        else:
            embed.add_field(
                name="✈️ Viagem",
                value=f"Use `?viajar {uf}` pra ir até lá (custa ${custo})",
                inline=False
            )
        
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Viagem(bot))
