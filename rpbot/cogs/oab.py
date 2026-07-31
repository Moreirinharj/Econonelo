import discord
from discord.ext import commands

import database as db
from utils_ia import gerar_boletim_ocorrencia, ia_disponivel


class OAB(commands.Cog):
    """Central da OAB: recebe chamados jurídicos e distribui pra advogados
    humanos disponíveis. Quando não há nenhum, ou pra tarefas burocráticas
    (como redigir um boletim de ocorrência), uma IA assume o atendimento."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="acionaroab")
    async def acionaroab(self, ctx: commands.Context, *, descricao: str = None):
        """Abre um chamado geral na OAB pra um advogado (humano ou IA) atender."""
        personagem = db.pegar_personagem_ativo(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("Você precisa de um personagem ativo. Use `?jogar`.")
            return
        if not descricao:
            await ctx.reply("Descreva o que você precisa. Ex: `?acionaroab quero contestar uma multa`")
            return

        chamado_id = db.abrir_chamado_oab(personagem["id"], descricao)
        advogados = db.listar_advogados_disponiveis()

        embed = discord.Embed(
            title=f"📋 Chamado OAB #{chamado_id}",
            description=f"**Solicitante:** {personagem['nome']}\n**Pedido:** {descricao}",
            color=discord.Color.blurple(),
        )

        if advogados:
            nomes = ", ".join(a["nome"] for a in advogados)
            embed.set_footer(text=f"Advogados disponíveis no servidor: {nomes}")
            await ctx.reply(
                content="Seu chamado foi registrado! Um advogado humano pode assumir com "
                        f"`?assumirchamado {chamado_id}`.",
                embed=embed,
            )
        else:
            embed.set_footer(text="Nenhum advogado humano disponível no momento.")
            await ctx.reply(
                content="Nenhum advogado humano por perto agora. Se for sobre registrar uma "
                        "ocorrência, use `?boletimia <descrição>` pra nossa IA jurídica te ajudar.",
                embed=embed,
            )

    @commands.command(name="assumirchamado")
    async def assumirchamado(self, ctx: commands.Context, chamado_id: int):
        """Um advogado humano assume um chamado aberto."""
        personagem = db.pegar_personagem_ativo(str(ctx.author.id))
        if personagem is None or personagem["profissao"] not in ("advogado", "advogado_criminal"):
            await ctx.reply("Só quem tem a profissão de advogado pode assumir chamados.")
            return

        sucesso = db.assumir_chamado_oab(chamado_id, personagem["id"])
        if not sucesso:
            await ctx.reply("Esse chamado não existe ou já foi assumido.")
            return

        await ctx.reply(f"{personagem['nome']} assumiu o chamado #{chamado_id}.")

    @commands.command(name="boletimia")
    async def boletimia(self, ctx: commands.Context, *, descricao: str = None):
        """Pede pra IA jurídica redigir um boletim de ocorrência formal."""
        personagem = db.pegar_personagem_ativo(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("Você precisa de um personagem ativo. Use `?jogar`.")
            return
        if not descricao:
            await ctx.reply("Descreva o que aconteceu. Ex: `?boletimia fui roubado na saída do mercado`")
            return

        if not ia_disponivel():
            await ctx.reply(
                "⚠️ A IA jurídica ainda não está configurada nesse servidor "
                "(falta `ANTHROPIC_API_KEY` no `.env`)."
            )
            return

        async with ctx.typing():
            texto_formal = gerar_boletim_ocorrencia(personagem["nome"], descricao)

        boletim_id = db.salvar_boletim(personagem["id"], descricao, texto_formal)

        embed = discord.Embed(
            title=f"🚓 Boletim de Ocorrência #{boletim_id}",
            description=texto_formal,
            color=discord.Color.dark_gold(),
        )
        embed.set_footer(text=f"Registrado por {personagem['nome']} — redigido pela IA jurídica")
        await ctx.reply(embed=embed)

    @commands.command(name="meusboletins")
    async def meusboletins(self, ctx: commands.Context):
        """Lista os boletins já registrados pelo seu personagem ativo."""
        personagem = db.pegar_personagem_ativo(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("Você precisa de um personagem ativo. Use `?jogar`.")
            return

        boletins = db.listar_boletins(personagem["id"])
        if not boletins:
            await ctx.reply("Você ainda não registrou nenhum boletim.")
            return

        linhas = [f"**#{b['id']}** — {b['descricao_original'][:50]}" for b in boletins[:10]]
        await ctx.reply("\n".join(linhas))


async def setup(bot: commands.Bot):
    await bot.add_cog(OAB(bot))
