import discord
from discord.ext import commands
import time

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
from services.concurso_service import (
    abrir_concursos_aleatorios, escolher_especialidade_professor,
    gerar_prova_concurso, avaliar_prova, processar_aprovacao
)
from services.concurso_profissao_service import (
    abrir_concursos_profissoes_aleatorios, pode_fazer_concurso_profissao,
    gerar_prova_profissao, processar_aprovacao_profissao
)
from data.professor_data import ESPECIALIDADES_PROFESSOR, CONCURSOS_PROFISSOES
import database as db


class ProvaView(discord.ui.View):
    def __init__(self, opcoes, callback_resposta, timeout=300):
        super().__init__(timeout=timeout)
        letras = ["A", "B", "C", "D"]
        for i, opcao in enumerate(opcoes):
            if i >= 4:
                break
            botao = discord.ui.Button(label=f"{letras[i]}) {opcao}"[:80], style=discord.ButtonStyle.primary)
            async def callback(interaction: discord.Interaction, indice=i):
                await callback_resposta(interaction, indice)
            botao.callback = callback
            self.add_item(botao)


class Concursos(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.provas_em_andamento = {}

    @commands.command(name="escolherespecialidade", aliases=["especialidade"])
    async def escolherespecialidade_cmd(self, ctx: commands.Context, especialidade: str = None):
        """Escolhe especialidade como professor."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        if personagem.get("profissao") != "professor":
            await ctx.reply(embed=embed_erro("Não é professor", "Você precisa ser professor primeiro. Usa `?escolherprofissao professor`.", ephemeral=True))
            return
        
        if not especialidade:
            embed = embed_padrao("🎓 Especialidades de Professor", cor=COR_PADRAO)
            for esp, dados in ESPECIALIDADES_PROFESSOR.items():
                materias = ", ".join(dados["materias"][:3]) + "..."
                embed.add_field(name=f"📚 {dados['nome']}", value=f"{dados['descricao']}\n*Matérias:* {materias}\n\n💡 `?escolherespecialidade {esp}`", inline=False)
            await ctx.reply(embed=embed, ephemeral=True)
            return
        
        resultado = escolher_especialidade_professor(personagem["id"], especialidade.lower())
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Especialidade escolhida", resultado["msg"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))

    @commands.command(name="concursos")
    async def concursos_cmd(self, ctx: commands.Context, tipo: str = None):
        """Lista concursos abertos (professores ou profissões)."""
        concursos_prof = db.listar_concursos_abertos()
        concursos_profissao = db.listar_concursos_profissao()
        
        if not concursos_prof and not concursos_profissao:
            await ctx.reply(embed=embed_info("📋 Sem concursos", "Nenhum concurso aberto no momento.\n\n💡 Admin: usa `?abrirconcursos` pra gerar novos.", ephemeral=True))
            return
        
        embed = embed_padrao("📋 Concursos Públicos Abertos", cor=COR_PADRAO)
        
        # Concursos de professores
        if concursos_prof:
            embed.add_field(name="🎓 Concursos para PROFESSORES", value="─" * 30, inline=False)
            for c in concursos_prof[:5]:
                tempo_restante = int((c["encerra_em"] - time.time()) / 3600)
                esp_nome = ESPECIALIDADES_PROFESSOR.get(c["especialidade"], {}).get("nome", c["especialidade"])
                embed.add_field(
                    name=f"🏛️ {c['universidade']} — {esp_nome}",
                    value=f"**ID:** `{c['id'][:20]}...`\n**Vagas:** {c['vagas']} | **Salário:** ${c['salario']}/mês\n**Tempo:** {tempo_restante}h",
                    inline=True,
                )
        
        # Concursos de profissões
        if concursos_profissao:
            embed.add_field(name="💼 Concursos para PROFISSÕES", value="─" * 30, inline=False)
            for c in concursos_profissao[:5]:
                tempo_restante = int((c["encerra_em"] - time.time()) / 3600)
                prof_nome = CONCURSOS_PROFISSOES.get(c["especialidade"], {}).get("nome", c["especialidade"])
                orgao = CONCURSOS_PROFISSOES.get(c["especialidade"], {}).get("orgao", "")
                embed.add_field(
                    name=f"🏢 {orgao} — {prof_nome}",
                    value=f"**ID:** `{c['id'][:20]}...`\n**Vagas:** {c['vagas']} | **Salário:** ${c['salario']}/mês\n**Tempo:** {tempo_restante}h",
                    inline=True,
                )
        
        embed.set_footer(text="Use ?fazerconcurso <id> pra fazer a prova")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="fazerconcurso")
    async def fazerconcurso_cmd(self, ctx: commands.Context, concurso_id: str):
        """Faz prova de concurso público."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        user_id = str(ctx.author.id)
        if user_id in self.provas_em_andamento:
            await ctx.reply(embed=embed_erro("Prova em andamento", "Termine a prova atual antes de iniciar outra.", ephemeral=True))
            return
        
        # Busca concurso (pode ser ID parcial)
        concurso = None
        tipo_concurso = None
        
        # Primeiro procura em concursos de professores
        for c in db.listar_concursos_abertos():
            if c["id"].startswith(concurso_id) or c["id"] == concurso_id:
                concurso = c
                tipo_concurso = "professor"
                break
        
        # Se não achou, procura em concursos de profissão
        if not concurso:
            for c in db.listar_concursos_profissao():
                if c["id"].startswith(concurso_id) or c["id"] == concurso_id:
                    concurso = c
                    tipo_concurso = "profissao"
                    break
        
        if not concurso:
            await ctx.reply(embed=embed_erro("Concurso não encontrado", "Verifica o ID com `?concursos`.", ephemeral=True))
            return
        
        # Verifica se já participou
        if db.ja_participou_concurso(personagem["id"], concurso["id"]):
            await ctx.reply(embed=embed_erro("Já participou", "Você já fez esse concurso.", ephemeral=True))
            return
        
        # Verificações específicas por tipo
        if tipo_concurso == "professor":
            if personagem.get("profissao") != "professor":
                await ctx.reply(embed=embed_erro("Não é professor", "Esse concurso é só pra professores.", ephemeral=True))
                return
        else:  # profissao
            verificacao = pode_fazer_concurso_profissao(personagem["id"], concurso["especialidade"])
            if not verificacao["pode"]:
                msg = verificacao["msg"]
                if "helper" in verificacao:
                    msg += f"\n\n{verificacao['helper']}"
                await ctx.reply(embed=embed_erro("Não pode fazer", msg, ephemeral=True))
                return
        
        # Gera prova
        if tipo_concurso == "professor":
            prova = gerar_prova_concurso(concurso["especialidade"], num_questoes=5)
        else:
            prova = gerar_prova_profissao(concurso["especialidade"], num_questoes=5)
        
        if not prova["sucesso"]:
            await ctx.reply(embed=embed_erro("Erro", prova["msg"], ephemeral=True))
            return
        
        self.provas_em_andamento[user_id] = {
            "concurso_id": concurso["id"],
            "concurso": concurso,
            "tipo": tipo_concurso,
            "questoes": prova["questoes"],
            "indice": 0,
            "acertos": 0,
            "respostas": [],
            "personagem_id": personagem["id"],
        }
        
        await self._enviar_questao(ctx, user_id)

    async def _enviar_questao(self, ctx, user_id):
        dados = self.provas_em_andamento[user_id]
        questoes = dados["questoes"]
        indice = dados["indice"]
        questao = questoes[indice]
        
        async def callback_resposta(interaction: discord.Interaction, escolha: int):
            if str(interaction.user.id) != user_id:
                await interaction.response.send_message("Essa prova não é sua!", ephemeral=True)
                return
            
            dados = self.provas_em_andamento.get(user_id)
            if not dados:
                await interaction.response.send_message("Prova expirou.", ephemeral=True)
                return
            
            questao_atual = dados["questoes"][dados["indice"]]
            if escolha == questao_atual["correta"]:
                dados["acertos"] += 1
                feedback = "✅ Certa!"
            else:
                feedback = f"❌ Errada. Correta: {questao_atual['opcoes'][questao_atual['correta']]}"
            
            dados["respostas"].append(escolha)
            dados["indice"] += 1
            
            if dados["indice"] >= len(questoes):
                resultado = avaliar_prova(dados["respostas"], questoes)
                
                if dados["tipo"] == "professor":
                    processamento = processar_aprovacao(dados["personagem_id"], dados["concurso_id"], resultado["nota"])
                else:
                    processamento = processar_aprovacao_profissao(dados["personagem_id"], dados["concurso"]["especialidade"], resultado["nota"], dados["concurso_id"])
                
                del self.provas_em_andamento[user_id]
                
                texto_final = f"{feedback}\n\n📊 **Nota: {resultado['nota']}/10** ({resultado['acertos']}/{resultado['total']} acertos)\n\n{processamento['msg']}"
                
                await interaction.response.edit_message(content=texto_final, view=None, embed=None)
            else:
                await interaction.response.edit_message(content=feedback, view=None, embed=None)
                await self._enviar_questao(ctx, user_id)
        
        embed = embed_padrao(f"📝 Concurso — {dados['concurso'].get('universidade', dados['concurso'].get('especialidade'))}", cor=COR_PADRAO)
        embed.description = f"**Questão {indice + 1}/{len(questoes)}**\n\n{questao['pergunta']}"
        
        view = ProvaView(questao["opcoes"], callback_resposta)
        await ctx.reply(embed=embed, view=view, ephemeral=True)

    @commands.command(name="meusconcursos")
    async def meusconcursos_cmd(self, ctx: commands.Context):
        """Mostra seu histórico de concursos."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        participacoes = db.listar_participacoes_personagem(personagem["id"])
        
        embed = embed_padrao(f"📋 Seus Concursos — {personagem['nome']}", cor=COR_PADRAO)
        
        esp = personagem.get("especialidade_professor")
        cargo = personagem.get("cargo_atual")
        concurso_prof = personagem.get("concurso_profissao")
        
        if esp:
            embed.add_field(name="🎓 Especialidade", value=ESPECIALIDADES_PROFESSOR.get(esp, {}).get("nome", esp), inline=True)
        if cargo:
            embed.add_field(name="💼 Cargo Atual", value=cargo, inline=True)
            embed.add_field(name="💰 Salário", value=f"${personagem.get('salario_cargo', 0)}/mês", inline=True)
        if concurso_prof:
            embed.add_field(name="🏢 Concurso Profissão", value=concurso_prof.replace("_", " ").title(), inline=True)
        
        if not participacoes:
            embed.add_field(name="📊 Histórico", value="Nenhuma participação ainda.", inline=False)
        else:
            linhas = []
            for p in participacoes[:10]:
                status = "✅ Aprovado" if p["aprovado"] else "❌ Reprovado"
                esp_nome = ESPECIALIDADES_PROFESSOR.get(p["especialidade"], {}).get("nome", p["especialidade"])
                linhas.append(f"**{p['universidade']}** — {esp_nome}\nNota: {p['nota']}/10 — {status}")
            embed.add_field(name="📊 Histórico", value="\n\n".join(linhas), inline=False)
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="abrirconcursos")
    @commands.has_permissions(administrator=True)
    async def abrirconcursos_cmd(self, ctx: commands.Context, quantidade: int = 5):
        """Abre concursos aleatórios (só admin)."""
        if quantidade < 1 or quantidade > 20:
            await ctx.reply(embed=embed_erro("Valor inválido", "Escolhe entre 1 e 20.", ephemeral=True))
            return
        
        count_prof = abrir_concursos_aleatorios(quantidade)
        count_profissao = abrir_concursos_profissoes_aleatorios()
        
        await ctx.reply(embed=embed_sucesso(
            "Concursos abertos!",
            f"🎓 {count_prof} concursos de PROFESSOR\n💼 {count_profissao} concursos de PROFISSÃO\n\n💡 Usa `?concursos` pra ver a lista."
        , ephemeral=True))


async def setup(bot: commands.Bot):
    await bot.add_cog(Concursos(bot))

    @commands.command(name="infouniversidade", aliases=["infouni", "uni"])
    async def infouniversidade_cmd(self, ctx: commands.Context, sigla: str = None):
        """Mostra informações detalhadas sobre uma universidade."""
        from data.professor_data import MODELOS_CONCURSO, ESPECIALIDADES_PROFESSOR
        
        if not sigla:
            embed = embed_padrao("🏛️ Universidades Disponíveis", cor=COR_PADRAO)
            linhas = []
            for cod, dados in MODELOS_CONCURSO.items():
                linhas.append(f"• **{dados['universidade']}** ({dados['nome_completo']})\n  💡 `?infouni {cod}`")
            embed.description = "Use o comando abaixo para ver detalhes, cursos e salários de cada instituição:\n\n" + "\n".join(linhas)
            await ctx.reply(embed=embed, ephemeral=True)
            return
        
        sigla = sigla.lower()
        if sigla not in MODELOS_CONCURSO:
            await ctx.reply(embed=embed_erro("Universidade não encontrada", "Use `?infouniversidade` sem argumentos pra ver a lista.", ephemeral=True))
            return
        
        dados = MODELOS_CONCURSO[sigla]
        
        embed = embed_padrao(f"🏛️ {dados['nome_completo']} ({dados['universidade']})", cor=COR_PADRAO)
        embed.description = dados["descricao"]
        
        cursos_formatados = ", ".join(dados.get("cursos_destaque", []))
        embed.add_field(name="📚 Cursos de Destaque", value=cursos_formatados, inline=False)
        embed.add_field(name="💼 Salário Base (Professor)", value=f"${dados['salario_base']}/mês", inline=True)
        embed.add_field(name="🎯 Nível Exigido", value=dados["nivel"].title(), inline=True)
        embed.add_field(name="📋 Vagas Médias por Concurso", value=str(dados["vagas_base"]), inline=True)
        
        embed.set_footer(text="Use ?concursos para ver editais abertos desta instituição.")
        await ctx.reply(embed=embed, ephemeral=True)
