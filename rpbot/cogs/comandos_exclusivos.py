import discord
from discord.ext import commands
import random

import database as db
from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO
from utils.comando_ajuda import mostrar_ajuda_cpf, mostrar_ajuda_pedido, validar_cpf
from utils.verificar_personagem import verificar_personagem
from utils.comando_ajuda import mostrar_ajuda_cpf, validar_cpf
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from utils.profissao_check import verificar_profissao
from services.personagem_service import obter_dados_personagem
from services.mensagens_service import mensagem_falha_economica


class ComandosExclusivos(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ===== POLICIAL MILITAR =====

    @commands.command(name="patrulha")
    @verificar_profissao(["policial_militar"])
    async def patrulha_cmd(self, ctx: commands.Context):
        """Inicia uma patrulha (alias de ?trabalhar pra PM)."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        await ctx.reply(
            f"🚓 **Patrulha iniciada, {personagem['nome']}!**\n\n"
            f"Tu saiu pra dar uma volta na viatura. Mantém os olhos abertos, mano!\n\n"
            f"💡 Usa `?trabalhar` pra iniciar o minigame de patrulha."
        )

    @commands.command(name="multar")
    @verificar_profissao(["policial_militar", "policial_civil"])
    async def multar_cmd(self, ctx: commands.Context, membro: discord.Member, motivo: str = None, valor: int = 200):
        """Aplica uma multa em alguém."""
        policial = obter_dados_personagem(str(ctx.author.id))
        if not motivo:
            await ctx.reply(embed=embed_aviso(
                "Cadê o motivo?",
                "Usa `?multar <@user> <motivo> [valor]`\n\n"
                "💡 Exemplo: `?multar @João excesso_de_velocidade 300`"
            ))
            return
        
        alvo = db.obter_personagem_ativo(str(membro.id))
        if not alvo:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo."))
            return
        
        if alvo["id"] == policial["id"]:
            await ctx.reply("🤡 Tu quer se multar, mano? Tá doido? Usa `?multar <@outro_user>`.")
            return
        
        # Aplica a multa (desconta do alvo, dá pro policial como recompensa)
        valor_real = min(valor, alvo["saldo"])
        if valor_real <= 0:
            await ctx.reply(f"💸 O alvo tá liso, mano! Ele não tem grana pra pagar a multa.\n\n💡 Deixa ele trabalhar primeiro com `?trabalhar`.")
            return
        
        db.atualizar_saldo_personagem(alvo["id"], -valor_real)
        db.atualizar_saldo_personagem(policial["id"], valor_real // 2)  # Policial fica com 50%
        db.modificar_status_personagem(policial["id"], "reputacao", 1)
        
        await ctx.reply(embed=embed_sucesso(
            "🎫 Multa aplicada!",
            f"**Policial:** {policial['nome']}\n"
            f"**Multado:** {alvo['nome']}\n"
            f"**Motivo:** {motivo}\n"
            f"**Valor:** ${valor_real}\n\n"
            f"💰 Tu ficou com ${valor_real // 2} (50% vai pro governo, mano)."
        ))

    @commands.command(name="revistar")
    @verificar_profissao(["policial_militar", "policial_civil"])
    async def revistar_cmd(self, ctx: commands.Context, membro: discord.Member):
        """Revista alguém (mostra itens e ficha criminal)."""
        policial = obter_dados_personagem(str(ctx.author.id))
        alvo = db.obter_personagem_ativo(str(membro.id))
        
        if not alvo:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo."))
            return
        
        itens = db.listar_inventario(alvo["id"])
        ficha = alvo.get("ficha_criminal", "limpa")
        
        embed = embed_padrao(f"🔍 Revista de {alvo['nome']}", cor=COR_PADRAO)
        embed.add_field(name="📋 Ficha Criminal", value="✅ Limpa" if ficha == "limpa" else f"❌ {ficha.replace('|', ', ')}", inline=False)
        
        if itens:
            lista_itens = "\n".join(f"• {i['item_nome']} x{i['quantidade']}" for i in itens[:10])
            embed.add_field(name="🎒 Itens encontrados", value=lista_itens, inline=False)
        else:
            embed.add_field(name="🎒 Itens encontrados", value="Nada, tá liso.", inline=False)
        
        embed.set_footer(text=f"Revistado por {policial['nome']}")
        await ctx.reply(embed=embed)

    # ===== MÉDICO / SAMU =====

    @commands.command(name="diagnosticar")
    @verificar_profissao(["medico", "samu"])
    async def diagnosticar_cmd(self, ctx: commands.Context, membro: discord.Member = None):
        """Vê o status de saúde de alguém (ou o teu)."""
        medico = obter_dados_personagem(str(ctx.author.id))
        
        if membro:
            alvo = db.obter_personagem_ativo(str(membro.id))
            if not alvo:
                await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo."))
                return
            paciente = alvo
            titulo = f"🩺 Diagnóstico de {alvo['nome']}"
        else:
            paciente = medico
            titulo = f"🩺 Auto-diagnóstico de {medico['nome']}"
        
        embed = embed_padrao(titulo, cor=COR_PADRAO)
        
        status = {
            "❤️ Saúde": paciente.get("saude", 100),
            "⚡ Energia": paciente.get("energia", 100),
            "🍔 Fome": paciente.get("fome", 100),
            "😊 Felicidade": paciente.get("felicidade", 100),
            "😰 Estresse": paciente.get("estresse", 0),
            "🚿 Higiene": paciente.get("higiene", 100),
        }
        
        diagnostico = []
        for nome, valor in status.items():
            if valor >= 70:
                emoji = "🟢"
            elif valor >= 40:
                emoji = "🟡"
            else:
                emoji = "🔴"
            diagnostico.append(f"{emoji} {nome}: {valor}/100")
        
        embed.description = "\n".join(diagnostico)
        
        # Recomendação médica
        criticos = [k for k, v in status.items() if v < 30]
        if criticos:
            embed.add_field(
                name="⚠️ Recomendação",
                value="Paciente precisa de atenção urgente em: " + ", ".join(criticos),
                inline=False
            )
        else:
            embed.add_field(name="✅ Recomendação", value="Paciente está bem. Só manter os hábitos!", inline=False)
        
        await ctx.reply(embed=embed)

    @commands.command(name="prescrever")
    @verificar_profissao(["medico"])
    async def prescrever_cmd(self, ctx: commands.Context, membro: discord.Member, *, receita: str):
        """Prescreve uma receita pra alguém."""
        medico = obter_dados_personagem(str(ctx.author.id))
        paciente = db.obter_personagem_ativo(str(membro.id))
        
        if not paciente:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo."))
            return
        
        await ctx.reply(embed=embed_info(
            f"📝 Receita Médica",
            f"**Médico:** Dr(a). {medico['nome']}\n"
            f"**Paciente:** {paciente['nome']}\n\n"
            f"**Prescrição:**\n{receita}\n\n"
            f"💡 Mostra essa receita numa farmácia pra comprar os remédios."
        ))

    # ===== ADVOGADO =====

    @commands.command(name="consultar")
    @verificar_profissao(["advogado", "advogado_criminal"])
    async def consultar_cmd(self, ctx: commands.Context, membro: discord.Member, *, assunto: str):
        """Faz uma consulta jurídica pra alguém (cobra!)."""
        advogado = obter_dados_personagem(str(ctx.author.id))
        cliente = db.obter_personagem_ativo(str(membro.id))
        
        if not cliente:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo."))
            return
        
        if cliente["id"] == advogado["id"]:
            await ctx.reply("🤡 Tu quer se consultar, mano? Vai num espelho e se aconselha. 😂")
            return
        
        valor_consulta = 300
        
        if cliente["saldo"] < valor_consulta:
            await ctx.reply(f"💸 O cliente tá liso, mano! Ele não tem ${valor_consulta} pra pagar a consulta.\n\n💡 Manda ele trabalhar com `?trabalhar` primeiro.")
            return
        
        # Cobra a consulta
        db.atualizar_saldo_personagem(cliente["id"], -valor_consulta)
        db.atualizar_saldo_personagem(advogado["id"], valor_consulta)
        db.modificar_status_personagem(advogado["id"], "reputacao", 2)
        
        # Resposta jurídica aleatória
        respostas = [
            "📚 Segundo o artigo 5º da Constituição, tu tem direitos garantidos. Recomendo entrar com uma ação.",
            "⚖️ Pelo que tu me contou, tu tem boas chances de ganhar na justiça. Vamos preparar a petição.",
            "🔍 Preciso analisar melhor os documentos. Me manda tudo que tu tiver relacionado ao caso.",
            "💼 Esse caso é complexo, mas eu posso te ajudar. Vamos marcar uma audiência.",
            "📝 Recomendo fazer um acordo extrajudicial primeiro. É mais rápido e barato.",
        ]
        resposta = random.choice(respostas)
        
        await ctx.reply(embed=embed_sucesso(
            f"⚖️ Consulta Jurídica — ${valor_consulta}",
            f"**Advogado:** {advogado['nome']}\n"
            f"**Cliente:** {cliente['nome']}\n\n"
            f"**Parecer:**\n{resposta}\n\n"
            f"💡 O cliente foi cobrado ${valor_consulta} automaticamente."
        ))

    # ===== PROFESSOR =====

    @commands.command(name="aplicarprova")
    @verificar_profissao(["professor"])
    async def aplicarprova_cmd(self, ctx: commands.Context, membro: discord.Member):
        """Aplica uma prova em alguém (simula)."""
        professor = obter_dados_personagem(str(ctx.author.id))
        aluno = db.obter_personagem_ativo(str(membro.id))
        
        if not aluno:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo."))
            return
        
        # Nota aleatória baseada na escolaridade do aluno
        bonus = {"nenhuma": 0, "fundamental": 1, "medio": 2, "superior": 3, "pos": 4}.get(aluno.get("escolaridade", "nenhuma"), 0)
        nota = min(10.0, round(random.uniform(3.0, 7.0) + bonus, 1))
        
        if nota >= 6:
            status = "✅ APROVADO"
            cor = COR_SUCESSO
        else:
            status = "❌ REPROVADO"
            cor = COR_ERRO
        
        embed = discord.Embed(
            title=f"📝 Resultado da Prova — {aluno['nome']}",
            description=f"**Professor:** {professor['nome']}\n**Nota:** {nota}/10\n**Status:** {status}",
            color=cor
        )
        
        if nota < 6:
            embed.set_footer(text="💡 Aluno precisa estudar mais. Recomendação: ?estudar")
        
        await ctx.reply(embed=embed)

    # ===== CRIMINOSO =====

    @commands.command(name="roubar")
    @verificar_profissao(["criminoso"])
    @commands.command(name="roubar")
    @verificar_profissao(["criminoso"])
    async def roubar_cmd(self, ctx: commands.Context, cpf_id: str = None):
        """Rouba dinheiro de outro personagem."""
        # 1. Mostrar ajuda se não passar o CPF
        if cpf_id is None:
            await ctx.reply(embed=mostrar_ajuda_cpf(ctx, "?roubar", "Rouba dinheiro de outro personagem."), ephemeral=True)
            return
        
        # 2. Validar CPF
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        # 3. Verificar personagem do autor
        personagem = await verificar_personagem(ctx)
        if not personagem:
            return
        
        # 4. Buscar vítima pelo CPF
        vitima = db.obter_personagem_por_cpf(cpf_id)
        if not vitima:
            await ctx.reply(embed=embed_erro("Vítima não encontrada", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        if vitima['id'] == personagem['id']:
            await ctx.reply(embed=embed_erro("Auto-roubo", "Você não pode roubar a si mesmo!"), ephemeral=True)
            return
        
        # 5. Verificar se a vítima tem dinheiro
        if vitima['saldo'] <= 0:
            await ctx.reply(embed=embed_erro("Vítima sem dinheiro", f"{vitima['nome']} não tem dinheiro para roubar."), ephemeral=True)
            return
        
        # 6. Roubar (50% do saldo da vítima)
        valor_roubado = vitima['saldo'] * 0.5
        db.atualizar_saldo_personagem(vitima['id'], -valor_roubado)
        db.atualizar_saldo_personagem(personagem['id'], valor_roubado)
        
        await ctx.reply(embed=embed_sucesso(
            "Roubo realizado!",
            f"Você roubou **${valor_roubado:.2f}** de **{vitima['nome']}** (CPF: {cpf_id})."
        ), ephemeral=True)

    @commands.command(name="contratar")
    @verificar_profissao(["empresario"])
    async def contratar_cmd(self, ctx: commands.Context, membro: discord.Member, profissao: str = None):
        """Contrata alguém pra trabalhar na tua empresa (simula)."""
        empresario = obter_dados_personagem(str(ctx.author.id))
        funcionario = db.obter_personagem_ativo(str(membro.id))
        
        if not funcionario:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo."))
            return
        
        if not profissao:
            await ctx.reply(embed=embed_aviso(
                "Qual profissão?",
                "Usa `?contratar <@user> <profissao>`\n\n"
                "💡 Exemplo: `?contratar @João motoboy`"
            ))
            return
        
        salario = 500  # Salário fixo pra simplicidade
        
        if empresario["saldo"] < salario:
            await ctx.reply(f"💸 Tu não tem grana pra contratar, mano! Precisa de ${salario}.\n\n💡 Usa `?trabalhar` pra ganhar mais.")
            return
        
        db.atualizar_saldo_personagem(empresario["id"], -salario)
        db.modificar_status_personagem(empresario["id"], "reputacao", 3)
        
        await ctx.reply(embed=embed_sucesso(
            "💼 Contratação realizada!",
            f"**Empresário:** {empresario['nome']}\n"
            f"**Funcionário:** {funcionario['nome']}\n"
            f"**Profissão:** {profissao}\n"
            f"**Salário:** ${salario}\n\n"
            f"💡 Boa contratação! O funcionário foi notificado."
        ))

    @commands.command(name="demitir")
    @verificar_profissao(["empresario"])
    async def demitir_cmd(self, ctx: commands.Context, membro: discord.Member):
        """Demitir alguém da tua empresa."""
        empresario = obter_dados_personagem(str(ctx.author.id))
        funcionario = db.obter_personagem_ativo(str(membro.id))
        
        if not funcionario:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo."))
            return
        
        db.modificar_status_personagem(funcionario["id"], "felicidade", -20)
        db.modificar_status_personagem(funcionario["id"], "estresse", 15)
        
        await ctx.reply(embed=embed_aviso(
            "📤 Demissão realizada",
            f"**Empresário:** {empresario['nome']}\n"
            f"**Demitido:** {funcionario['nome']}\n\n"
            f"💼 O funcionário foi demitido. Que a força esteja com ele."
        ))

    # ===== MOTObOY =====

    @commands.command(name="aceitarpedido")
    @verificar_profissao(["motoboy"])
    async def aceitarpedido_cmd(self, ctx: commands.Context):
        """Aceita um pedido de entrega (alias de ?trabalhar pra motoboy)."""
        motoboy = obter_dados_personagem(str(ctx.author.id))
        
        await ctx.reply(
            f"🛵 **Pedido aceito, {motoboy['nome']}!**\n\n"
            f"Tu pegou a mochila térmica e saiu pra entregar.\n\n"
            f"💡 Usa `?trabalhar` pra iniciar o minigame de entrega."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ComandosExclusivos(bot))
