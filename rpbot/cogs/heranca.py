import discord
from discord.ext import commands
import json

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
from services.heranca_service import (
    criar_testamento, ver_testamento, cancelar_testamento,
    listar_herancas_pendentes, receber_heranca, obter_herdeiros_legais
)
import database as db


class Heranca(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="testamento")
    async def testamento_cmd(self, ctx: commands.Context, *, args: str = None):
        """Cria, vê ou cancela testamento.
        
        Uso:
        ?testamento — vê teu testamento atual
        ?testamento criar <@user1> <porcentagem1> <@user2> <porcentagem2> ...
        ?testamento cancelar
        """
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        if not args:
            # Mostra testamento atual
            resultado = ver_testamento(personagem["id"])
            if resultado["sucesso"]:
                await ctx.reply(embed=embed_info("📜 Teu Testamento", resultado["msg"], ephemeral=True))
            else:
                await ctx.reply(embed=embed_aviso(
                    "Sem testamento",
                    resultado["msg"] + "\n\n"
                    "**Como criar:**\n"
                    "`?testamento criar @user1 50 @user2 50`\n\n"
                    "**Cancelar:**\n"
                    "`?testamento cancelar`"
                , ephemeral=True))
            return
        
        partes = args.split()
        
        if partes[0].lower() == "cancelar":
            resultado = cancelar_testamento(personagem["id"])
            if resultado["sucesso"]:
                await ctx.reply(embed=embed_sucesso("Testamento Cancelado", resultado["msg"], ephemeral=True))
            else:
                await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))
            return
        
        if partes[0].lower() == "criar":
            if len(partes) < 4:
                await ctx.reply(embed=embed_erro(
                    "Formato inválido",
                    "Usa: `?testamento criar @user1 50 @user2 50`\n\n"
                    "A soma das porcentagens deve ser 100%."
                , ephemeral=True))
                return
            
            # Parse herdeiros
            herdeiros = {}
            i = 1
            while i < len(partes) - 1:
                # Pega @menção
                mencao = partes[i]
                if mencao.startswith("<@") and mencao.endswith(">"):
                    user_id = mencao[2:-1].replace("!", "")
                else:
                    await ctx.reply(embed=embed_erro("Erro", f"Menção inválida: {mencao}. Usa @user.", ephemeral=True))
                    return
                
                # Pega porcentagem
                try:
                    porcentagem = int(partes[i + 1])
                except ValueError:
                    await ctx.reply(embed=embed_erro("Erro", f"Porcentagem inválida: {partes[i + 1]}", ephemeral=True))
                    return
                
                # Busca personagem do user
                herdeiro = db.obter_personagem_ativo(user_id)
                if not herdeiro:
                    await ctx.reply(embed=embed_erro("Erro", f"Usuário {mencao} não tem personagem ativo.", ephemeral=True))
                    return
                
                herdeiros[herdeiro["id"]] = porcentagem
                i += 2
            
            resultado = criar_testamento(personagem["id"], herdeiros)
            if resultado["sucesso"]:
                await ctx.reply(embed=embed_sucesso("📜 Testamento Criado", resultado["msg"], ephemeral=True))
            else:
                await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))
            return
        
        await ctx.reply(embed=embed_erro(
            "Opção inválida",
            "Usa `?testamento`, `?testamento criar ...` ou `?testamento cancelar`."
        , ephemeral=True))

    @commands.command(name="verherdeiros")
    async def verherdeiros_cmd(self, ctx: commands.Context):
        """Mostra quem seriam teus herdeiros legais (sem testamento)."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        herdeiros = obter_herdeiros_legais(personagem["id"])
        
        if not herdeiros:
            await ctx.reply(embed=embed_aviso(
                "Sem herdeiros",
                "Você não tem familiares vivos. Se morrer, seus bens vão pro governo.\n\n"
                "💡 Usa `?adicionarfam` pra adicionar familiares ou `?testamento criar` pra deixar bens pra alguém."
            , ephemeral=True))
            return
        
        embed = embed_padrao("👥 Teus Herdeiros Legais", cor=COR_PADRAO)
        embed.description = "Se tu morreres **sem testamento**, teus bens serão distribuídos assim:"
        
        for h in herdeiros:
            embed.add_field(
                name=f"👤 {h['personagem']['nome']}",
                value=f"**Porcentagem:** {h['porcentagem']}%",
                inline=True
            )
        
        embed.set_footer(text="💡 Usa ?testamento criar pra mudar essa distribuição")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="heranca", aliases=["herancas"])
    async def heranca_cmd(self, ctx: commands.Context):
        """Mostra heranças pendentes pra você receber."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        herancas = listar_herancas_pendentes(personagem["id"])
        
        if not herancas:
            await ctx.reply(embed=embed_info(
                "📦 Sem heranças",
                "Você não tem heranças pendentes no momento."
            , ephemeral=True))
            return
        
        embed = embed_padrao("📦 Heranças Pendentes", cor=COR_PADRAO)
        embed.description = "Use `?receberheranca <id>` pra receber."
        
        for h in herancas:
            bens = json.loads(h["bens"])
            embed.add_field(
                name=f"💰 Herança #{h['id']} — de {h['falecido_nome']}",
                value=f"**Valor:** ${bens['dinheiro']}\n"
                      f"**Imposto pago:** ${bens['imposto']}\n"
                      f"**Casas:** {len(bens.get('casas', []))}\n"
                      f"**Veículos:** {len(bens.get('veiculos', []))}\n\n"
                      f"💡 `?receberheranca {h['id']}`",
                inline=False
            )
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="receberheranca")
    async def receberheranca_cmd(self, ctx: commands.Context, heranca_id: int):
        """Recebe uma herança pendente."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        resultado = receber_heranca(personagem["id"], heranca_id)
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("💰 Herança Recebida", resultado["msg"], ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True))


async def setup(bot: commands.Bot):
    await bot.add_cog(Heranca(bot))
