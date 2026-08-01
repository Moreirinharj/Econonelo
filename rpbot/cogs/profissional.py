import discord
from discord.ext import commands

import database as db
from data.constantes import MSG_SEM_PERSONAGEM, COR_SUCESSO, COR_ERRO
from utils.embeds import embed_sucesso, embed_erro, embed_info
from utils.profissao_check import (
    obter_comandos_profissao, criar_embed_comandos_profissao, COMANDOS_POR_PROFISSAO
)


class Profissional(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="comandos", aliases=["cmds", "prof"])
    async def comandos_cmd(self, ctx: commands.Context):
        """Mostra os comandos exclusivos da sua profissão."""
        personagem = db.obter_personagem_ativo(str(ctx.author.id))
        if not personagem:
            await ctx.reply("👻 Você não tem personagem, mano! Usa `?jogar` pra criar.")
            return
        
        profissao = personagem.get("profissao")
        if not profissao:
            await ctx.reply("💼 Você não tem profissão, mano! Usa `?profissoes` pra ver as vagas.")
            return
        
        embed = criar_embed_comandos_profissao(profissao)
        if not embed:
            await ctx.reply(embed=embed_erro("Sem comandos", f"A profissão {profissao} não tem comandos exclusivos ainda."))
            return
        
        embed.set_author(name=f"{personagem['nome']} — {COMANDOS_POR_PROFISSAO[profissao]['nome']}")
        await ctx.reply(embed=embed)

    @commands.command(name="pedirdemissao", aliases=["demissao", "sair"])
    async def pedirdemissao_cmd(self, ctx: commands.Context):
        """Pede demissão da profissão atual."""
        personagem = db.obter_personagem_ativo(str(ctx.author.id))
        if not personagem:
            await ctx.reply("👻 Você não tem personagem, mano! Usa `?jogar` pra criar.")
            return
        
        profissao = personagem.get("profissao")
        if not profissao:
            await ctx.reply("💼 Você não tem profissão, mano! Não tem como pedir demissão do nada. 😂")
            return
        
        nome_profissao = COMANDOS_POR_PROFISSAO.get(profissao, {}).get("nome", profissao.replace("_", " ").title())
        
        view = ConfirmarDemissaoView(ctx.author.id, profissao, nome_profissao)
        await ctx.reply(
            f"🤔 Você tem certeza que quer pedir demissão de **{nome_profissao}**?\n"
            f"💡 Você vai perder o acesso aos comandos exclusivos dessa profissão.",
            view=view
        )


class ConfirmarDemissaoView(discord.ui.View):
    def __init__(self, user_id: int, profissao: str, nome_profissao: str):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.profissao = profissao
        self.nome_profissao = nome_profissao

    @discord.ui.button(label="✅ Sim, quero pedir demissão", style=discord.ButtonStyle.danger)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("🚫 Esse botão não é seu, mano!", ephemeral=True)
            return
        
        personagem = db.obter_personagem_ativo(str(interaction.user.id))
        if not personagem:
            await interaction.response.send_message("👻 Você não tem personagem!", ephemeral=True)
            return
        
        # Verifica se ainda tem a mesma profissão (evita race condition)
        if personagem.get("profissao") != self.profissao:
            await interaction.response.send_message(
                f"🤔 Você já não é mais {self.nome_profissao}. Verifica aí!", ephemeral=True
            )
            return
        
        # Define profissão como string vazia (não None)
        db.definir_profissao_personagem(personagem["id"], "")
        
        for child in self.children:
            child.disabled = True
        
        await interaction.response.edit_message(
            content=f"📤 **Demissão aceita!**\n\n"
                    f"Você pediu demissão de **{self.nome_profissao}**.\n"
                    f"Agora você tá desempregado, mano. 💼\n\n"
                    f"💡 Usa `?profissoes` pra ver as vagas disponíveis e escolher uma nova!",
            view=self
        )

    @discord.ui.button(label="❌ Não, mudei de ideia", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("🚫 Esse botão não é seu, mano!", ephemeral=True)
            return
        
        for child in self.children:
            child.disabled = True
        
        await interaction.response.edit_message(
            content="✅ Boa decisão, mano! Continua na tua profissão. 💪",
            view=self
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Profissional(bot))
