import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info
from services.personagem_service import obter_dados_personagem
from services.casa_service import (
    comprar_imovel, vender_imovel, reformar_casa,
    depositar_cofre, sacar_cofre, DECORACOES, TIPOS_CASA,
)
import database as db

MAX_CASAS_POR_JOGADOR = 3


class Casas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="casas")
    async def casas_cmd(self, ctx: commands.Context, cidade: str = None):
        casas = db.listar_casas_disponiveis(cidade=cidade)
        if not casas:
            await ctx.reply(embed=embed_erro("Nenhuma casa disponível", "Tente outra cidade ou aguarde novas casas."))
            return
        embed = embed_padrao(f"🏠 Casas à Venda{' em ' + cidade if cidade else ''}", cor=COR_PADRAO)
        for casa in casas[:10]:
            embed.add_field(
                name=f"{casa['nome']} (ID: {casa['id']})",
                value=f"**Tipo:** {casa['tipo']}\n**Cidade:** {casa['cidade']}\n**Bairro:** {casa['bairro']}\n**Preço:** ${casa['preco']}\n**Garagem:** {casa['garagem']} vagas",
                inline=True,
            )
        embed.set_footer(text="Use ?comprarcasa <id> pra comprar")
        await ctx.reply(embed=embed)

    @commands.command(name="minhascasas")
    async def minhascasas_cmd(self, ctx: commands.Context):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        casas = db.listar_casas_do_proprietario(personagem["id"])
        if not casas:
            await ctx.reply(embed=embed_info("🏠 Sem casas", "Você não possui nenhuma casa. Use `?casas` pra ver casas à venda."))
            return
        embed = embed_padrao(f"🏠 Casas de {personagem['nome']}", cor=COR_PADRAO)
        for casa in casas:
            decoracao_nome = DECORACOES.get(casa["decoracao"], {}).get("nome", casa["decoracao"])
            embed.add_field(
                name=f"{casa['nome']} (ID: {casa['id']})",
                value=f"**Tipo:** {casa['tipo']}\n**Endereço:** {casa['bairro']}, {casa['cidade']}\n**Decoração:** {decoracao_nome}\n**Cofre:** ${casa['cofre']}\n**Garagem:** {casa['garagem']} vagas",
                inline=False,
            )
        await ctx.reply(embed=embed)

    @commands.command(name="comprarcasa")
    async def comprarcasa_cmd(self, ctx: commands.Context, casa_id: int):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        casas_atuais = db.listar_casas_do_proprietario(personagem["id"])
        if len(casas_atuais) >= MAX_CASAS_POR_JOGADOR:
            await ctx.reply(embed=embed_erro(
                "Limite atingido",
                f"Você já tem {MAX_CASAS_POR_JOGADOR} casas, mano! Vende uma antes de comprar outra.\n\n"
                f"💡 Usa `?minhascasas` pra ver tuas casas e `?vendercasa <id>` pra vender."
            ))
            return
        resultado = comprar_imovel(personagem["id"], casa_id)
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Casa comprada!", resultado["mensagem"]))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["mensagem"]))

    @commands.command(name="vendercasa")
    async def vendercasa_cmd(self, ctx: commands.Context, casa_id: int):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        resultado = vender_imovel(personagem["id"], casa_id)
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Casa vendida!", resultado["mensagem"]))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["mensagem"]))

    @commands.command(name="reformar")
    async def reformar_cmd(self, ctx: commands.Context, casa_id: int, decoracao: str):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        resultado = reformar_casa(personagem["id"], casa_id, decoracao)
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Reforma concluída", resultado["mensagem"]))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["mensagem"]))

    @commands.command(name="cofredepositar")
    async def cofredepositar_cmd(self, ctx: commands.Context, casa_id: int, valor: int):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        resultado = depositar_cofre(personagem["id"], casa_id, valor)
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Depósito feito", resultado["mensagem"]))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["mensagem"]))

    @commands.command(name="cofresacar")
    async def cofresacar_cmd(self, ctx: commands.Context, casa_id: int, valor: int):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        resultado = sacar_cofre(personagem["id"], casa_id, valor)
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Saque feito", resultado["mensagem"]))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["mensagem"]))

    @commands.command(name="criarcasa")
    @commands.has_permissions(administrator=True)
    async def criarcasa_cmd(self, ctx: commands.Context, tipo: str, cidade: str, bairro: str, preco: int, *, nome: str = None):
        if tipo not in TIPOS_CASA:
            await ctx.reply(embed=embed_erro("Tipo inválido", f"Opções: {', '.join(TIPOS_CASA.keys())}"), ephemeral=True)
            return
        info = TIPOS_CASA[tipo]
        nome_real = nome or f"{info['nome']} em {bairro}"
        garagem = info["garagem"]
        casa_id = db.criar_casa(nome_real, tipo, cidade, bairro, preco, garagem)
        await ctx.reply(embed=embed_sucesso(
            "Casa criada",
            f"**{nome_real}** (ID: {casa_id})\nTipo: {tipo}\nCidade: {cidade}\nPreço: ${preco}"
        ))


async def setup(bot: commands.Bot):
    await bot.add_cog(Casas(bot))
