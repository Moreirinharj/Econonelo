import discord
from discord.ext import commands
import time

import database as db
from data.config import PROFISSOES, TIMEOUT_CONFIRMACAO
from data.provas import PROVAS, NOTA_MINIMA


class RespostaView(discord.ui.View):
    def __init__(self, opcoes, callback_resposta, timeout=TIMEOUT_CONFIRMACAO):
        super().__init__(timeout=timeout)
        letras = ["A", "B", "C", "D"]
        for i, opcao in enumerate(opcoes):
            botao = discord.ui.Button(label=f"{letras[i]}) {opcao}"[:80], style=discord.ButtonStyle.secondary)

            async def callback(interaction: discord.Interaction, indice=i):
                await callback_resposta(interaction, indice)

            botao.callback = callback
            self.add_item(botao)


class Provas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.em_andamento = {}
        self.cooldown_provas = {}  # {user_id: timestamp}

    @commands.command(name="fazerprova")
    async def fazerprova(self, ctx: commands.Context, profissao: str = None):
        personagem = db.pegar_personagem_ativo(str(ctx.author.id))
        if personagem is None:
            await ctx.reply("Você precisa de um personagem ativo. Use ?jogar.")
            return

        if not profissao or profissao.lower() not in PROVAS:
            opcoes = ", ".join(PROVAS.keys())
            await ctx.reply(f"Profissões com prova disponível: {opcoes}")
            return

        profissao = profissao.lower()
        user_id = str(ctx.author.id)

        if user_id in self.em_andamento:
            await ctx.reply("Você já tem uma prova em andamento. Termine ela antes de iniciar outra.")
            return

        # ✅ CORREÇÃO: Cooldown de 1 hora entre provas
        cooldown = 3600  # 1 hora
        ultimo_teste = self.cooldown_provas.get(user_id, 0)
        if time.time() - ultimo_teste < cooldown:
            minutos_restantes = int((cooldown - (time.time() - ultimo_teste)) / 60)
            await ctx.reply(f"Você já fez uma prova recentemente. Espera mais **{minutos_restantes} minutos** antes de tentar outra.")
            return

        self.em_andamento[user_id] = {"profissao": profissao, "indice": 0, "acertos": 0, "personagem_id": personagem["id"]}
        self.cooldown_provas[user_id] = time.time()
        await self._enviar_pergunta(ctx.channel, user_id)

    async def _enviar_pergunta(self, canal, user_id):
        progresso = self.em_andamento[user_id]
        perguntas = PROVAS[progresso["profissao"]]
        indice = progresso["indice"]
        pergunta = perguntas[indice]

        async def callback_resposta(interaction: discord.Interaction, escolha: int):
            if str(interaction.user.id) != user_id:
                await interaction.response.send_message("Essa prova não é sua!", ephemeral=True)
                return

            correta = pergunta["correta"] == escolha
            if correta:
                progresso["acertos"] += 1

            progresso["indice"] += 1
            texto = "✅ Certa!" if correta else "❌ Errada."

            if progresso["indice"] >= len(perguntas):
                await interaction.response.edit_message(content=texto, view=None)
                await self._finalizar_prova(interaction.channel, user_id)
            else:
                await interaction.response.edit_message(content=texto, view=None)
                await self._enviar_pergunta(interaction.channel, user_id)

        view = RespostaView(pergunta["opcoes"], callback_resposta)
        await canal.send(
            content=f"Pergunta {indice + 1}/{len(perguntas)}: {pergunta['pergunta']}",
            view=view,
        )

    async def _finalizar_prova(self, canal, user_id):
        progresso = self.em_andamento.pop(user_id)
        acertos = progresso["acertos"]
        total = len(PROVAS[progresso["profissao"]])
        profissao = progresso["profissao"]
        nome_bonito = profissao.replace("_", " ").title()

        if acertos >= NOTA_MINIMA:
            db.definir_profissao_personagem(progresso["personagem_id"], profissao)
            await canal.send(
                f"🎉 Você acertou {acertos}/{total} e foi aprovado! Agora sua profissão é "
                f"{nome_bonito}. Use ?trabalhar se a profissão já tiver tarefas."
            )
        else:
            await canal.send(
                f"😕 Você acertou {acertos}/{total} (mínimo é {NOTA_MINIMA}). Não foi dessa vez — "
                f"pode tentar de novo com ?fazerprova {profissao} (depois de 1 hora)."
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Provas(bot))
