import discord
from discord.ext import commands
import json

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
from services.delivery_service import (
    listar_empresas_delivery, criar_pedido, listar_pedidos_pendentes,
    aceitar_pedido, completar_pedido
)
import database as db


class Delivery(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ifood", aliases=["delivery", "pedirdelivery"])
    async def ifood_cmd(self, ctx: commands.Context):
        """Mostra empresas disponíveis pra pedir delivery."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        estado_atual = personagem.get("estado_atual") or personagem.get("estado")
        empresas = listar_empresas_delivery(estado_atual)
        
        if not empresas:
            await ctx.reply(embed=embed_info(
                "🛵 Sem delivery",
                f"Nenhuma empresa com delivery disponível em seu estado ({estado_atual}).\n\n💡 Tenta viajar pra outro estado com `?viajar <UF>`."
            ))
            return
        
        embed = embed_padrao("🛵 Delivery Disponível", cor=COR_PADRAO)
        embed.description = f"📍 Empresas no seu estado ({estado_atual}):\n\nUse `?cardapio <id_empresa>` pra ver os itens."
        
        for e in empresas[:10]:
            tipo_emoji = "🍽️" if e["tipo"] == "restaurante" else "🛒"
            embed.add_field(
                name=f"{tipo_emoji} {e['nome']}",
                value=f"**Tipo:** {e['tipo'].title()}\n**Cidade:** {e['cidade']}\n**ID:** `{e['id']}`\n\n💡 `?cardapio {e['id']}`",
                inline=True
            )
        
        await ctx.reply(embed=embed)

    @commands.command(name="cardapio", )
    async def cardapio_cmd(self, ctx: commands.Context, empresa_id: str):
        """Mostra cardápio de uma empresa."""
        empresa = db.obter_empresa(empresa_id)
        if not empresa:
            await ctx.reply(embed=embed_erro("Empresa não encontrada", "Use `?ifood` pra ver as disponíveis."))
            return
        
        produtos = db.listar_produtos(empresa_id)
        
        embed = embed_padrao(f"📋 Cardápio — {empresa['nome']}", cor=COR_PADRAO)
        
        if not produtos:
            embed.description = "Sem produtos disponíveis no momento."
        else:
            por_cat = {}
            for p in produtos:
                por_cat.setdefault(p["categoria"], []).append(p)
            
            for cat, lista in por_cat.items():
                linhas = [f"• **ID {p['id']}** — {p['nome']} — ${p['preco']}" for p in lista[:10]]
                embed.add_field(name=f"📦 {cat.title()}", value="\n".join(linhas), inline=False)
        
        embed.set_footer(text="Use ?pedir <id_empresa> <id_produto> [quantidade] pra pedir")
        await ctx.reply(embed=embed)

    @commands.command(name="pedir")
    async def pedir_cmd(self, ctx: commands.Context, empresa_id: str, produto_id: int, quantidade: int = 1):
        """Faz um pedido de delivery."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        if quantidade < 1 or quantidade > 20:
            await ctx.reply(embed=embed_erro("Quantidade inválida", "Escolhe entre 1 e 20."))
            return
        
        itens = [{"produto_id": produto_id, "quantidade": quantidade}]
        resultado = criar_pedido(personagem["id"], empresa_id, itens)
        
        if resultado["sucesso"]:
            msg = resultado["msg"]
            if resultado.get("motoboy_id"):
                motoboy = db.obter_personagem_por_id(resultado["motoboy_id"])
                msg += f"\n\n🛵 **Motoboy acionado:** {motoboy['nome'] if motoboy else 'Alguém'} está a caminho!"
            else:
                msg += "\n\n⏳ Nenhum motoboy disponível no momento. Seu pedido ficará pendente."
            
            await ctx.reply(embed=embed_sucesso("🛵 Pedido Realizado", msg))
        else:
            msg = resultado["msg"]
            if "helper" in resultado:
                msg += f"\n\n{resultado['helper']}"
            await ctx.reply(embed=embed_erro("Erro no pedido", msg))

    @commands.command(name="pedidospendentes")
    async def pedidospendentes_cmd(self, ctx: commands.Context):
        """Mostra pedidos pendentes pra motoboys."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        if personagem.get("profissao") != "motoboy":
            await ctx.reply(embed=embed_erro("Não é motoboy", "Apenas motoboys podem ver pedidos pendentes.\n\n💡 Usa `?escolherprofissao motoboy` pra virar motoboy."))
            return
        
        pedidos = listar_pedidos_pendentes(personagem["id"])
        
        if not pedidos:
            await ctx.reply(embed=embed_info("🛵 Sem pedidos", "Nenhum pedido pendente no momento. Tenta de novo mais tarde!"))
            return
        
        embed = embed_padrao("🛵 Pedidos Pendentes", cor=COR_PADRAO)
        embed.description = "Use `?aceitarentrega <id>` pra aceitar um pedido."
        
        for p in pedidos:
            itens = json.loads(p["itens"])
            itens_texto = ", ".join([f"{i['nome']} x{i['quantidade']}" for i in itens])
            embed.add_field(
                name=f"📦 Pedido #{p['id']} — {p['empresa_nome']}",
                value=f"**Itens:** {itens_texto}\n**Valor:** ${p['valor_total']}\n**Endereço:** {p['endereco_entrega']}\n\n💡 `?aceitarentrega {p['id']}`",
                inline=False
            )
        
        await ctx.reply(embed=embed)

    @commands.command(name="aceitarentrega")
    async def aceitarentrega_cmd(self, ctx: commands.Context, pedido_id: int):
        """Motoboy aceita um pedido pendente."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        if personagem.get("profissao") != "motoboy":
            await ctx.reply(embed=embed_erro("Não é motoboy", "Apenas motoboys podem aceitar entregas."))
            return
        
        resultado = aceitar_pedido(personagem["id"], pedido_id)
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("🛵 Pedido Aceito", resultado["msg"]))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"]))

    @commands.command(name="completarentrega")
    async def completarentrega_cmd(self, ctx: commands.Context, pedido_id: int):
        """Motoboy completa uma entrega."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        if personagem.get("profissao") != "motoboy":
            await ctx.reply(embed=embed_erro("Não é motoboy", "Apenas motoboys podem completar entregas."))
            return
        
        resultado = completar_pedido(pedido_id, personagem["id"])
        
        if resultado["sucesso"]:
            await ctx.reply(embed=embed_sucesso("✅ Entrega Concluída", resultado["msg"]))
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"]))

    @commands.command(name="meuspedidos")
    async def meuspedidos_cmd(self, ctx: commands.Context):
        """Mostra teus pedidos."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM)
            return
        
        conn = db.conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.*, e.nome as empresa_nome
            FROM pedidos p
            JOIN empresas e ON p.empresa_id = e.id
            WHERE p.cliente_id = ?
            ORDER BY p.criado_em DESC
            LIMIT 10
        """, (personagem["id"],))
        pedidos = [dict(r) for r in cur.fetchall()]
        conn.close()
        
        if not pedidos:
            await ctx.reply(embed=embed_info("📦 Sem pedidos", "Você não fez nenhum pedido ainda."))
            return
        
        embed = embed_padrao("📦 Meus Pedidos", cor=COR_PADRAO)
        
        for p in pedidos:
            status_emoji = {"pendente": "⏳", "em_entrega": "🛵", "entregue": "✅"}.get(p["status"], "❓")
            itens = json.loads(p["itens"])
            itens_texto = ", ".join([f"{i['nome']} x{i['quantidade']}" for i in itens])
            
            embed.add_field(
                name=f"{status_emoji} Pedido #{p['id']} — {p['empresa_nome']}",
                value=f"**Itens:** {itens_texto}\n**Total:** ${p['valor_total']}\n**Status:** {p['status'].replace('_', ' ').title()}",
                inline=False
            )
        
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Delivery(bot))
