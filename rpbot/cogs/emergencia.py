import discord
from discord.ext import commands

from data.constantes import (
    EMOJI_POLICIA, EMOJI_SAMU, EMOJI_PRISAO,
    MSG_SEM_PERSONAGEM, MSG_PERSONAGEM_PRESO,
)
from utils.verificar_personagem import verificar_personagem, verificar_personagem_e_profissao
from utils.comando_ajuda import mostrar_ajuda_cpf, mostrar_ajuda_pedido, validar_cpf
from utils.embeds import embed_emergencia, embed_sucesso, embed_aviso, embed_erro
from services.personagem_service import obter_dados_personagem
from services.emergencia_service import EmergenciaService

emergencia_service = EmergenciaService()


class Emergencia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _abrir_chamado(self, ctx, tipo: str, descricao: str, profissoes_alvo: list, nome_servico: str):
        import database as db
        
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return

        if personagem["preso"]:
            await ctx.reply(MSG_PERSONAGEM_PRESO)
            return

        chamado_id = emergencia_service.abrir_chamado(personagem["id"], tipo, descricao)
        profissionais = db.listar_profissionais(profissoes_alvo)

        embed = embed_emergencia(
            f"Chamado {tipo} #{chamado_id} — {nome_servico}",
            f"**Solicitante:** {personagem['nome']}\n**Descrição:** {descricao}",
        )

        if profissionais:
            nomes = ", ".join(p["nome"] for p in profissionais)
            embed.set_footer(text=f"Disponíveis: {nomes} — use ?atender {chamado_id}")
        else:
            embed.set_footer(text="Nenhum profissional dessa área tem personagem no momento.")

        await ctx.reply(embed=embed)

    @commands.command(name="acionar192")
    async def acionar192(self, ctx: commands.Context, *, descricao: str = None):
        if not descricao:
            await ctx.reply(embed=embed_aviso("Descreva a emergência", "Ex: `?acionar192 fui atropelado`"))
            return
        await self._abrir_chamado(ctx, "192", descricao, ["samu"], "SAMU")

    @commands.command(name="acionar190")
    async def acionar190(self, ctx: commands.Context, *, descricao: str = None):
        if not descricao:
            await ctx.reply(embed=embed_aviso("Descreva a ocorrência", "Ex: `?acionar190 fui roubado na rua`"))
            return
        await self._abrir_chamado(ctx, "190", descricao, ["policial_militar"], "Polícia Militar")

    @commands.command(name="atender")
    async def atender(self, ctx: commands.Context, chamado_id: int = None):
        """Atende um chamado de emergência."""
        # 1. Mostrar ajuda se não passar o ID
        if chamado_id is None:
            await ctx.reply(embed=embed_aviso(
                "Uso do comando",
                "Use: `?atender <chamado_id>`\n\n"
                "Exemplo: `?atender 5`\n\n"
                "Use `?chamados` para ver os chamados abertos."
            ), ephemeral=True)
            return

        # 2. Verificar personagem vinculado ao CPF/Discord ID
        personagem = await verificar_personagem(ctx)
        if not personagem:
            return

        # 3. Verificar profissão (Apenas PM, PC e SAMU podem atender)
        profissao = personagem.get('profissao', '').lower()
        if profissao not in ['policial_militar', 'policial_civil', 'samu']:
            await ctx.reply(embed=embed_erro(
                "Profissão não autorizada",
                f"Apenas **Policial** ou **SAMU** podem atender chamados.\nSua profissão: `{profissao or 'nenhuma'}`"
            ), ephemeral=True)
            return

        # 4. Buscar o chamado
        chamado = db.obter_chamado(chamado_id)
        if not chamado:
            await ctx.reply(embed=embed_erro("Chamado não encontrado", f"O chamado ID {chamado_id} não existe."), ephemeral=True)
            return

        if chamado.get('status') != 'aberto':
            await ctx.reply(embed=embed_erro("Chamado indisponível", f"O chamado ID {chamado_id} já está {chamado.get('status')}."), ephemeral=True)
            return

        # 5. Atender o chamado
        db.atender_chamado(chamado_id, personagem['id'])
        
        await ctx.reply(embed=embed_sucesso(
            "Chamado atendido!",
            f"Você (**{personagem['nome']}**) está a caminho do chamado ID {chamado_id}."
        ), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Emergencia(bot))
