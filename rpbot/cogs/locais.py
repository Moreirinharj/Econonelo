import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_INFO
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info
from services.local_service import TIPOS_LOCAIS, popular_mundo, locais_por_tipo
from services.viagem_service import ESTADOS_DISPONIVEIS
import database as db


class Locais(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="locais")
    async def locais_cmd(self, ctx: commands.Context, cidade: str = None, tipo: str = None):
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply("👻 Você não tem personagem, mano! Usa `?jogar` pra criar.", ephemeral=True)
            return
        estado_atual = personagem.get("estado_atual") or personagem.get("estado")
        nome_estado = ESTADOS_DISPONIVEIS.get(estado_atual, {}).get("nome", estado_atual)
        # Se não especificou cidade, usa o estado atual
        if not cidade:
            cidade = nome_estado
        """Lista locais do mundo."""
        if tipo and tipo not in TIPOS_LOCAIS:
            tipos_list = ", ".join(TIPOS_LOCAIS.keys())
            await ctx.reply(embed=embed_erro("Tipo inválido", f"Tipos disponíveis: {tipos_list}", ephemeral=True))
            return
        
        locais = db.listar_locais(cidade=cidade, tipo=tipo)
        
        if not locais:
            await ctx.reply(embed=embed_info("🗺️ Sem locais", "Nenhum local encontrado. Use `?popularmundo` (admin, ephemeral=True)."))
            return
        
        titulo = f"🗺️ Locais{' em ' + cidade if cidade else ''}"
        if tipo:
            titulo += f" ({TIPOS_LOCAIS[tipo]['nome']})"
        
        embed = embed_padrao(titulo, cor=COR_PADRAO)
        
        # Agrupa por cidade
        por_cidade = {}
        for local in locais:
            c = local["cidade"]
            if c not in por_cidade:
                por_cidade[c] = []
            por_cidade[c].append(local)
        
        for cidade_nome, lista in por_cidade.items():
            linhas = []
            for local in lista[:15]:
                emoji = TIPOS_LOCAIS.get(local["tipo"], {}).get("emoji", "📍")
                status = "🟢" if db.local_aberto_agora(local) else "🔴"
                linhas.append(f"{status} {emoji} **{local['nome']}** — {local['bairro']} ({local['horario_abertura']}-{local['horario_fechamento']})")
            
            valor = "\n".join(linhas)
            if len(lista) > 15:
                valor += f"\n*...e mais {len(lista) - 15} locais (use ?locais {cidade_nome} pra ver todos)*"
            
            embed.add_field(name=f"📍 {cidade_nome}", value=valor, inline=False)
        
        embed.set_footer(text=f"Total: {len(locais)} locais | 🟢 aberto agora | 🔴 fechado")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="local")
    async def local_cmd(self, ctx: commands.Context, local_id: int):
        """Mostra detalhes de um local."""
        local = db.obter_local(local_id)
        if not local:
            await ctx.reply(embed=embed_erro("Local não encontrado", ephemeral=True))
            return
        
        emoji = TIPOS_LOCAIS.get(local["tipo"], {}).get("emoji", "📍")
        nome_tipo = TIPOS_LOCAIS.get(local["tipo"], {}).get("nome", local["tipo"])
        aberto = db.local_aberto_agora(local)
        status = "🟢 Aberto agora" if aberto else "🔴 Fechado agora"
        
        embed = embed_info(
            f"{emoji} {local['nome']}",
            f"**Tipo:** {nome_tipo}\n"
            f"**Cidade:** {local['cidade']}\n"
            f"**Bairro:** {local['bairro']}\n"
            f"**Horário:** {local['horario_abertura']} - {local['horario_fechamento']}\n"
            f"**Status:** {status}"
        )
        
        if local["descricao"]:
            embed.add_field(name="📝 Sobre", value=local["descricao"], inline=False)
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="cidades")
    async def cidades_cmd(self, ctx: commands.Context):
        """Lista cidades com locais."""
        todos = db.listar_locais()
        cidades = {}
        for local in todos:
            c = local["cidade"]
            if c not in cidades:
                cidades[c] = 0
            cidades[c] += 1
        
        if not cidades:
            await ctx.reply(embed=embed_info("🗺️ Sem cidades", "Nenhuma cidade cadastrada ainda.", ephemeral=True))
            return
        
        embed = embed_padrao("🌎 Cidades do Mundo", cor=COR_PADRAO)
        linhas = []
        for cidade, qtd in sorted(cidades.items(), key=lambda x: -x[1]):
            linhas.append(f"📍 **{cidade}** — {qtd} local(is)")
        
        embed.description = "\n".join(linhas)
        embed.set_footer(text=f"Total: {len(cidades)} cidades, {len(todos)} locais")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="popularmundo")
    @commands.has_permissions(administrator=True)
    async def popularmundo_cmd(self, ctx: commands.Context):
        """Popula o mundo com locais reais (só admin)."""
        count = popular_mundo()
        if count == 0:
            await ctx.reply(embed=embed_info("Mundo já populado", f"Já existem {db.contar_locais()} locais cadastrados."), ephemeral=True)
            return
        
        await ctx.reply(embed=embed_sucesso("Mundo populado!", f"{count} locais reais foram adicionados ao mundo.", ephemeral=True))

    @commands.command(name="criarlocal")
    @commands.has_permissions(administrator=True)
    async def criarlocal_cmd(self, ctx: commands.Context, tipo: str, cidade: str, bairro: str, *, nome: str):
        """Cria um local manualmente (só admin)."""
        if tipo not in TIPOS_LOCAIS:
            tipos_list = ", ".join(TIPOS_LOCAIS.keys())
            await ctx.reply(embed=embed_erro("Tipo inválido", f"Opções: {tipos_list}", ephemeral=True))
            return
        
        local_id = db.criar_local(nome, tipo, cidade, bairro)
        emoji = TIPOS_LOCAIS[tipo]["emoji"]
        await ctx.reply(embed=embed_sucesso(
            "Local criado",
            f"{emoji} **{nome}** (ID: {local_id}, ephemeral=True)\n"
            f"Tipo: {tipo}\n"
            f"Cidade: {cidade} / {bairro}"
        ))


async def setup(bot: commands.Bot):
    await bot.add_cog(Locais(bot))
