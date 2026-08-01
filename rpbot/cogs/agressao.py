import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO, MSG_SEM_PERSONAGEM
from utils.comando_ajuda import mostrar_ajuda_cpf, mostrar_ajuda_pedido, validar_cpf
from utils.verificar_personagem import verificar_personagem
from utils.comando_ajuda import mostrar_ajuda_cpf, validar_cpf
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso
from services.personagem_service import obter_dados_personagem
from services.agressao_service import (
    aplicar_agressao, defender_de_agressao, curar_ferimento,
    ver_ferimento, verificar_cooldown, verificar_arma
)
from services.acao_privada import registrar_acao_privada, gerar_mensagem_publica_neutra
from data.agressao_data import TIPOS_AGRESSAO, ARMAS_DISPONIVEIS
import database as db


class Agressao(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="agredir", aliases=["atacar", "bater"])
    async def agredir_cmd(self, ctx: commands.Context, membro: discord.Member, tipo: str = "soco"):
        """Agridi alguém (ação privada — só envolvidos veem detalhes)."""
        atacante = obter_dados_personagem(str(ctx.author.id))
        if not atacante:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        alvo = db.obter_personagem_ativo(str(membro.id))
        if not alvo:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo.", ephemeral=True))
            return
        
        tipo = tipo.lower()
        if tipo not in TIPOS_AGRESSAO:
            tipos_lista = ", ".join(f"`{t}`" for t in TIPOS_AGRESSAO.keys())
            await ctx.reply(embed=embed_erro(
                "Tipo inválido",
                f"Tipos disponíveis: {tipos_lista}\n\n💡 Usa `?agredir @user soco`"
            , ephemeral=True), ephemeral=True)
            return
        
        resultado = aplicar_agressao(atacante["id"], alvo["id"], tipo)
        
        if not resultado["sucesso"]:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True), ephemeral=True)
            return
        
        tipo_info = resultado.get("tipo", {})
        emoji = tipo_info.get("emoji", "💥")
        
        # Monta mensagens privadas
        if resultado.get("matou"):
            titulo = "💀 HOMICÍDIO"
            desc_executor = f"Você matou **{alvo['nome']}** com {tipo_info['nome']}!\n\n{resultado['msg']}"
            desc_vitima = f"Você foi morto(a) por **{atacante['nome']}** com {tipo_info['nome']}.\n\nSeus bens serão distribuídos conforme teu testamento ou herança legal."
        elif resultado.get("preso"):
            titulo = "🚔 PRESO EM FLAGRANTE"
            desc_executor = f"Você agrediu **{alvo['nome']}** e foi preso!\n\n{resultado['msg']}"
            desc_vitima = f"**{atacante['nome']}** te agrediu com {tipo_info['nome']} e foi preso em flagrante!\n\n{resultado['msg']}"
        elif resultado.get("acertou"):
            titulo = f"{emoji} Agressão"
            desc_executor = f"Você agrediu **{alvo['nome']}** com {tipo_info['nome']}!\n\n{resultado['msg']}"
            desc_vitima = f"**{atacante['nome']}** te agrediu com {tipo_info['nome']}!\n\n{resultado['msg']}"
        else:
            titulo = f"{emoji} Agressão Falhou"
            desc_executor = f"Você tentou agredir **{alvo['nome']}** mas errou!\n\n{resultado['msg']}"
            desc_vitima = f"**{atacante['nome']}** tentou te agredir mas você desviou!\n\n{resultado['msg']}"
        
        # Registra ação privada
        acao_id = registrar_acao_privada(
            executor_id=ctx.author.id,
            vitima_id=membro.id,
            titulo=titulo,
            descricao_executor=desc_executor,
            descricao_vitima=desc_vitima
        )
        
        # Mensagem pública neutra (só menciona a vítima)
        msg_publica = gerar_mensagem_publica_neutra(membro.mention, acao_id)
        
        # Envia mensagem efêmera pro executor (só ele vê)
        embed_executor = discord.Embed(
            title=f"🔒 {titulo} (Privado)",
            description=desc_executor,
            color=discord.Color.orange()
        )
        embed_executor.set_footer(text=f"ID da ação: {acao_id} • A vítima foi notificada")
        
        await ctx.reply(embed=embed_executor, ephemeral=True)
        
        # Envia mensagem pública mencionando a vítima
        await ctx.send(msg_publica)

    @commands.command(name="defender", aliases=["defesa"])
    async def defender_cmd(self, ctx: commands.Context, agressor: discord.Member):
        """Tenta se defender de quem te agrediu (ação privada)."""
        defensor = obter_dados_personagem(str(ctx.author.id))
        if not defensor:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        alvo_agressor = db.obter_personagem_ativo(str(agressor.id))
        if not alvo_agressor:
            await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo.", ephemeral=True))
            return
        
        resultado = defender_de_agressao(defensor["id"], alvo_agressor["id"])
        
        if resultado["sucesso"]:
            if resultado.get("defendeu"):
                acao_id = registrar_acao_privada(
                    executor_id=ctx.author.id,
                    vitima_id=agressor.id,
                    titulo="🛡️ Defesa Bem-Sucedida",
                    descricao_executor=f"Você se defendeu de **{agressor.display_name}**!\n\n{resultado['msg']}",
                    descricao_vitima=f"**{ctx.author.display_name}** se defendeu do teu ataque!\n\n{resultado['msg']}"
                )
                
                embed_executor = discord.Embed(
                    title="🛡️ Defesa (Privado)",
                    description=f"Você se defendeu de **{agressor.display_name}**!\n\n{resultado['msg']}",
                    color=discord.Color.green()
                )
                embed_executor.set_footer(text=f"ID: {acao_id}")
                
                await ctx.reply(embed=embed_executor, ephemeral=True)
                await ctx.send(gerar_mensagem_publica_neutra(agressor.mention, acao_id))
            else:
                await ctx.reply(embed=embed_aviso("❌ Falhou!", resultado["msg"], ephemeral=True), ephemeral=True)
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True), ephemeral=True)

    @commands.command(name="curar", aliases=["tratar"])
    @commands.command(name="curar", aliases=["tratar"])
    async def curar_cmd(self, ctx: commands.Context, cpf_id: str = None):
        """Médico/SAMU cura ferimentos de alguém."""
        # 1. Mostrar ajuda se não passar o CPF
        if cpf_id is None:
            await ctx.reply(embed=mostrar_ajuda_cpf(ctx, "?curar", "Cura ferimentos de outro personagem."), ephemeral=True)
            return
        
        # 2. Validar CPF
        if not validar_cpf(cpf_id):
            await ctx.reply(embed=embed_erro("CPF inválido", "O CPF deve ter 3 dígitos (000 a 999)."), ephemeral=True)
            return
        
        # 3. Verificar personagem do autor
        personagem = await verificar_personagem(ctx)
        if not personagem:
            return
        
        # 4. Verificar profissão (apenas médico e SAMU)
        profissao = personagem.get('profissao', '').lower()
        if profissao not in ['medico', 'samu']:
            await ctx.reply(embed=embed_erro(
                "Profissão não autorizada",
                f"Apenas **Médico** ou **SAMU** podem curar.\nSua profissão: `{profissao or 'nenhuma'}`"
            ), ephemeral=True)
            return
        
        # 5. Buscar paciente pelo CPF
        paciente = db.obter_personagem_por_cpf(cpf_id)
        if not paciente:
            await ctx.reply(embed=embed_erro("Paciente não encontrado", f"Nenhum personagem com CPF {cpf_id}."), ephemeral=True)
            return
        
        # 6. Curar (restaurar vida para 100)
        db.atualizar_vida_personagem(paciente['id'], 100)
        
        await ctx.reply(embed=embed_sucesso(
            "Cura realizada!",
            f"Você curou **{paciente['nome']}** (CPF: {cpf_id}).\nVida restaurada para 100."
        ), ephemeral=True)

    @commands.command(name="ferimento", aliases=["ferido", "machucado"])
    async def ferimento_cmd(self, ctx: commands.Context, membro: discord.Member = None):
        """Mostra nível de ferimento (teu ou de alguém)."""
        if membro:
            personagem = db.obter_personagem_ativo(str(membro.id))
            if not personagem:
                await ctx.reply(embed=embed_erro("Erro", "Esse usuário não tem personagem ativo.", ephemeral=True))
                return
        else:
            personagem = obter_dados_personagem(str(ctx.author.id))
            if not personagem:
                await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
                return
        
        resultado = ver_ferimento(personagem["id"])
        
        if resultado["sucesso"]:
            await ctx.reply(
                embed=embed_info(f"🩹 Ferimento de {personagem['nome']}", resultado["msg"], ephemeral=True),
                ephemeral=True
            )
        else:
            await ctx.reply(embed=embed_erro("Erro", resultado["msg"], ephemeral=True), ephemeral=True)

    @commands.command(name="tiposagressao", aliases=["armas", "combate"])
    async def tiposagressao_cmd(self, ctx: commands.Context):
        """Mostra tipos de agressão e armas disponíveis."""
        embed = embed_padrao("⚔️ Tipos de Agressão", cor=COR_PADRAO)
        
        for tipo, dados in TIPOS_AGRESSAO.items():
            requer = f"\n🔹 Requer: `{dados['requer_item']}`" if "requer_item" in dados else ""
            embed.add_field(
                name=f"{dados['emoji']} {dados['nome']} (`{tipo}`)",
                value=f"**Dano:** {dados['dano_min']}-{dados['dano_max']}\n"
                      f"**Acerto:** {int(dados['chance_acerto']*100)}%\n"
                      f"**Morte:** {int(dados['chance_morte']*100)}%\n"
                      f"**Flagrante:** {int(dados['chance_flagrante']*100)}%\n"
                      f"**Crime:** {dados['crime']}{requer}",
                inline=True
            )
        
        embed.set_footer(text="Use ?agredir @user <tipo> pra atacar")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="comprararma")
    async def comprararma_cmd(self, ctx: commands.Context, arma_nome: str):
        """Compra uma arma (mercado negro)."""
        personagem = obter_dados_personagem(str(ctx.author.id))
        if not personagem:
            await ctx.reply(MSG_SEM_PERSONAGEM, ephemeral=True)
            return
        
        arma_encontrada = None
        for nome, dados in ARMAS_DISPONIVEIS.items():
            if nome.lower() == arma_nome.lower():
                arma_encontrada = (nome, dados)
                break
        
        if not arma_encontrada:
            armas_lista = ", ".join(f"`{n}`" for n in ARMAS_DISPONIVEIS.keys())
            await ctx.reply(embed=embed_erro(
                "Arma não encontrada",
                f"Armas disponíveis: {armas_lista}"
            , ephemeral=True), ephemeral=True)
            return
        
        nome, dados = arma_encontrada
        
        if personagem["saldo"] < dados["preco"]:
            await ctx.reply(embed=embed_erro(
                "💸 Saldo insuficiente",
                f"Essa arma custa ${dados['preco']}. Você tem ${personagem['saldo']}."
            , ephemeral=True), ephemeral=True)
            return
        
        db.atualizar_saldo_personagem(personagem["id"], -dados["preco"])
        db.adicionar_item(personagem["id"], nome, "arma", 1, peso=1.0)
        
        if dados.get("ilegal"):
            db.adicionar_registro_criminal(personagem["id"], f"Porte ilegal de {nome}")
        
        await ctx.reply(embed=embed_sucesso(
            f"🔫 {nome} Comprada!",
            f"**Preço:** ${dados['preco']}\n**Descrição:** {dados['descricao']}\n\n"
            f"⚠️ Item adicionado ao teu inventário. Usa `?inventario` pra ver."
            + ("\n\n🚨 **ARMA ILEGAL!** Se for pego, pode ser preso." if dados.get("ilegal", ephemeral=True) else "")
        ), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Agressao(bot))
