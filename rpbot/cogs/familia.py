import discord
from discord.ext import commands

import database as db
from data.config import TIMEOUT_CONFIRMACAO

# tipos que exigem processo da OAB pra remover (não pode ser removido sem consentimento)
TIPOS_PROTEGIDOS = {"pai", "mae", "filho", "filha"}

NOME_TIPO = {
    "pai": "pai", "mae": "mãe", "filho": "filho", "filha": "filha",
    "amante": "amante", "amigo": "amigo(a)",
}


class ConfirmarRelacaoView(discord.ui.View):
    def __init__(self, pedido_id: int, alvo_user_id: int, tipo: str, nome_solicitante: str, nome_alvo_personagem: str):
        super().__init__(timeout=TIMEOUT_CONFIRMACAO)
        self.pedido_id = pedido_id
        self.alvo_user_id = alvo_user_id
        self.tipo = tipo
        self.nome_solicitante = nome_solicitante
        self.nome_alvo_personagem = nome_alvo_personagem

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.alvo_user_id:
            await interaction.response.send_message("Esse pedido não é seu!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.success)
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        db.responder_pedido_relacao(self.pedido_id, aceitar=True)
        await interaction.response.edit_message(
            content=f"✅ {self.nome_alvo_personagem} aceitou ser **{NOME_TIPO[self.tipo]}** de {self.nome_solicitante}!",
            view=None,
        )

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.danger)
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button):
        db.responder_pedido_relacao(self.pedido_id, aceitar=False)
        await interaction.response.edit_message(
            content=f"❌ {self.nome_alvo_personagem} recusou o pedido.",
            view=None,
        )


