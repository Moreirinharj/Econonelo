import discord
from utils.horario import formatar_data_hora
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.comando_ajuda import mostrar_ajuda_cpf, mostrar_ajuda_pedido, validar_cpf
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
from services.aula_service import dar_aula, assistir_aula
from data.professor_data import ESPECIALIDADES_PROFESSOR
import database as db


class Aulas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="daraula")
    async def daraula_cmd(self, ctx: commands.Context, curso_id: int):
        """Professor dá aula em um curso."""
        professor = obter_dados_personagem(str(ctx.author.id))
        if not professor:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        if professor.get("profissao") != "professor":
            await ctx.reply(embed=embed_erro("Não é professor", "Você precisa ser professor pra dar aula.", ephemeral=True))
            return
        
        if not professor.get("especialidade_professor"):
            await ctx.reply(embed=embed_erro("Sem especialidade", "Escolhe tua especialidade com `?escolherespecialidade`.", ephemeral=True))
            return
        
        if professor.get("energia", 100) < 20:
            await ctx.reply(embed=embed_erro("Sem energia", "Você precisa de pelo menos 20 de energia pra dar aula.\n\n💡 Usa `?dormir` pra descansar.", ephemeral=True))
            return
        
        resultado = dar_aula(professor["id"], curso_id)
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("📚 Aula Ministrada", resultado["msg"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))

    @commands.command(name="assistiraula")
    async def assistiraula_cmd(self, ctx: commands.Context, aula_id: int):
        """Aluno assiste uma aula."""
        aluno = obter_dados_personagem(str(ctx.author.id))
        if not aluno:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        matricula = db.obter_matricula_ativa(aluno["id"])
        if not matricula:
            await ctx.reply(embed=embed_erro("Não matriculado", "Você precisa estar matriculado em um curso pra assistir aula.\n\n💡 Usa `?universidades` e `?matricular`.", ephemeral=True))
            return
        
        if aluno.get("energia", 100) < 10:
            await ctx.reply(embed=embed_erro("Sem energia", "Você precisa de pelo menos 10 de energia.\n\n💡 Usa `?dormir` pra descansar.", ephemeral=True))
            return
        
        resultado = assistir_aula(aluno["id"], aula_id)
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("📖 Aula Assistida", resultado["msg"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))

    @commands.command(name="minhasaulas")
    async def minhasaulas_cmd(self, ctx: commands.Context):
        """Mostra aulas que você deu (professor) ou assistiu (aluno)."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        embed = embed_padrao(f"📚 Minhas Aulas — {personagem['nome']}", cor=COR_PADRAO)
        
        if personagem.get("profissao") == "professor":
            aulas = db.listar_aulas_professor(personagem["id"], 10)
            if not aulas:
                embed.add_field(name="📚 Aulas Dadas", value="Nenhuma aula dada ainda.", inline=False)
            else:
                linhas = []
                for a in aulas:
                    linhas.append(f"**{a['tema']}**\nCurso: {a['curso_nome']} ({a['universidade']})\nAlunos: {a['alunos_presentes']} | Pagamento: ${a['pagamento']}")
                embed.add_field(name="📚 Aulas Dadas", value="\n\n".join(linhas), inline=False)
        else:
            # Mostra aulas do curso atual
            matricula = db.obter_matricula_ativa(personagem["id"])
            if matricula:
                aulas = db.listar_aulas_curso(matricula["curso_id"], 10)
                if not aulas:
                    embed.add_field(name="📖 Aulas Disponíveis", value="Nenhuma aula disponível ainda.", inline=False)
                else:
                    linhas = []
                    for a in aulas:
                        linhas.append(f"**ID {a['id']}** — {a['tema']}\nProfessor: {a['professor_nome']}\n💡 `?assistiraula {a['id']}`")
                    embed.add_field(name="📖 Aulas Disponíveis", value="\n\n".join(linhas), inline=False)
            else:
                embed.add_field(name="📖 Aulas", value="Você não tá matriculado em nenhum curso.", inline=False)
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="aulascurso")
    async def aulascurso_cmd(self, ctx: commands.Context, curso_id: int):
        """Mostra aulas de um curso específico."""
        curso = db.obter_curso(curso_id)
        if not curso:
            await ctx.reply(embed=embed_erro("Curso não encontrado", "Verifica o ID com `?universidades`.", ephemeral=True))
            return
        
        aulas = db.listar_aulas_curso(curso_id, 10)
        
        embed = embed_padrao(f"📚 Aulas — {curso['nome']} ({curso['universidade']})", cor=COR_PADRAO)
        
        if not aulas:
            embed.description = "Nenhuma aula disponível ainda. Professores podem dar aulas com `?daraula`."
        else:
            for a in aulas:
                embed.add_field(
                    name=f"📖 {a['tema']} (ID {a['id']})",
                    value=f"**Professor:** {a['professor_nome']}\n**Duração:** {a['duracao_min']}min\n**Alunos:** {a['alunos_presentes']}\n\n💡 `?assistiraula {a['id']}`",
                    inline=False,
                )
        
        await ctx.reply(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Aulas(bot))
