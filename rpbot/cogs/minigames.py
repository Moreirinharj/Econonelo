import discord
from discord.ext import commands
import time

from data.constantes import (
    COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO,
    MSG_SEM_PERSONAGEM, EMOJI_TRABALHO,
)
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_aviso
from services.personagem_service import obter_dados_personagem
from services.minigames_service import iniciar_minigame, MINIGAMES_POR_PROFISSAO
from services.mensagens_service import mensagem_sucesso_trabalho, mensagem_falhou_minigame, mensagem_foi_preso
from data import balanceamento as bal


class MinigameView(discord.ui.View):
    def __init__(self, opcoes, callback_resposta, timeout=60):
        super().__init__(timeout=timeout)
        letras = ["A", "B", "C", "D"]
        for i, opcao in enumerate(opcoes):
            if i >= 4:
                break
            botao = discord.ui.Button(
                label=f"{letras[i]}) {opcao}"[:80],
                style=discord.ButtonStyle.primary,
            )

            async def callback(interaction: discord.Interaction, indice=i):
                await callback_resposta(interaction, indice)

            botao.callback = callback
            self.add_item(botao)


class Minigames(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.minigames_ativos = {}

    @commands.command(name="trabalhar", aliases=["work"])
    async def trabalhar_cmd(self, ctx: commands.Context):
        """Inicia o minigame da sua profissão."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return

        if personagem.get("preso"):
            await ctx.reply(embed=embed_erro("Você está preso!", "Não pode trabalhar na prisão."))
            return

        profissao = personagem.get("profissao")
        if not profissao:
            await ctx.reply(embed=embed_erro("Sem profissão", "Use `?escolherprofissao` primeiro."))
            return

        # ✅ CORREÇÃO: Verifica cooldown
        salario_info = bal.obter_salario(profissao)
        cooldown_minutos = salario_info.get("cooldown_min", 15)
        ultimo_trabalho = personagem.get("ultimo_trabalho", 0)
        tempo_passado = time.time() - ultimo_trabalho
        tempo_cooldown = cooldown_minutos * 60
        
        if tempo_passado < tempo_cooldown:
            tempo_restante = int((tempo_cooldown - tempo_passado) / 60)
            await ctx.reply(embed=embed_aviso(
                "Calma aí, parceiro!",
                f"Você ainda tá cansado do último trabalho. Espera mais **{tempo_restante} minutos**.\n\n"
                f"💡 Usa `?status` pra ver como tu tá, ou `?descansar` se tiver com energia baixa."
            ))
            return

        if profissao not in MINIGAMES_POR_PROFISSAO:
            await ctx.reply(embed=embed_aviso("Sem minigame", "Sua profissão ainda não tem minigame. Use `?trabalharrapido`."))
            return

        user_id = str(ctx.author.id)
        if user_id in self.minigames_ativos:
            await ctx.reply(embed=embed_aviso("Minigame em andamento", "Termine o minigame atual antes de iniciar outro."))
            return

        dados = iniciar_minigame(personagem["id"], profissao)
        if not dados["sucesso"]:
            await ctx.reply(embed=embed_erro("Erro", dados["mensagem"]))
            return

        self.minigames_ativos[user_id] = dados

        embed = embed_padrao(
            f"{EMOJI_TRABALHO} {dados['nome_minigame']} — {profissao.replace('_', ' ').title()}",
            cor=COR_PADRAO,
        )
        embed.description = f"**Situação:** {dados['texto']}\n\nEscolha a melhor ação:"

        async def callback_resposta(interaction: discord.Interaction, escolha: int):
            if str(interaction.user.id) != user_id:
                await interaction.response.send_message("Esse minigame não é seu!", ephemeral=True)
                return

            dados_mg = self.minigames_ativos.pop(user_id, None)
            if dados_mg is None:
                await interaction.response.send_message("Minigame expirou.", ephemeral=True)
                return

            prof = dados_mg.get("profissao", personagem["profissao"])
            mg_info = MINIGAMES_POR_PROFISSAO.get(prof)
            if not mg_info:
                await interaction.response.send_message("Erro interno.", ephemeral=True)
                return

            kwargs = {"personagem_id": personagem["id"], "escolha": escolha}
            if "correta" in dados_mg:
                kwargs["correta"] = dados_mg["correta"]
            if "cenario_correto" in dados_mg:
                kwargs["cenario_correto"] = dados_mg["cenario_correto"]
            if "reward" in dados_mg:
                kwargs["reward"] = dados_mg["reward"]
            if "risco" in dados_mg:
                kwargs["risco"] = dados_mg["risco"]

            resolver_func = mg_info["resolver"]
            try:
                resultado = resolver_func(**kwargs)
            except TypeError:
                resultado = resolver_func(personagem["id"], escolha, dados_mg.get("correta", dados_mg.get("cenario_correto", 0)))

            if resultado.get("preso"):
                await interaction.response.edit_message(
                    content=f"{mensagem_foi_preso()}\n\n🔒 **{resultado['mensagem']}**",
                    view=None,
                    embed=None,
                )
                return

            if resultado["sucesso"]:
                r = resultado["recompensa"]
                texto = mensagem_sucesso_trabalho(r.get("subiu_nivel", False), r.get("nivel", 1)) + f"\n\n💰 +${r['ganho']} | ⭐ +{r['xp']} XP"
                await interaction.response.edit_message(
                    content=texto,
                    view=None,
                    embed=None,
                )
            else:
                r = resultado.get("recompensa")
                texto = mensagem_falhou_minigame() + f"\n\n{resultado['mensagem']}"
                if r:
                    texto += f"\n\n💰 +${r['ganho']} | ⭐ +{r['xp']} XP (reduzido)"
                await interaction.response.edit_message(
                    content=texto,
                    view=None,
                    embed=None,
                )

        view = MinigameView(dados["opcoes"], callback_resposta)
        await ctx.reply(embed=embed, view=view)

    @commands.command(name="trabalharrapido", aliases=["wr"])
    async def trabalharrapido_cmd(self, ctx: commands.Context):
        """Trabalho rápido sem minigame (recompensa menor)."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if personagem is None:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return

        if personagem.get("preso"):
            await ctx.reply(embed=embed_erro("Você está preso!"))
            return

        profissao = personagem.get("profissao")
        if not profissao:
            await ctx.reply(embed=embed_erro("Sem profissão", "Use `?escolherprofissao` primeiro."))
            return

        # ✅ CORREÇÃO: Verifica cooldown (metade do normal)
        salario_info = bal.obter_salario(profissao)
        cooldown_minutos = salario_info.get("cooldown_min", 15) // 2
        ultimo_trabalho = personagem.get("ultimo_trabalho", 0)
        tempo_passado = time.time() - ultimo_trabalho
        tempo_cooldown = cooldown_minutos * 60
        
        if tempo_passado < tempo_cooldown:
            tempo_restante = int((tempo_cooldown - tempo_passado) / 60)
            await ctx.reply(embed=embed_aviso(
                "Calma aí!",
                f"Espera mais **{tempo_restante} minutos** antes de trabalhar de novo."
            ))
            return

        import database as db
        import random

        salario = bal.obter_salario(profissao)
        ganho = int(random.randint(salario["min"], salario["max"]) * 0.5)
        xp = int(salario["xp"] * 0.5)
        resultado = db.registrar_trabalho_personagem(personagem["id"], ganho, xp)

        texto = f"💼 Trabalho rápido concluído!\n💰 +${ganho} | ⭐ +{xp} XP"
        if resultado["subiu_nivel"]:
            texto += f"\n🎉 **SUBIU PRO NÍVEL {resultado['nivel']}!**"

        await ctx.reply(embed=embed_sucesso("Trabalho Rápido", texto))


async def setup(bot: commands.Bot):
    await bot.add_cog(Minigames(bot))
