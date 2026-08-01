import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info
from services.personagem_service import obter_dados_personagem
from services.veiculo_service import (
    comprar_veiculo_service, vender_veiculo_service, abastecer_service,
    reparar_service, toggle_seguro_service, simular_acidente_service, MODELOS_DISPONIVEIS
)
import database as db

MAX_VEICULOS_BASE = 2


class Veiculos(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="veiculos")
    async def veiculos_cmd(self, ctx: commands.Context):
        veiculos = db.listar_veiculos_disponiveis()
        if not veiculos:
            await ctx.reply(embed=embed_erro("Concessionária vazia", "Nenhum veículo disponível no momento.", ephemeral=True))
            return
        embed = embed_padrao("🚗 Concessionária de Veículos", cor=COR_PADRAO)
        for v in veiculos[:10]:
            embed.add_field(
                name=f"{v['modelo']} ({v['placa']})",
                value=f"**ID:** {v['id']}\n**Preço:** ${v['valor']}",
                inline=True
            )
        embed.set_footer(text="Use ?comprarveiculo <id>")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="garagem")
    async def garagem_cmd(self, ctx: commands.Context):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        veiculos = db.listar_veiculos_do_proprietario(personagem["id"])
        if not veiculos:
            await ctx.reply(embed=embed_info("🚗 Garagem vazia", "Você não possui veículos.", ephemeral=True))
            return
        embed = embed_padrao(f"🚗 Garagem de {personagem['nome']}", cor=COR_PADRAO)
        for v in veiculos:
            seguro = "✅ Sim" if v["seguro_ativo"] else "❌ Não"
            placa_formatada = f"`{v['placa']}`"
            embed.add_field(
                name=f"{v['modelo']} {placa_formatada}",
                value=f"**Combustível:** {v['combustivel']}%\n**Saúde:** {v['saude']}%\n**Seguro:** {seguro}\n**Doc:** {v['documentacao'].title()}",
                inline=True
            )
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="comprarveiculo")
    async def comprarveiculo_cmd(self, ctx: commands.Context, veiculo_id: int):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        veiculos_atuais = db.listar_veiculos_do_proprietario(personagem["id"])
        casas = db.listar_casas_do_proprietario(personagem["id"])
        max_veiculos = MAX_VEICULOS_BASE + len(casas)
        if len(veiculos_atuais) >= max_veiculos:
            await ctx.reply(embed=embed_erro(
                "Garagem cheia!",
                f"Você já tem {len(veiculos_atuais)} veículos. Máximo atual: {max_veiculos}.\n\n"
                f"💡 Compra uma casa pra aumentar o limite, ou vende um veículo com `?venderveiculo <id>`."
            ))
            return
        res = comprar_veiculo_service(personagem["id"], veiculo_id)
        if res["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Veículo comprado!", res["mensagem"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro na compra", res["mensagem"], ephemeral=True))

    @commands.command(name="venderveiculo")
    async def venderveiculo_cmd(self, ctx: commands.Context, veiculo_id: int):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        res = vender_veiculo_service(personagem["id"], veiculo_id)
        if res["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Veículo vendido!", res["mensagem"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro na venda", res["mensagem"], ephemeral=True))

    @commands.command(name="abastecer")
    async def abastecer_cmd(self, ctx: commands.Context, placa: str, litros: int):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        res = abastecer_service(personagem["id"], placa, litros)
        if res["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Posto de Gasolina", res["mensagem"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro no abastecimento", res["mensagem"], ephemeral=True))

    @commands.command(name="reparar")
    async def reparar_cmd(self, ctx: commands.Context, placa: str):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        res = reparar_service(personagem["id"], placa)
        if res["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Oficina Mecânica", res["mensagem"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro no reparo", res["mensagem"], ephemeral=True))

    @commands.command(name="seguro")
    async def seguro_cmd(self, ctx: commands.Context, placa: str):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        res = toggle_seguro_service(personagem["id"], placa)
        if res["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Seguro", res["mensagem"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", res["mensagem"], ephemeral=True))

    @commands.command(name="acidente")
    async def acidente_cmd(self, ctx: commands.Context, placa: str, severidade: int = 30):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        res = simular_acidente_service(personagem["id"], placa, severidade)
        if res["sucesso"]:
            await ctx.reply(embed=embed_erro("💥 Acidente!", res["mensagem"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", res["mensagem"], ephemeral=True))

    @commands.command(name="criarveiculo")
    @commands.has_permissions(administrator=True)
    async def criarveiculo_cmd(self, ctx: commands.Context, modelo: str):
        if modelo not in MODELOS_DISPONIVEIS:
            await ctx.reply(embed=embed_erro("Modelo inválido", f"Opções: {', '.join(MODELOS_DISPONIVEIS.keys())}"))
            return
        info = MODELOS_DISPONIVEIS[modelo]
        veiculo_id = db.criar_veiculo(info["nome"], info["valor"])
        v = db.obter_veiculo(veiculo_id=veiculo_id)
        await ctx.reply(embed=embed_sucesso("Veículo criado", f"**{v['modelo']}**\nPlaca: `{v['placa']}`\nValor: ${v['valor']}", ephemeral=True))


async def setup(bot: commands.Bot):
    await bot.add_cog(Veiculos(bot))
