import discord
from discord.ext import commands
import database as db
from utils.embeds import embed_sucesso, embed_erro


class Imagens(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="atualizarimagem")
    async def atualizarimagem_cmd(self, ctx: commands.Context, tipo: str, url: str):
        """
        Atualiza a imagem de uma empresa/profissão.
        
        Uso: ?atualizarimagem empresa <url>
        Uso: ?atualizarimagem profissao <url>
        """
        if tipo.lower() not in ["empresa", "profissao"]:
            await ctx.reply(embed=embed_erro("Tipo inválido", "Use `empresa` ou `profissao`"), ephemeral=True)
            return
        
        # Verificar URL
        if not url.startswith("http"):
            await ctx.reply(embed=embed_erro("URL inválida", "A URL deve começar com http:// ou https://"), ephemeral=True)
            return
        
        if tipo.lower() == "empresa":
            # Atualizar todas as empresas do usuário (se for admin, atualiza todas)
            conn = db.conectar()
            cur = conn.cursor()
            cur.execute("UPDATE empresas SET imagem_url = ?", (url,))
            atualizadas = cur.rowcount
            conn.commit()
            conn.close()
            
            await ctx.reply(embed=embed_sucesso("Imagem atualizada", f"{atualizadas} empresa(s) atualizada(s) com a nova imagem."), ephemeral=True)
        else:
            await ctx.reply(embed=embed_erro("Em desenvolvimento", "Atualização de imagens de profissão será implementada em breve."), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Imagens(bot))
