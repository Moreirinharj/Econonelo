import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
import database as db


def _filtro_por_estado(item, estado_atual):
    """Filtra item por estado, aceitando UF ou nome completo."""
    cidade = item.get("cidade", "")
    mapeamento = {
        "SP": ["São Paulo"],
        "RJ": ["Rio de Janeiro"],
        "MG": ["Minas Gerais", "Belo Horizonte"],
        "PR": ["Paraná", "Curitiba"],
        "RS": ["Rio Grande do Sul", "Porto Alegre"],
        "BA": ["Bahia", "Salvador"],
    }
    cidades_validas = mapeamento.get(estado_atual, [estado_atual])
    return any(c in cidade for c in cidades_validas)


class Empresas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="empresas")
    async def empresas_cmd(self, ctx: commands.Context):
        """Lista empresas disponíveis no seu estado."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        estado_atual = personagem.get("estado_atual") or personagem.get("estado")
        empresas = db.listar_empresas()
        empresas = [e for e in empresas if _filtro_por_estado(e, estado_atual)]
        
        if not empresas:
            await ctx.reply(embed=embed_aviso("Sem empresas", "Não há empresas no seu estado atual."), ephemeral=True)
            return
        
        embed = embed_padrao("🏢 Empresas Disponíveis", cor=COR_PADRAO)
        embed.description = f"📍 Empresas no seu estado ({estado_atual}):\n\n"
        
        for i, empresa in enumerate(empresas[:10], 1):
            embed.description += f"**{i}. {empresa['nome']}** (ID: {empresa['id']})\n"
            embed.description += f"   Tipo: {empresa['tipo']} | Cidade: {empresa['cidade']}\n\n"
        
        embed.set_footer(text="Use ?loja <id> para ver os produtos.")
        
        # Adicionar imagem da primeira empresa se existir
        if empresas and empresas[0].get("imagem_url"):
            embed.set_image(url=empresas[0]["imagem_url"])
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="loja")
    async def loja_cmd(self, ctx: commands.Context, empresa_id: str):
        """Mostra produtos de uma empresa."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        empresa = db.obter_empresa(empresa_id)
        if not empresa:
            empresas_disp = db.listar_empresas()
            ids_disponiveis = ", ".join([f"`{e['id']}`" for e in empresas_disp[:10]])
            await ctx.reply(embed=embed_erro(
                "Empresa não encontrada", 
                f"Essa empresa não existe.\n\n💡 IDs disponíveis: {ids_disponiveis}"
            ), ephemeral=True)
            return
        
        produtos = db.listar_produtos(empresa_id)
        
        embed = embed_padrao(f"🏪 {empresa['nome']}", cor=COR_PADRAO)
        embed.description = f"**Tipo:** {empresa['tipo']}\n**Cidade:** {empresa['cidade']}\n\n"
        
        if produtos:
            embed.description += "**Produtos disponíveis:**\n\n"
            for i, produto in enumerate(produtos[:10], 1):
                embed.description += f"**{i}. {produto['nome']}**\n"
                embed.description += f"   Preço: ${produto['preco']} | Estoque: {produto['estoque']}\n\n"
        else:
            embed.description += "❌ Nenhum produto disponível no momento."
        
        embed.set_footer(text="Use ?comprar <id> <produto> <qtd> para comprar.")
        
        # Adicionar imagem da empresa se existir
        if empresa.get("imagem_url"):
            embed.set_image(url=empresa["imagem_url"])
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="comprar")
    async def comprar_cmd(self, ctx: commands.Context, empresa_id: str, produto_nome: str, quantidade: int = 1):
        """Compra produtos de uma empresa."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        empresa = db.obter_empresa(empresa_id)
        if not empresa:
            await ctx.reply(embed=embed_erro("Empresa não encontrada", "Essa empresa não existe."), ephemeral=True)
            return
        
        produtos = db.listar_produtos(empresa_id)
        produto = None
        for p in produtos:
            if p['nome'].lower() == produto_nome.lower():
                produto = p
                break
        
        if not produto:
            await ctx.reply(embed=embed_erro("Produto não encontrado", f"Essa empresa não vende '{produto_nome}'."), ephemeral=True)
            return
        
        if produto['estoque'] < quantidade:
            await ctx.reply(embed=embed_erro("Estoque insuficiente", f"Só tem {produto['estoque']} unidades disponíveis."), ephemeral=True)
            return
        
        custo_total = produto['preco'] * quantidade
        
        if personagem['saldo'] < custo_total:
            await ctx.reply(embed=embed_erro("Saldo insuficiente", f"Você precisa de ${custo_total} mas só tem ${personagem['saldo']}."), ephemeral=True)
            return
        
        # Processar compra
        db.atualizar_saldo_personagem(personagem['id'], -custo_total)
        db.adicionar_item(personagem['id'], produto['nome'], "consumivel", quantidade, peso=0.5)
        db.comprar_produto(empresa_id, produto['id'], quantidade)
        
        await ctx.reply(embed=embed_sucesso(
            "✅ Compra realizada!",
            f"Você comprou **{quantidade}x {produto['nome']}** por **${custo_total}**.\n\n"
            f"💰 Saldo atual: ${personagem['saldo'] - custo_total}\n"
            f"📦 Item adicionado ao inventário."
        ), ephemeral=True)

    @commands.command(name="vagas")
    async def vagas_cmd(self, ctx: commands.Context):
        """Lista vagas de emprego disponíveis."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        vagas = db.listar_vagas()
        
        if not vagas:
            await ctx.reply(embed=embed_aviso("Sem vagas", "Não há vagas disponíveis no momento."), ephemeral=True)
            return
        
        embed = embed_padrao("💼 Vagas de Emprego", cor=COR_PADRAO)
        embed.description = "**Vagas disponíveis:**\n\n"
        
        for i, vaga in enumerate(vagas[:10], 1):
            embed.description += f"**{i}. {vaga['profissao']}** (ID: {vaga['id']})\n"
            embed.description += f"   Empresa: {vaga.get('empresa_nome', 'N/A')} | Salário: ${vaga['salario']}\n\n"
        
        embed.set_footer(text="Use ?candidatar <id> para se candidatar.")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="candidatar")
    async def candidatar_cmd(self, ctx: commands.Context, vaga_id: int):
        """Candidata-se a uma vaga de emprego."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        vaga = db.obter_vaga(vaga_id)
        if not vaga:
            await ctx.reply(embed=embed_erro("Vaga não encontrada", "Essa vaga não existe."), ephemeral=True)
            return
        
        # Verificar requisitos (exemplo: escolaridade)
        if vaga.get('nivel') == 'superior' and personagem.get('escolaridade') != 'superior':
            await ctx.reply(embed=embed_erro("Requisito não atendido", "Essa vaga exige ensino superior completo."), ephemeral=True)
            return
        
        # Contratar
        db.contratar_personagem(personagem['id'], vaga_id)
        
        await ctx.reply(embed=embed_sucesso(
            "✅ Contratado!",
            f"Você foi contratado como **{vaga['profissao']}**!\n\n"
            f"💰 Salário: ${vaga['salario']}\n"
            f"🏢 Empresa: {vaga.get('empresa_nome', 'N/A')}\n\n"
            f"Use ?trabalhar para começar a trabalhar."
        ), ephemeral=True)

    @commands.command(name="statusempresa")
    async def statusempresa_cmd(self, ctx: commands.Context, empresa_id: str):
        """Mostra status detalhado de uma empresa."""
        empresa = db.obter_empresa(empresa_id)
        if not empresa:
            await ctx.reply(embed=embed_erro("Empresa não encontrada", "Essa empresa não existe."), ephemeral=True)
            return
        
        embed = embed_padrao(f"🏢 {empresa['nome']}", cor=COR_PADRAO)
        embed.description = f"**Tipo:** {empresa['tipo']}\n**Cidade:** {empresa['cidade']}\n"
        embed.description += f"**Saldo:** ${empresa.get('saldo', 0)}\n"
        embed.description += f"**Funcionários:** {empresa.get('funcionarios', 0)}\n\n"
        
        produtos = db.listar_produtos(empresa_id)
        if produtos:
            embed.description += f"**Produtos:** {len(produtos)} disponíveis\n"
        
        # Adicionar imagem se existir
        if empresa.get("imagem_url"):
            embed.set_image(url=empresa["imagem_url"])
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="rankingempresas")
    async def rankingempresas_cmd(self, ctx: commands.Context):
        """Mostra ranking das empresas mais ricas."""
        empresas = db.listar_empresas()
        
        # Ordenar por saldo
        empresas_ordenadas = sorted(empresas, key=lambda x: x.get('saldo', 0), reverse=True)
        
        embed = embed_padrao("🏆 Ranking de Empresas", cor=COR_PADRAO)
        embed.description = "**Top 10 empresas mais ricas:**\n\n"
        
        for i, empresa in enumerate(empresas_ordenadas[:10], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            embed.description += f"{emoji} **{empresa['nome']}**\n"
            embed.description += f"   Saldo: ${empresa.get('saldo', 0):,}\n\n"
        
        await ctx.reply(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Empresas(bot))
