import discord
from utils.horario import formatar_data_hora
from discord.ext import commands

from data.constantes import (
    COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO,
    MSG_SEM_PERSONAGEM, EMOJI_DINHEIRO,
)
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
from services.economia_service import depositar, sacar, pix_enviar, pagar_cartao, extrato_resumido
from services.mensagens_service import mensagem_falha_economica
import database as db


class Economia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="carteira", aliases=["wallet"])
    async def carteira(self, ctx: commands.Context):
        """Mostra resumo financeiro completo."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.", ephemeral=True)
            return
        
        resumo = extrato_resumido(personagem["id"])
        cartao = resumo["cartao"]
        
        embed = embed_padrao(f"{EMOJI_DINHEIRO} Carteira de {personagem['nome']}", cor=COR_PADRAO)
        embed.add_field(name="💵 Bolso", value=f"${resumo['bolso']}", inline=True)
        embed.add_field(name="🏦 Banco", value=f"${resumo['banco']}", inline=True)
        # ✅ CORREÇÃO: Mostra percentual do cartão usado
        percentual_uso = int((cartao['fatura'] / cartao['limite']) * 100) if cartao['limite'] > 0 else 0
        barra_cartao = f"{'█' * (percentual_uso // 10)}{'░' * (10 - percentual_uso // 10)}"
        embed.add_field(
            name="💳 Cartão",
            value=f"${cartao['fatura']}/{cartao['limite']} ({percentual_uso}%)\n{barra_cartao}\nDisponível: ${cartao['disponivel']}",
            inline=True,
        )
        
        if resumo["chave_pix"]:
            embed.add_field(name="🔑 Chave PIX", value=f"`{resumo['chave_pix']}`", inline=False)
        else:
            embed.add_field(name="🔑 Chave PIX", value="Não definida. Usa `?pixchave <chave>`", inline=False)
        
        # Dica se tá liso
        total = resumo["bolso"] + resumo["banco"]
        if total < 100:
            embed.set_footer(text="💀 Tá liso, mano. Usa ?trabalhar pra fazer uma grana!")
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="depositar", aliases=["dep"])
    async def depositar_cmd(self, ctx: commands.Context, valor: int):
        """Deposita dinheiro do bolso no banco."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.", ephemeral=True)
            return
        
        resultado = depositar(personagem["id"], valor)
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Depósito feito", resultado["mensagem"], ephemeral=True))
        else:
            await ctx.reply(f"{mensagem_falha_economica(personagem, ephemeral=True)}\n\n❌ {resultado['mensagem']}")

    @commands.command(name="sacar", aliases=["saq"])
    async def sacar_cmd(self, ctx: commands.Context, valor: int):
        """Saca dinheiro do banco pro bolso."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.", ephemeral=True)
            return
        
        resultado = sacar(personagem["id"], valor)
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Saque feito", resultado["mensagem"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Deu ruim", resultado["mensagem"], ephemeral=True))

    @commands.command(name="pixchave")
    async def pixchave(self, ctx: commands.Context, *, chave: str):
        """Define sua chave PIX."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.", ephemeral=True)
            return
        
        db.definir_chave_pix(personagem["id"], chave)
        await ctx.reply(embed=embed_sucesso("Chave PIX definida", f"Sua chave agora é: `{chave}`\n💡 Agora os outros podem te mandar PIX com `?pix {chave} <valor>`", ephemeral=True))

    @commands.command(name="pix")
    async def pix_cmd(self, ctx: commands.Context, chave: str, valor: int):
        """Envia PIX pra outra pessoa pela chave."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.", ephemeral=True)
            return
        
        resultado = pix_enviar(personagem["id"], chave, valor)
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("PIX enviado", resultado["mensagem"], ephemeral=True))
        else:
            await ctx.reply(f"{mensagem_falha_economica(personagem, ephemeral=True)}\n\n❌ {resultado['mensagem']}")

    @commands.command(name="cartao")
    async def cartao_cmd(self, ctx: commands.Context):
        """Mostra dados do cartão de crédito."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.", ephemeral=True)
            return
        
        cartao = db.obter_dados_cartao(personagem["id"])
        embed = embed_info(
            "💳 Cartão de Crédito",
            f"**Limite:** ${cartao['limite']}\n"
            f"**Fatura atual:** ${cartao['fatura']}\n"
            f"**Disponível:** ${cartao['disponivel']}\n\n"
            f"💡 Usa `?pagarcartao <valor>` pra pagar a fatura."
        )
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="pagarcartao", aliases=["pagarfat"])
    async def pagarcartao_cmd(self, ctx: commands.Context, valor: int):
        """Paga fatura do cartão usando saldo do banco."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.", ephemeral=True)
            return
        
        resultado = pagar_cartao(personagem["id"], valor)
        if resultado["sucesso"]:
            await ctx.reply(
                embed=embed_sucesso(
                    "Fatura paga",
                    f"Tu pagou ${resultado['valor_pago']} da fatura. Boa, parceiro!\n"
                    f"Nova fatura: ${resultado['dados']['fatura']}"
                , ephemeral=True)
            )
        else:
            await ctx.reply(f"{mensagem_falha_economica(personagem, ephemeral=True)}\n\n❌ {resultado['mensagem']}")

    @commands.command(name="extrato")
    async def extrato_cmd(self, ctx: commands.Context):
        """Mostra últimas transações."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.", ephemeral=True)
            return
        
        transacoes = db.listar_transacoes(personagem["id"], 15)
        
        embed = embed_padrao("📜 Extrato", cor=COR_PADRAO)
        
        # ✅ CORREÇÃO: Formatação melhorada do extrato
        if not transacoes:
            embed.description = "Nenhuma transação ainda, mano. Tá parado! 💤"
        else:
            linhas = []
            for t in transacoes:
                # Define se é entrada ou saída
                entradas = ["deposito", "pix_recebido", "venda_casa", "venda_veiculo", "suborno_devolvido", "salario"]
                saidas = ["saque", "pix_enviado", "compra_casa", "compra_veiculo", "suborno_enviado", "mensalidade"]
                
                if t["tipo"] in entradas:
                    emoji = "🟢"
                    sinal = "+"
                elif t["tipo"] in saidas:
                    emoji = "🔴"
                    sinal = "-"
                else:
                    emoji = "⚪"
                    sinal = ""
                
                desc = t["descricao"] or t["tipo"].replace("_", " ").title()
                linhas.append(f"{emoji} **{sinal}${t['valor']}** — {desc}")
            
            embed.description = "\n".join(linhas[:15])
            if len(transacoes) > 15:
                embed.set_footer(text=f"Mostrando 15 de {len(transacoes)} transações")
        
        await ctx.reply(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Economia(bot))
