import discord
from discord.ext import commands

import database as db
from utils import formatar_moeda
from data.config import (
    MAX_PERSONAGENS, IDADE_MINIMA, IDADE_MAXIMA, CORES_PELE, TIPOS_CABELO,
    CORES_CABELO, IDADE_CABELO_BRANCO, RELIGIOES, REGIOES, PROFISSOES,
    TIMEOUT_CONFIRMACAO,
)

# guarda o progresso de criação de cada usuário enquanto ele não termina o wizard
SESSOES_CRIACAO = {}


class SelecaoView(discord.ui.View):
    """View genérica de um único select, usada em cada etapa do wizard."""

    def __init__(self, opcoes, proxima_etapa, timeout=TIMEOUT_CONFIRMACAO):
        super().__init__(timeout=timeout)
        select = discord.ui.Select(
            placeholder="Escolha uma opção...",
            options=[discord.SelectOption(label=o) for o in opcoes[:25]],
        )

        async def callback(interaction: discord.Interaction):
            await proxima_etapa(interaction, select.values[0])

        select.callback = callback
        self.add_item(select)


class NomeIdadeModal(discord.ui.Modal, title="Criação de personagem"):
    nome = discord.ui.TextInput(label="Nome do personagem", max_length=32)
    idade = discord.ui.TextInput(label=f"Idade ({IDADE_MINIMA} a {IDADE_MAXIMA})", max_length=3)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            idade_int = int(self.idade.value)
        except ValueError:
            await interaction.response.send_message("Idade inválida, use apenas números.", ephemeral=True)
            return

        if not (IDADE_MINIMA <= idade_int <= IDADE_MAXIMA):
            await interaction.response.send_message(
                f"A idade precisa ser entre {IDADE_MINIMA} e {IDADE_MAXIMA}.", ephemeral=True
            )
            return

        user_id = str(interaction.user.id)
        SESSOES_CRIACAO[user_id] = {"nome": self.nome.value, "idade": idade_int}

        await interaction.response.send_message(
            "Agora escolha a **cor de pele** do seu personagem:",
            view=SelecaoView(CORES_PELE, etapa_tipo_cabelo),
            ephemeral=True,
        )


async def etapa_tipo_cabelo(interaction: discord.Interaction, cor_pele: str):
    user_id = str(interaction.user.id)
    SESSOES_CRIACAO[user_id]["cor_pele"] = cor_pele
    await interaction.response.edit_message(
        content="Agora escolha o **tipo de cabelo**:",
        view=SelecaoView(TIPOS_CABELO, etapa_cor_cabelo),
    )


async def etapa_cor_cabelo(interaction: discord.Interaction, tipo_cabelo: str):
    user_id = str(interaction.user.id)
    SESSOES_CRIACAO[user_id]["tipo_cabelo"] = tipo_cabelo
    await interaction.response.edit_message(
        content="Agora escolha a **cor do cabelo**:",
        view=SelecaoView(CORES_CABELO, etapa_regiao),
    )


async def etapa_regiao(interaction: discord.Interaction, cor_cabelo: str):
    user_id = str(interaction.user.id)
    sessao = SESSOES_CRIACAO[user_id]

    if sessao["idade"] >= IDADE_CABELO_BRANCO:
        cor_cabelo = f"{cor_cabelo} Esbranquiçado"
    sessao["cor_cabelo"] = cor_cabelo

    await interaction.response.edit_message(
        content="Agora escolha a **região do Brasil** onde seu personagem mora:",
        view=SelecaoView(list(REGIOES.keys()), etapa_estado),
    )


async def etapa_estado(interaction: discord.Interaction, regiao: str):
    estados_da_regiao = REGIOES[regiao]

    async def proxima(interaction2: discord.Interaction, estado: str):
        await etapa_religiao(interaction2, estado)

    await interaction.response.edit_message(
        content=f"Agora escolha o **estado** ({regiao}):",
        view=SelecaoView(estados_da_regiao, proxima),
    )


async def etapa_religiao(interaction: discord.Interaction, estado: str):
    user_id = str(interaction.user.id)
    SESSOES_CRIACAO[user_id]["estado"] = estado

    await interaction.response.edit_message(
        content="Por último, escolha a **religião** do seu personagem:",
        view=SelecaoView(RELIGIOES, etapa_confirmar),
    )


async def etapa_confirmar(interaction: discord.Interaction, religiao: str):
    user_id = str(interaction.user.id)
    sessao = SESSOES_CRIACAO[user_id]
    sessao["religiao"] = religiao

    resumo = (
        f"**Nome:** {sessao['nome']}\n"
        f"**Idade:** {sessao['idade']}\n"
        f"**Cor de pele:** {sessao['cor_pele']}\n"
        f"**Cabelo:** {sessao['cor_cabelo']} ({sessao['tipo_cabelo']})\n"
        f"**Estado:** {sessao['estado']}\n"
        f"**Religião:** {sessao['religiao']}"
    )

    view = discord.ui.View(timeout=TIMEOUT_CONFIRMACAO)
    botao_confirmar = discord.ui.Button(label="Confirmar", style=discord.ButtonStyle.success)
    botao_cancelar = discord.ui.Button(label="Cancelar", style=discord.ButtonStyle.danger)

    async def confirmar_callback(interaction2: discord.Interaction):
        personagem_id = db.criar_personagem(user_id, sessao)
        SESSOES_CRIACAO.pop(user_id, None)
        await interaction2.response.edit_message(
            content=f"🎉 Personagem **{sessao['nome']}** criado com sucesso! (ID #{personagem_id})\n"
                    f"Use `?info` pra ver os detalhes.",
            view=None,
        )

    async def cancelar_callback(interaction2: discord.Interaction):
        SESSOES_CRIACAO.pop(user_id, None)
        await interaction2.response.edit_message(content="Criação cancelada.", view=None)

    botao_confirmar.callback = confirmar_callback
    botao_cancelar.callback = cancelar_callback
    view.add_item(botao_confirmar)
    view.add_item(botao_cancelar)

    await interaction.response.edit_message(
        content=f"Confira os dados do seu personagem:\n\n{resumo}",
        view=view,
    )


