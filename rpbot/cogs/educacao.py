import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_INFO, MSG_SEM_PERSONAGEM
from utils.comando_ajuda import mostrar_ajuda_cpf, mostrar_ajuda_pedido, validar_cpf
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info
from services.personagem_service import obter_dados_personagem
from services.educacao_service import popular_cursos, fazer_vestibular, matricular_no_curso, estudar_semestre, trancar_matricula
from services.viagem_service import ESTADOS_DISPONIVEIS
import database as db


def _filtro_por_estado(item, estado_atual):
    """Filtra item por estado, aceitando UF ou nome completo."""
    cidade = item.get("cidade", "")
    mapeamento = {
        "SP": ["São Paulo"],
        "RJ": ["Rio de Janeiro"],
        "MG": ["Minas Gerais", "Belo Horizonte"],
        "PR": ["Paraná", "Curitiba"],
        "RS": ["Rio Grande do Sul", "Porto Alegre"],
        "BA": ["Bahia", "Salvador"],
    }
    cidades_validas = mapeamento.get(estado_atual, [estado_atual])
    return any(c in cidade for c in cidades_validas)

class Educacao(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="universidades", aliases=["cursos"])
    async def universidades_cmd(self, ctx: commands.Context, universidade: str = None):
        """Lista cursos disponíveis."""
        cursos = db.listar_cursos(universidade=universidade)
        # Filtra apenas cursos de universidades do estado atual
        cursos_filtrados = []
        for c in cursos:
            uf_uni = next((uf for uf, dados in ESTADOS_DISPONIVEIS.items() if dados['nome'] == c['universidade'] or c['universidade'].startswith(dados['nome'])), None)
            if not uf_uni or uf_uni == estado_atual:
                cursos_filtrados.append(c)
        cursos = cursos_filtrados
        if not cursos:
            await ctx.reply(embed=embed_info("🎓 Sem cursos", "Nenhum curso cadastrado. Admin: use `?populacursos`.", ephemeral=True))
            return
        embed = embed_padrao("🎓 Cursos Disponíveis", cor=COR_PADRAO)
        por_uni = {}
        for c in cursos:
            por_uni.setdefault(c["universidade"], []).append(c)
        for uni, lista in por_uni.items():
            linhas = [f"• **{c['nome']}** (ID {c['id']}) — {c['nivel']} — {c['duracao_semestres']} sem — ${c['mensalidade']}/mês" for c in lista[:8]]
            embed.add_field(name=f"🏛️ {uni}", value="\n".join(linhas), inline=False)
        embed.set_footer(text="Use ?vestibular <id> pra tentar entrar")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="vestibular")
    async def vestibular_cmd(self, ctx: commands.Context, curso_id: int):
        """Faz vestibular pra um curso."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        estado_atual = personagem.get("estado_atual") or personagem.get("estado")
        # Filtra cursos que pertencem a universidades do estado atual (simplificado: checa se a universidade tem cursos)
        res = fazer_vestibular(personagem["id"], curso_id)
        if not res["sucesso"]:
            await ctx.reply(embed=embed_erro("Erro", res["msg"], ephemeral=True))
            return
        cor = COR_SUCESSO if res["aprovado"] else COR_ERRO
        embed = discord.Embed(title="📝 Resultado do Vestibular", description=res["msg"], color=cor)
        embed.add_field(name="Curso", value=res["curso"]["nome"], inline=True)
        embed.add_field(name="Universidade", value=res["curso"]["universidade"], inline=True)
        if res["aprovado"]:
            embed.set_footer(text="Use ?matricular <id> pra se matricular")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="matricular")
    async def matricular_cmd(self, ctx: commands.Context, curso_id: int):
        """Matricula no curso (paga 1ª mensalidade)."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        res = matricular_no_curso(personagem["id"], curso_id)
        if res["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Matrícula Confirmada", res["msg"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", res["msg"], ephemeral=True))

    @commands.command(name="estudar")
    async def estudar_cmd(self, ctx: commands.Context):
        """Estuda um semestre do seu curso."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        res = estudar_semestre(personagem["id"])
        if not res["sucesso"]:
            await ctx.reply(embed=embed_erro("Erro", res["msg"], ephemeral=True))
            return
        if res.get("formatura"):
            await ctx.reply(embed=embed_sucesso("🎓 FORMATURA!", res["msg"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_info("📚 Semestre concluído", res["msg"], ephemeral=True))

    @commands.command(name="minhaseducacao", aliases=["historico"])
    async def minhaseducacao_cmd(self, ctx: commands.Context):
        """Mostra seu histórico educacional."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        mats = db.listar_matriculas_personagem(personagem["id"])
        embed = embed_padrao(f"🎓 Histórico de {personagem['nome']}", cor=COR_PADRAO)
        embed.add_field(name="📜 Escolaridade atual", value=personagem.get("escolaridade", "nenhuma").title(), inline=False)
        if not mats:
            embed.add_field(name="📚 Cursos", value="Nenhum curso feito.", inline=False)
        else:
            for m in mats:
                status_emoji = {"matriculado": "📖", "formado": "🎓", "trancado": "⏸️"}.get(m["status"], "❓")
                embed.add_field(
                    name=f"{status_emoji} {m['curso_nome']} — {m['universidade']}",
                    value=f"**Status:** {m['status']}\n**Semestre:** {m['semestre_atual']}\n**Média:** {m['nota_media']}/10",
                    inline=True
                )
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="trancar")
    async def trancar_cmd(self, ctx: commands.Context):
        """Tranca sua matrícula atual."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        res = trancar_matricula(personagem["id"])
        if res["sucesso"]:
            await ctx.reply(embed=embed_sucesso("Matrícula trancada", res["msg"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", res["msg"], ephemeral=True))

    @commands.command(name="populacursos")
    @commands.has_permissions(administrator=True)
    async def populacursos_cmd(self, ctx: commands.Context):
        """Popula cursos reais (só admin)."""
        count = popular_cursos()
        if count == 0:
            await ctx.reply(embed=embed_info("Já populado", "Cursos já existem no banco.", ephemeral=True))
        else:
            await ctx.reply(embed=embed_sucesso("Cursos populados!", f"{count} cursos reais cadastrados.", ephemeral=True))

async def setup(bot: commands.Bot):
    await bot.add_cog(Educacao(bot))

    @commands.command(name="populacursos")
    @commands.has_permissions(administrator=True)
    async def populacursos_cmd(self, ctx: commands.Context):
        """Popula o banco com cursos reais (só admin)."""
        from services.educacao_service import popular_cursos
        
        count = popular_cursos()
        if count == 0:
            await ctx.reply("ℹ️ Cursos já foram populados anteriormente.", ephemeral=True)
        else:
            await ctx.reply(f"✅ {count} cursos foram adicionados ao banco!", ephemeral=True)
