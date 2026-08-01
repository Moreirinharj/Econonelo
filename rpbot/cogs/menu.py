import discord
from discord.ext import commands

from data.constantes import COR_PADRAO
from services.menu_service import obter_categorias, obter_categoria, formatar_categoria_embed


class MenuView(discord.ui.View):
    def __init__(self, categorias: dict, timeout=300):
        super().__init__(timeout=timeout)
        self.categorias = categorias
        
        # Cria botões pra cada categoria (máximo 25 botões por view)
        for i, (chave, dados) in enumerate(list(categorias.items())[:25]):
            emoji = chave.split(" ")[0]
            nome_curto = chave.split(" ")[1][:15]
            
            botao = discord.ui.Button(
                label=nome_curto,
                emoji=emoji,
                style=discord.ButtonStyle.secondary,
                custom_id=f"menu_{chave}",
                row=i // 5,
            )
            
            async def callback(interaction: discord.Interaction, chave_categoria=chave):
                categoria = obter_categoria(chave_categoria)
                if not categoria:
                    await interaction.response.send_message("Categoria não encontrada.", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    title=categoria["titulo"],
                    description=categoria["descricao"] + "\n\n" + formatar_categoria_embed(categoria),
                    color=COR_PADRAO,
                )
                embed.set_footer(text="Clica em outro botão pra ver outra categoria")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            botao.callback = callback
            self.add_item(botao)


class Menu(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="menu", aliases=["comandinhos", "guia"])
    async def menu_cmd(self, ctx: commands.Context):
        """Mostra um menu interativo com todos os comandos organizados por categoria."""
        categorias = obter_categorias()
        
        embed = discord.Embed(
            title="📋 Menu de Comandos",
            description=(
                "Clica num botão abaixo pra ver os comandos daquela categoria.\n\n"
                f"**Total:** {len(categorias)} categorias | "
                f"**Comandos:** {sum(len(c['comandos']) for c in categorias.values())}\n\n"
                "💡 *As respostas aparecem só pra ti (mensagem efêmera)*"
            ),
            color=COR_PADRAO,
        )
        
        # Lista as categorias no embed principal
        lista_categorias = []
        for chave, dados in categorias.items():
            emoji = chave.split(" ")[0]
            nome = chave.split(" ")[1].title()
            qtd = len(dados["comandos"])
            lista_categorias.append(f"{emoji} **{nome}** ({qtd} cmds)")
        
        embed.add_field(
            name="📂 Categorias Disponíveis",
            value="\n".join(lista_categorias),
            inline=False,
        )
        
        embed.set_footer(text="💡 Usa ?ajuda <comando> pra detalhes específicos")
        
        view = MenuView(categorias)
        await ctx.reply(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Menu(bot))
