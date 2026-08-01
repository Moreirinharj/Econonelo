import discord
from discord.ext import commands

import database as db
from data.constantes import COR_PADRAO, COR_SUCESSO, COR_ERRO, NOMES_GENERO, NOMES_SEXUALIDADE, NOMES_PRONOMES
from utils.embeds import embed_padrao, embed_sucesso, embed_erro
from data.filtro_nomes import validar_nome, mensagem_nome_invalido


class Personagem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="jogar", aliases=["criar", "start"])
    async def jogar_cmd(self, ctx: commands.Context, *, nome: str = None):
        """Cria um novo personagem."""
        user_id = str(ctx.author.id)
        
        personagens = db.listar_personagens(user_id)
        if len(personagens) >= 3:
            if personagem.get('cpf'):
            embed.add_field(name="🆔 CPF", value=str(personagem['cpf']), inline=True)
        await ctx.reply(embed=embed_erro(
                "Limite atingido",
                "Você já tem 3 personagens, mano! Exclui um antes de criar outro.\n\n"
                "💡 Usa `?personagens` pra ver tua lista."
            , ephemeral=True))
            return
        
        if not nome:
            await ctx.reply(embed=embed_erro(
                "Cadê o nome?",
                "Usa `?jogar <nome>` pra criar teu personagem.\n\n"
                "💡 Exemplo: `?jogar João Silva`"
            , ephemeral=True))
            return
        
        validacao = validar_nome(nome)
        if not validacao["valido"]:
            await ctx.reply(embed=embed_erro("Nome inválido", f"{mensagem_nome_invalido}\n\n❌ {validacao['motivo']}"))
            return
        
        todos_personagens = db.listar_todos_personagens()
        nome_lower = nome.strip().lower()
        for p in todos_personagens:
            if p["nome"].lower() == nome_lower:
                await ctx.reply(embed=embed_erro(
                    "Nome já existe",
                    f"Já existe um personagem chamado **{nome}** no jogo, mano!\n\n"
                    f"💡 Escolhe outro nome. Tenta adicionar um sobrenome diferente."
                , ephemeral=True))
                return
        
        dados = {
            "nome": nome.strip(),
            "idade": 18,
            "cor_pele": "nao_informado",
            "tipo_cabelo": "nao_informado",
            "cor_cabelo": "nao_informado",
            "estado": "nao_informado",
            "religiao": "nao_informado",
            "saldo": 500,
        }
        
        personagem_id = db.criar_personagem(user_id, dados)
        
        await ctx.reply(embed=embed_sucesso(
            "🎉 Personagem criado!",
            f"Bem-vindo(a, ephemeral=True) ao jogo, **{nome}**!\n\n"
            f"💰 Você começou com $500.\n"
            f"💡 Usa `?profissoes` pra escolher uma profissão e começar a trabalhar!\n"
            f"💡 Usa `?editar` pra personalizar teu personagem (idade, aparência, etc)."
        ))

    @commands.command(name="personagens", aliases=["chars", "lista"])
    async def personagens_cmd(self, ctx: commands.Context):
        """Lista todos os teus personagens."""
        personagens = db.listar_personagens(str(ctx.author.id))
        
        if not personagens:
            await ctx.reply("👻 Você não tem nenhum personagem ainda, mano!\n\n💡 Usa `?jogar <nome>` pra criar um.", ephemeral=True)
            return
        
        embed = embed_padrao("🎭 Teus Personagens", cor=COR_PADRAO)
        
        for p in personagens:
            ativo = "🟢 ATIVO" if p["ativo"] else "⚪ Inativo"
            profissao = p.get("profissao", "Desempregado") or "Desempregado"
            embed.add_field(
                name=f"**{p['nome']}** (ID: {p['id']})",
                value=f"{ativo}\n💼 {profissao}\n💰 ${p['saldo']}",
                inline=True,
            )
        
        embed.set_footer(text="💡 Usa ?ativar <id> pra trocar de personagem")
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="ativar")
    async def ativar_cmd(self, ctx: commands.Context, personagem_id: int):
        """Ativa um personagem específico."""
        user_id = str(ctx.author.id)
        sucesso = db.definir_personagem_ativo(user_id, personagem_id)
        
        if sucesso:
            personagem = db.obter_personagem_por_id(personagem_id)
            await ctx.reply(embed=embed_sucesso(
                "Personagem ativado",
                f"Agora você tá jogando como **{personagem['nome']}**! 🎭\n\n"
                f"💡 Usa `?perfil` pra ver os detalhes."
            , ephemeral=True))
        else:
            await ctx.reply(embed=embed_erro(
                "Erro",
                "Não foi possível ativar esse personagem.\n\n"
                "💡 Usa `?personagens` pra ver teus personagens e o ID correto."
            , ephemeral=True))

    @commands.command(name="perfil")
    async def perfil_cmd(self, ctx: commands.Context):
        """Mostra o perfil do personagem ativo."""
        personagem = db.obter_personagem_ativo(str(ctx.author.id))
        
        if not personagem:
            await ctx.reply("👻 Você não tem personagem ativo, mano!\n\n💡 Usa `?jogar <nome>` pra criar um ou `?ativar <id>` pra ativar.", ephemeral=True)
            return
        
        embed = embed_padrao(f"🎭 Perfil de {personagem['nome']}", cor=COR_PADRAO)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        # ✅ CORREÇÃO: Mostra pronomes de forma bonita
        genero_raw = personagem.get("genero", "nao_informado")
        sexualidade_raw = personagem.get("sexualidade", "nao_informado")
        pronomes_raw = personagem.get("pronomes", "nao_informado")
        
        genero = NOMES_GENERO.get(genero_raw, genero_raw)
        sexualidade = NOMES_SEXUALIDADE.get(sexualidade_raw, sexualidade_raw)
        pronomes = NOMES_PRONOMES.get(pronomes_raw, pronomes_raw)
        
        embed.add_field(
            name="🌈 Identidade",
            value=f"**Gênero:** {genero}\n**Sexualidade:** {sexualidade}\n**Pronomes:** {pronomes}",
            inline=True,
        )
        
        # ✅ CORREÇÃO: Mostra data de nascimento
        data_nasc = personagem.get("data_nascimento")
        data_texto = data_nasc if data_nasc else "Não informada"
        
        embed.add_field(
            name="👤 Aparência",
            value=f"**Idade:** {personagem['idade']}\n**Nascimento:** {data_texto}\n**Pele:** {personagem['cor_pele']}\n**Cabelo:** {personagem['tipo_cabelo']} ({personagem['cor_cabelo']})",
            inline=True,
        )
        
        embed.add_field(
            name="💼 Status",
            value=f"**Profissão:** {personagem.get('profissao', 'Desempregado') or 'Desempregado'}\n**Nível:** {personagem['nivel']}\n**XP:** {personagem['xp']}",
            inline=True,
        )
        
        embed.add_field(
            name="💰 Economia",
            value=f"**Bolso:** ${personagem['saldo']}\n**Banco:** ${personagem.get('saldo_banco', 0)}",
            inline=True,
        )
        
        embed.add_field(
            name="📍 Localização",
            value=f"**Estado:** {personagem['estado']}\n**Religião:** {personagem['religiao']}",
            inline=True,
        )
        
        objetivos = personagem.get("objetivos")
        if objetivos:
            embed.add_field(
                name="🎯 Objetivos",
                value=objetivos[:200] + ("..." if len(objetivos) > 200 else ""),
                inline=False,
            )
        
        embed.set_footer(text="💡 Usa ?editar pra personalizar teu personagem")
        await ctx.reply(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Personagem(bot))
