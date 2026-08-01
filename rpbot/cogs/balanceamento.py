import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_INFO
from utils.embeds import embed_padrao, embed_sucesso, embed_info, embed_erro
from services.balanceamento_service import obter_resumo_balanceamento, simular_progressao
import data.balanceamento as bal


class Balanceamento(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="balanceamento")
    @commands.has_permissions(administrator=True)
    async def balanceamento_cmd(self, ctx: commands.Context):
        """Mostra resumo do balanceamento atual (só admin)."""
        resumo = obter_resumo_balanceamento()
        
        embed = embed_padrao("⚖️ Balanceamento do Jogo", cor=COR_PADRAO)
        
        # Economia
        eco = resumo["economia"]
        embed.add_field(
            name="💰 Economia",
            value=f"Saldo inicial: ${eco['saldo_inicial']}\n"
                  f"Limite cartão: ${eco['limite_cartao_inicial']}\n"
                  f"Combustível: ${eco['preco_combustivel']}/L\n"
                  f"Imposto renda: {eco['imposto_renda']}",
            inline=True,
        )
        
        # Progressão
        prog = resumo["progressao"]
        embed.add_field(
            name="📈 Progressão",
            value=f"XP base: {prog['xp_base']}\n"
                  f"Multiplicador: {prog['xp_multiplicador']}x\n"
                  f"Nível 1→2: {prog['xp_nivel_1_para_2']} XP\n"
                  f"Nível 5→6: {prog['xp_nivel_5_para_6']} XP\n"
                  f"Nível 10→11: {prog['xp_nivel_10_para_11']} XP",
            inline=True,
        )
        
        # Chances
        ch = resumo["chances"]
        embed.add_field(
            name="🎲 Chances",
            value=f"Prisão base: {ch['prisao_base']}\n"
                  f"Prisão máx: {ch['prisao_max']}\n"
                  f"Roubo: {ch['roubo']}\n"
                  f"Assalto: {ch['assalto']}\n"
                  f"Fugir polícia: {ch['fugir_policia']}",
            inline=True,
        )
        
        # Status
        st = resumo["status"]
        embed.add_field(
            name="❤️ Deterioração/hora",
            value=f"Fome: {st['deterioracao_fome_hora']}\n"
                  f"Energia: {st['deterioracao_energia_hora']}\n"
                  f"Higiene: {st['deterioracao_higiene_hora']}\n"
                  f"Felicidade: {st['deterioracao_felicidade_hora']}",
            inline=True,
        )
        
        embed.set_footer(text="Valores em data/balanceamento.py")
        await ctx.reply(embed=embed)

    @commands.command(name="salarios")
    @commands.has_permissions(administrator=True)
    async def salarios_cmd(self, ctx: commands.Context):
        """Mostra salários de todas as profissões (só admin)."""
        embed = embed_padrao("💼 Tabela de Salários", cor=COR_PADRAO)
        
        linhas = []
        for prof, dados in sorted(bal.SALARIOS.items(), key=lambda x: x[1]["max"], reverse=True):
            linhas.append(
                f"**{prof}**: ${dados['min']}-${dados['max']} | "
                f"{dados['xp']} XP | {dados['cooldown_min']}min"
            )
        
        embed.description = "\n".join(linhas) if linhas else "Sem salários configurados."
        await ctx.reply(embed=embed)

    @commands.command(name="simularprogressao")
    @commands.has_permissions(administrator=True)
    async def simularprogressao_cmd(self, ctx: commands.Context, profissao: str, trabalhos: int = 100):
        """Simula progressão de XP de uma profissão (só admin)."""
        if profissao not in bal.SALARIOS:
            await ctx.reply(embed=embed_erro("Profissão inválida", f"Opções: {', '.join(bal.SALARIOS.keys())}"))
            return
        
        if trabalhos < 1 or trabalhos > 10000:
            await ctx.reply(embed=embed_erro("Valor inválido", "Use entre 1 e 10000 trabalhos."))
            return
        
        resultado = simular_progressao(1, trabalhos, profissao)
        
        embed = embed_info(
            f"📊 Simulação: {profissao}",
            f"**Trabalhos realizados:** {resultado['trabalhos']}\n"
            f"**XP por trabalho:** {resultado['xp_por_trabalho']}\n"
            f"**Nível inicial:** {resultado['nivel_inicial']}\n"
            f"**Nível final:** {resultado['nivel_final']}\n"
            f"**Níveis ganhos:** {resultado['nivel_final'] - resultado['nivel_inicial']}"
        )
        await ctx.reply(embed=embed)

    @commands.command(name="xpnivel")
    @commands.has_permissions(administrator=True)
    async def xpnivel_cmd(self, ctx: commands.Context, nivel: int):
        """Mostra XP necessário pra um nível específico (só admin)."""
        if nivel < 1 or nivel > 100:
            await ctx.reply(embed=embed_erro("Nível inválido", "Use entre 1 e 100."))
            return
        
        xp = bal.xp_para_proximo_nivel(nivel)
        await ctx.reply(embed=embed_info(
            f"Nível {nivel} → {nivel+1}",
            f"XP necessário: **{xp}**"
        ))


async def setup(bot: commands.Bot):
    await bot.add_cog(Balanceamento(bot))
