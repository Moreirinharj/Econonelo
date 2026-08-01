import discord
from discord.ext import commands

import database as db
from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
from services.corrupcao_service import (
    tentar_subornar, processar_decisao_suborno,
    denunciar_corrupcao, historico_corrupcao
)
from database.estados_temporarios import salvar_estado, obter_estado, remover_estado


class Corrupcao(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="subornar")
    async def subornar_cmd(self, ctx: commands.Context, membro: discord.Member, valor: int):
        subornador = obter_dados_personagem(str(ctx.author.id))
        if not subornador:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        subornado = db.obter_personagem_ativo(str(membro.id))
        if not subornado:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo.", ephemeral=True))
            return
        if subornado["id"] == subornador["id"]:
            await ctx.reply("🤡 Você quer se subornar, mano? Tá doido? 😂", ephemeral=True)
            return
        if valor < 100:
            await ctx.reply(embed=embed_erro("Valor muito baixo", "Suborno mínimo é $100, mano. Ninguém aceita menos que isso!", ephemeral=True))
            return
        resultado = tentar_subornar(subornador["id"], subornado["id"], valor)
        if resultado.get("preso"):
            await ctx.reply(embed=embed_erro("🚔 Preso!", resultado["msg"], ephemeral=True))
            return
        if not resultado["sucesso"]:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))
            return
        salvar_estado("suborno", str(resultado["corrupcao_id"]), {
            "subornado_id": subornado["id"],
            "subornado_user_id": str(membro.id),
            "valor": valor,
        })
        await ctx.reply(embed=embed_aviso(
            "💰 Suborno oferecido",
            f"{resultado['msg']}\n\n"
            f"💡 {membro.mention} usa `?aceitarsuborno {resultado['corrupcao_id']}` pra aceitar\n"
            f"💡 Ou `?recusarsuborno {resultado['corrupcao_id']}` pra recusar e denunciar"
        , ephemeral=True))

    @commands.command(name="aceitarsuborno")
    async def aceitarsuborno_cmd(self, ctx: commands.Context, corrupcao_id: int):
        subornado = obter_dados_personagem(str(ctx.author.id))
        if not subornado:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        tentativa = obter_estado("suborno", str(corrupcao_id))
        if tentativa is None:
            await ctx.reply(embed=embed_erro("Erro", "Essa tentativa não existe ou já foi resolvida.", ephemeral=True))
            return
        if tentativa["subornado_id"] != subornado["id"]:
            await ctx.reply(embed=embed_erro("Erro", "Esse suborno não é pra você, mano!", ephemeral=True))
            return
        resultado = processar_decisao_suborno(corrupcao_id, aceitar=True)
        remover_estado("suborno", str(corrupcao_id))
        if not resultado["sucesso"]:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))
            return
        await ctx.reply(embed=embed_sucesso("💰 Suborno aceito!", resultado["msg"], ephemeral=True))

    @commands.command(name="recusarsuborno")
    async def recusarsuborno_cmd(self, ctx: commands.Context, corrupcao_id: int):
        subornado = obter_dados_personagem(str(ctx.author.id))
        if not subornado:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        tentativa = obter_estado("suborno", str(corrupcao_id))
        if tentativa is None:
            await ctx.reply(embed=embed_erro("Erro", "Essa tentativa não existe ou já foi resolvida.", ephemeral=True))
            return
        if tentativa["subornado_id"] != subornado["id"]:
            await ctx.reply(embed=embed_erro("Erro", "Esse suborno não é pra você, mano!", ephemeral=True))
            return
        resultado = processar_decisao_suborno(corrupcao_id, aceitar=False)
        remover_estado("suborno", str(corrupcao_id))
        if not resultado["sucesso"]:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))
            return
        await ctx.reply(embed=embed_sucesso("🚫 Suborno recusado", resultado["msg"], ephemeral=True))

    @commands.command(name="denunciarcorrupcao")
    async def denunciarcorrupcao_cmd(self, ctx: commands.Context, membro: discord.Member):
        denunciante = obter_dados_personagem(str(ctx.author.id))
        if not denunciante:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        acusado = db.obter_personagem_ativo(str(membro.id))
        if not acusado:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo.", ephemeral=True))
            return
        resultado = denunciar_corrupcao(denunciante["id"], acusado["id"])
        if not resultado["sucesso"]:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))
            return
        if resultado.get("preso"):
            await ctx.reply(embed=embed_sucesso("🚔 Denúncia aceita!", resultado["msg"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_info("📋 Denúncia registrada", resultado["msg"], ephemeral=True))

    @commands.command(name="historiocorrupcao", aliases=["corrupcao"])
    async def historiocorrupcao_cmd(self, ctx: commands.Context, membro: discord.Member = None):
        if membro:
            personagem = db.obter_personagem_ativo(str(membro.id))
            if not personagem:
                await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo.", ephemeral=True))
                return
        else:
            personagem = obter_dados_personagem(str(ctx.author.id))
            if not personagem:
                await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
                return
        historico = historico_corrupcao(personagem["id"])
        reputacao_corrupta = db.obter_reputacao_corrupta(personagem["id"])
        embed = embed_padrao(f"🕵️ Histórico de Corrupção — {personagem['nome']}", cor=COR_PADRAO)
        embed.add_field(name="🔴 Reputação Corrupta", value=f"{reputacao_corrupta}/100", inline=True)
        if not historico:
            embed.add_field(name="📋 Histórico", value="Nenhuma participação em corrupção. Você tá limpo! ✨", inline=False)
        else:
            linhas = []
            total = len(historico)
            for h in historico[:15]:
                subornador = db.obter_personagem_por_id(h["subornador_id"])
                subornado = db.obter_personagem_por_id(h["subornado_id"])
                if h["subornado_id"] == personagem["id"]:
                    papel = "Subornado"
                    outro = subornador["nome"] if subornador else "Desconhecido"
                else:
                    papel = "Subornador"
                    outro = subornado["nome"] if subornado else "Desconhecido"
                status = "✅ Aceito" if h["aceito"] else ("🚫 Denunciado" if h["denunciado"] else "⏳ Pendente")
                linhas.append(f"**{papel}** — ${h['valor']} com {outro} — {status}")
            embed.add_field(name="📋 Histórico", value="\n".join(linhas), inline=False)
            if total > 15:
                embed.set_footer(text=f"Mostrando 15 de {total} registros")
        await ctx.reply(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Corrupcao(bot))