class Familia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _pegar_personagem_ou_avisar(self, ctx, membro: discord.Member = None):
        """Retorna (meu_personagem, personagem_alvo) ou None se algo faltar (já avisando o usuário)."""
        meu = db.pegar_personagem_ativo(str(ctx.author.id))
        if meu is None:
            await ctx.reply("Você precisa de um personagem ativo. Use `?jogar`.")
            return None, None

        if membro is None:
            await ctx.reply("Marque um usuário ou passe o ID dele. Ex: `?adcpai @usuario`")
            return None, None

        if membro.id == ctx.author.id:
            await ctx.reply("Você não pode adicionar a si mesmo.")
            return None, None

        alvo = db.pegar_personagem_ativo(str(membro.id))
        if alvo is None:
            await ctx.reply(f"{membro.display_name} não tem um personagem ativo.")
            return None, None

        return meu, alvo

    async def _adicionar_relacao(self, ctx, membro: discord.Member, tipo: str):
        meu, alvo = await self._pegar_personagem_ou_avisar(ctx, membro)
        if meu is None:
            return

        if tipo in ("pai", "mae") and db.contar_pais(meu["id"]) >= 2:
            await ctx.reply("Seu personagem já tem 2 pais/mães. Remova um antes de adicionar outro.")
            return

        if db.ja_existe_relacao(meu["id"], alvo["id"], tipo):
            await ctx.reply("Já existe um pedido ou relação desse tipo com essa pessoa.")
            return

        pedido_id = db.criar_pedido_relacao(meu["id"], alvo["id"], tipo)

        view = ConfirmarRelacaoView(pedido_id, membro.id, tipo, meu["nome"], alvo["nome"])
        await ctx.reply(
            f"{membro.mention}, {meu['nome']} quer te adicionar como **{NOME_TIPO[tipo]}** "
            f"(seu personagem: {alvo['nome']}). Você aceita?",
            view=view,
        )

    async def _remover_direta(self, ctx, membro: discord.Member, tipo: str):
        """Remove amigo/amante sem precisar de consentimento."""
        meu, alvo = await self._pegar_personagem_ou_avisar(ctx, membro)
        if meu is None:
            return

        removeu = db.remover_relacao_direta(meu["id"], alvo["id"], tipo)
        if removeu:
            await ctx.reply(f"Removido: {alvo['nome']} não é mais seu(sua) {NOME_TIPO[tipo]}.")
        else:
            await ctx.reply("Não encontrei essa relação.")

    async def _abrir_processo_remocao(self, ctx, membro: discord.Member, tipo: str):
        """Pai/mãe/filho/filha só saem via processo da OAB."""
        meu, alvo = await self._pegar_personagem_ou_avisar(ctx, membro)
        if meu is None:
            return

        processo_id = db.abrir_processo_oab(meu["id"], alvo["id"], tipo)
        await ctx.reply(
            f"📋 Processo #{processo_id} aberto na OAB pra remover {alvo['nome']} como "
            f"**{NOME_TIPO[tipo]}** do seu personagem.\n"
            f"Um advogado vai encaminhar ao juiz — isso ainda depende do sistema de "
            f"Justiça (Fase 2). Por enquanto, um administrador pode resolver manualmente "
            f"com `?resolveroab {processo_id} aprovar`."
        )

    # ------------------ ADICIONAR ------------------
    @commands.command(name="adcpai")
    async def adcpai(self, ctx, membro: discord.Member = None):
        await self._adicionar_relacao(ctx, membro, "pai")

    @commands.command(name="adcmae")
    async def adcmae(self, ctx, membro: discord.Member = None):
        await self._adicionar_relacao(ctx, membro, "mae")

    @commands.command(name="adcfilho")
    async def adcfilho(self, ctx, membro: discord.Member = None):
        await self._adicionar_relacao(ctx, membro, "filho")

    @commands.command(name="adcfilha")
    async def adcfilha(self, ctx, membro: discord.Member = None):
        await self._adicionar_relacao(ctx, membro, "filha")

    @commands.command(name="adcamante")
    async def adcamante(self, ctx, membro: discord.Member = None):
        await self._adicionar_relacao(ctx, membro, "amante")

    @commands.command(name="adcamigo")
    async def adcamigo(self, ctx, membro: discord.Member = None):
        await self._adicionar_relacao(ctx, membro, "amigo")

    # ------------------ REMOVER (sem consentimento) ------------------
    @commands.command(name="removeamante")
    async def removeamante(self, ctx, membro: discord.Member = None):
        await self._remover_direta(ctx, membro, "amante")

    @commands.command(name="removeamigo")
    async def removeamigo(self, ctx, membro: discord.Member = None):
        await self._remover_direta(ctx, membro, "amigo")

    # ------------------ REMOVER (precisa de processo) ------------------
    @commands.command(name="removepai")
    async def removepai(self, ctx, membro: discord.Member = None):
        await self._abrir_processo_remocao(ctx, membro, "pai")

    @commands.command(name="removemae")
    async def removemae(self, ctx, membro: discord.Member = None):
        await self._abrir_processo_remocao(ctx, membro, "mae")

    @commands.command(name="removefilho")
    async def removefilho(self, ctx, membro: discord.Member = None):
        await self._abrir_processo_remocao(ctx, membro, "filho")

    @commands.command(name="removefilha")
    async def removefilha(self, ctx, membro: discord.Member = None):
        await self._abrir_processo_remocao(ctx, membro, "filha")

    # ------------------ ADMIN: resolver processo (placeholder da Fase 2) ------------------
    @commands.command(name="resolveroab")
    @commands.has_permissions(administrator=True)
    async def resolveroab(self, ctx, processo_id: int, decisao: str):
        decisao = decisao.lower()
        if decisao not in ("aprovar", "negar"):
            await ctx.reply("Use `aprovar` ou `negar`.")
            return
        processo = db.resolver_processo_oab(processo_id, aprovar=(decisao == "aprovar"))
        if processo is None:
            await ctx.reply("Processo não encontrado.")
            return
        await ctx.reply(f"Processo #{processo_id} foi **{decisao}do**.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Familia(bot))
