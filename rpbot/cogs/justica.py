import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, MSG_SEM_PERSONAGEM
from utils.comando_ajuda import mostrar_ajuda_cpf, mostrar_ajuda_pedido, validar_cpf
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info
from utils.profissao_check import verificar_profissao
from services.personagem_service import obter_dados_personagem
from services.justica_service import criar_denuncia, calcular_fianca_restante
import database as db

class Justica(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="denunciar")
    async def denunciar_cmd(self, ctx: commands.Context, membro: discord.Member, *, crime: str):
        """Abre um processo contra alguém."""
        acusador = obter_dados_personagem(str(ctx.author.id))
        if not acusador:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        reu = db.obter_personagem_ativo(str(membro.id))
        if not reu:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo."))
            return
        
        res = criar_denuncia(reu["id"], acusador["id"], crime, f"Denunciado por {acusador['nome']}")
        if res["sucesso"]:
            await ctx.reply(embed=embed_sucesso(
                "Processo Aberto",
                f"Processo #{res['pid']} aberto contra {reu['nome']}.\n"
                f"Crime: {crime}\n"
                f"Valor da fiança: ${res['fianca']}\n\n"
                f"💡 O réu pode pagar a fiança com `?pagarfianca {res['pid']} <valor>`"
            ))
        else:
            await ctx.reply(embed=embed_erro("Erro", res["msg"]))

    @commands.command(name="processos")
    async def processos_cmd(self, ctx: commands.Context, status: str = "aberto"):
        """Lista processos judiciais."""
        processos = db.listar_processos(status=status)
        if not processos:
            await ctx.reply(embed=embed_info("Nenhum processo", f"Não há processos com status '{status}'."))
            return
        
        embed = embed_padrao(f"⚖️ Processos ({status})", cor=COR_PADRAO)
        for p in processos[:10]:
            reu = db.obter_personagem_por_id(p["reu_id"])
            nome_reu = reu["nome"] if reu else "Desconhecido"
            fianca_rest = calcular_fianca_restante(p["id"])
            embed.add_field(
                name=f"#{p['id']} vs {nome_reu}",
                value=f"**Crime:** {p['crime']}\n**Fiança restante:** ${fianca_rest}\n**Status:** {p['status']}",
                inline=True
            )
        embed.set_footer(text="💡 Advogados: use ?assumirdefesa <id> pra pegar o caso")
        await ctx.reply(embed=embed)

    @commands.command(name="assumirdefesa")
    @verificar_profissao(["advogado", "advogado_criminal"])
    async def assumirdefesa_cmd(self, ctx: commands.Context, processo_id: int):
        """Advogado assume a defesa de um processo."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        
        if db.assumir_defesa(processo_id, personagem["id"]):
            await ctx.reply(embed=embed_sucesso("Defesa assumida", f"Tu agora é o advogado de defesa do processo #{processo_id}. Boa sorte, mano! ⚖️"))
        else:
            await ctx.reply(embed=embed_erro("Erro", "Não foi possível assumir esse processo. Talvez já tenha um advogado ou o processo esteja encerrado."))

    @commands.command(name="julgar")
    @verificar_profissao(["juiz"])
    async def julgar_cmd(self, ctx: commands.Context, processo_id: int, veredito: str, pena_dias: int = 0):
        """Juiz profere sentença. Veredito: 'absolvido' ou 'condenado'."""
        personagem = obter_dados_personagem(str(ctx.author.id))
            
        veredito = veredito.lower()
        if veredito not in ("absolvido", "condenado"):
            await ctx.reply(embed=embed_erro("Erro", "Veredito deve ser 'absolvido' ou 'condenado', mano."))
            return
            
        if veredito == "condenado" and pena_dias <= 0:
            await ctx.reply(embed=embed_erro("Erro", "Condenação requer pena em dias (>0)."))
            return

        p = db.obter_processo(processo_id)
        if not p:
            await ctx.reply(embed=embed_erro("Erro", "Processo não encontrado."))
            return

        db.proferir_sentenca(processo_id, veredito, pena_dias)
        
        if veredito == "condenado":
            db.prender_personagem(p["reu_id"])
            db.adicionar_registro_criminal(p["reu_id"], f"Condenado a {pena_dias} dias")
            msg = f"🔒 Réu condenado a {pena_dias} dias de prisão. Justiça feita! 👨‍⚖️"
        else:
            db.soltar_personagem(p["reu_id"])
            msg = "✅ Réu absolvido e solto. Justiça prevaleceu! 👨‍⚖️"

        await ctx.reply(embed=embed_sucesso("Sentença Proferida", f"Processo #{processo_id} encerrado.\n{msg}"))

    @commands.command(name="pagarfianca")
    async def pagarfianca_cmd(self, ctx: commands.Context, processo_id: int, valor: int):
        """Paga parte ou total da fiança de um processo."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        if personagem["saldo"] < valor:
            await ctx.reply(f"💸 Tá liso, mano! Essa grana não tá nem nos seus sonhos. 💀\n\n💡 Tenta `?trabalhar` pra fazer uma grana ou `?trabalharrapido` se tiver com pressa.\n\n❌ Saldo insuficiente. Tu tem ${personagem['saldo']}.")
            return
        
        res = db.pagar_fianca(processo_id, personagem["id"], valor)
        if res["sucesso"]:
            db.atualizar_saldo_personagem(personagem["id"], -valor)
            if res["novo_status"] == "fianca_paga":
                await ctx.reply(embed=embed_sucesso("Fiança Paga!", f"Tu pagou ${valor}. O réu foi solto! 🎉\n💡 Boa ação, mano. A justiça agradece."))
            else:
                await ctx.reply(embed=embed_sucesso("Fiança Parcial", f"Tu pagou ${valor}. Fiança restante: ${calcular_fianca_restante(processo_id)}\n💡 Continua pagando até completar o valor total."))
        else:
            await ctx.reply(embed=embed_erro("Erro", res["msg"]))


async def setup(bot: commands.Bot):
    await bot.add_cog(Justica(bot))