class Personagem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="jogar")
    async def jogar(self, ctx: commands.Context):
        """Inicia a criação de um novo personagem."""
        user_id = str(ctx.author.id)
        if db.contar_personagens(user_id) >= MAX_PERSONAGENS:
            await ctx.reply(
                f"Você já atingiu o limite de {MAX_PERSONAGENS} personagens. "
                f"Use `?meuspersonagens` pra ver os seus."
            )
            return

        view = discord.ui.View(timeout=TIMEOUT_CONFIRMACAO)
        botao = discord.ui.Button(label="Criar personagem", style=discord.ButtonStyle.primary)

        async def abrir_modal(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("Esse botão não é seu!", ephemeral=True)
                return
            await interaction.response.send_modal(NomeIdadeModal())

        botao.callback = abrir_modal
        view.add_item(botao)

        await ctx.reply(
            "Vamos começar a jornada do seu personagem! Clique no botão abaixo:",
            view=view,
        )

    @commands.command(name="mudarperson")
    async def mudarperson(self, ctx: commands.Context):
        """Cria outro personagem (não apaga os anteriores)."""
        await self.jogar(ctx)

    @commands.command(name="meuspersonagens")
    async def meuspersonagens(self, ctx: commands.Context):
        """Lista todos os seus personagens."""
        personagens = db.listar_personagens(str(ctx.author.id))
        if not personagens:
            await ctx.reply("Você ainda não tem nenhum personagem. Use `?jogar` pra criar um!")
            return

        linhas = []
        for p in personagens:
            marcador = "✅ (ativo)" if p["ativo"] else ""
            linhas.append(f"**#{p['id']}** — {p['nome']}, {p['idade']} anos {marcador}")

        embed = discord.Embed(
            title="Seus personagens",
            description="\n".join(linhas),
            color=discord.Color.blue(),
        )
        embed.set_footer(text="Use ?usar <id> pra trocar de personagem ativo")
        await ctx.reply(embed=embed)

    @commands.command(name="usar")
    async def usar(self, ctx: commands.Context, personagem_id: int):
        """Troca qual personagem está ativo."""
        sucesso = db.definir_personagem_ativo(str(ctx.author.id), personagem_id)
        if not sucesso:
            await ctx.reply("Personagem não encontrado. Confira o ID com `?meuspersonagens`.")
            return
        await ctx.reply(f"Personagem #{personagem_id} agora está ativo.")

    @commands.command(name="info")
    async def info(self, ctx: commands.Context):
        """Mostra as informações do seu personagem ativo."""
        personagem = db.pegar_personagem_ativo(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("Você não tem um personagem ativo. Use `?jogar` pra criar um.")
            return

        profissao_info = PROFISSOES.get(personagem["profissao"])
        profissao_texto = (
            f"{profissao_info['emoji']} {personagem['profissao'].replace('_', ' ').title()}"
            if profissao_info else "Nenhuma (use `?profissoes`)"
        )

        relacoes = db.listar_familia(personagem["id"])
        familiares_texto = "Nenhum ainda"
        if relacoes:
            partes = []
            for r in relacoes:
                outro_id = r["alvo_id"] if r["personagem_id"] == personagem["id"] else r["personagem_id"]
                outro = db.pegar_personagem_por_id(outro_id)
                nome_outro = outro["nome"] if outro else "?"
                partes.append(f"{r['tipo'].capitalize()}: {nome_outro}")
            familiares_texto = "\n".join(partes)

        embed = discord.Embed(
            title=f"{personagem['nome']} ({personagem['idade']} anos)",
            color=discord.Color.gold(),
        )
        embed.add_field(name="Cor de pele", value=personagem["cor_pele"], inline=True)
        embed.add_field(name="Cabelo", value=f"{personagem['cor_cabelo']} ({personagem['tipo_cabelo']})", inline=True)
        embed.add_field(name="Estado", value=personagem["estado"], inline=True)
        embed.add_field(name="Religião", value=personagem["religiao"], inline=True)
        embed.add_field(name="Profissão", value=profissao_texto, inline=True)
        embed.add_field(name="Nível / XP", value=f"{personagem['nivel']} / {personagem['xp']}", inline=True)
        embed.add_field(name="Saldo bancário", value=formatar_moeda(personagem["saldo"]), inline=False)
        embed.add_field(name="Família / relações", value=familiares_texto, inline=False)

        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Personagem(bot))
