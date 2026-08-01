import discord
from discord.ext import commands

import database as db
from data.constantes import (
    COR_PADRAO, COR_SUCESSO, COR_ERRO, COR_AVISO,
    OPCOES_GENERO, OPCOES_SEXUALIDADE, OPCOES_PRONOMES,
    NOMES_GENERO, NOMES_SEXUALIDADE, NOMES_PRONOMES,
)
from utils.embeds import embed_padrao, embed_sucesso, embed_erro, embed_info, embed_aviso


# Campos que o jogador PODE editar
CAMPOS_EDITAVEIS = {
    "nome": {
        "descricao": "Nome do personagem",
        "exemplo": "João Silva",
        "validar": lambda v: 2 <= len(v.strip()) <= 30,
        "erro": "Nome precisa ter entre 2 e 30 caracteres, mano.",
    },
    "idade": {
        "descricao": "Idade do personagem",
        "exemplo": "25",
        "validar": lambda v: v.isdigit() and 1 <= int(v) <= 120,
        "erro": "Idade tem que ser número entre 1 e 120, parceiro.",
        "converter": int,
    },
    "cor_pele": {
        "descricao": "Cor da pele",
        "exemplo": "morena",
        "validar": lambda v: 2 <= len(v.strip()) <= 30,
        "erro": "Cor da pele precisa ter entre 2 e 30 caracteres.",
    },
    "tipo_cabelo": {
        "descricao": "Tipo de cabelo",
        "exemplo": "cacheado",
        "validar": lambda v: 2 <= len(v.strip()) <= 30,
        "erro": "Tipo de cabelo precisa ter entre 2 e 30 caracteres.",
    },
    "cor_cabelo": {
        "descricao": "Cor do cabelo",
        "exemplo": "preto",
        "validar": lambda v: 2 <= len(v.strip()) <= 30,
        "erro": "Cor do cabelo precisa ter entre 2 e 30 caracteres.",
    },
    "estado": {
        "descricao": "Estado onde mora",
        "exemplo": "SP",
        "validar": lambda v: 2 <= len(v.strip()) <= 30,
        "erro": "Estado precisa ter entre 2 e 30 caracteres.",
    },
    "religiao": {
        "descricao": "Religião do personagem",
        "exemplo": "católico",
        "validar": lambda v: 2 <= len(v.strip()) <= 30,
        "erro": "Religião precisa ter entre 2 e 30 caracteres.",
    },
    "data_nascimento": {
        "descricao": "Data de nascimento",
        "exemplo": "15/03/2000",
        "validar": lambda v: len(v.strip()) <= 20,
        "erro": "Data de nascimento muito longa (máx 20 caracteres).",
    },
    "objetivos": {
        "descricao": "Objetivos de vida",
        "exemplo": "Ficar rico e viajar o mundo",
        "validar": lambda v: len(v.strip()) <= 200,
        "erro": "Objetivos muito longos (máx 200 caracteres).",
    },
    "genero": {
        "descricao": "Gênero do personagem",
        "exemplo": "masculino",
        "validar": lambda v: v.lower() in OPCOES_GENERO,
        "erro": f"Gênero inválido. Opções: {', '.join(OPCOES_GENERO)}",
        "converter": lambda v: v.lower(),
    },
    "sexualidade": {
        "descricao": "Sexualidade do personagem",
        "exemplo": "hetero",
        "validar": lambda v: v.lower() in OPCOES_SEXUALIDADE,
        "erro": f"Sexualidade inválida. Opções: {', '.join(OPCOES_SEXUALIDADE)}",
        "converter": lambda v: v.lower(),
    },
    "pronomes": {
        "descricao": "Pronomes do personagem",
        "exemplo": "ele/dele",
        "validar": lambda v: v.lower() in OPCOES_PRONOMES,
        "erro": f"Pronomes inválidos. Opções: {', '.join(OPCOES_PRONOMES)}",
        "converter": lambda v: v.lower(),
    },
}

# Campos que o jogador NÃO PODE editar (mesmo tentando)
CAMPOS_PROIBIDOS = {
    "saldo": "💰 Saldo? Tu acha que eu sou bobo? Usa `?trabalhar` pra ganhar dinheiro, mano.",
    "saldo_banco": "💰 Saldo do banco? Nem sonhando, parceiro. Trabalha aí!",
    "limite_cartao": "💳 Limite do cartão? Isso o banco decide, não tu.",
    "fatura_cartao": "💳 Fatura do cartão? Paga ela com `?pagarcartao`, não edita.",
    "chave_pix": "🔑 Chave PIX? Usa `?pixchave <chave>` pra mudar.",
    "profissao": "💼 Profissão? Usa `?escolherprofissao` ou `?pedirdemissao`.",
    "nivel": "🎖️ Nível? Sobe trabalhando, mano. Não tem atalho.",
    "xp": "⭐ XP? Ganha trabalhando, não editando.",
    "saude": "❤️ Saúde? Usa `?usaritem` com remédio.",
    "energia": "⚡ Energia? Usa `?dormir`.",
    "fome": "🍔 Fome? Usa `?comer`.",
    "felicidade": "😊 Felicidade? Vive a vida, mano.",
    "estresse": "😰 Estresse? Usa `?relaxar`.",
    "higiene": "🚿 Higiene? Usa `?banho`.",
    "reputacao": "⭐ Reputação? Conquista trabalhando.",
    "preso": "🔒 Preso? Só sai com fiança ou absolvição.",
    "ficha_criminal": "📋 Ficha criminal? Só o juiz limpa isso.",
    "escolaridade": "🎓 Escolaridade? Forma na faculdade com `?estudar`.",
    "ativo": "🎭 Personagem ativo? Usa `?ativar <id>`.",
}


class Editar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="editar", aliases=["edit", "mudar"])
    async def editar_cmd(self, ctx: commands.Context, campo: str = None, *, valor: str = None):
        """Edita um campo pessoal do teu personagem."""
        personagem = db.obter_personagem_ativo(str(ctx.author.id))
        if not personagem:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.")
            return
        
        if not campo:
            await ctx.reply(embed=embed_aviso(
                "Como editar?",
                "Usa `?editar <campo> <valor>`\n\n"
                "💡 Exemplos:\n"
                "• `?editar nome João Silva`\n"
                "• `?editar idade 25`\n"
                "• `?editar genero masculino`\n\n"
                "Pra ver todos os campos editáveis: `?editarlist`"
            ))
            return
        
        campo = campo.lower()
        
        # Verifica se é um campo proibido
        if campo in CAMPOS_PROIBIDOS:
            await ctx.reply(f"🚫 {CAMPOS_PROIBIDOS[campo]}\n\n💡 Usa `?editarlist` pra ver o que tu PODE editar.")
            return
        
        # Verifica se é um campo editável
        if campo not in CAMPOS_EDITAVEIS:
            await ctx.reply(embed=embed_erro(
                "Campo inválido",
                f"Não conheço esse campo, mano.\n\n"
                f"💡 Usa `?editarlist` pra ver os campos que tu pode editar."
            ))
            return
        
        if not valor:
            await ctx.reply(embed=embed_aviso(
                "Cadê o valor?",
                f"Tu esqueceu de dizer o novo valor pro campo **{campo}**.\n\n"
                f"💡 Exemplo: `?editar {campo} {CAMPOS_EDITAVEIS[campo]['exemplo']}`"
            ))
            return
        
        info_campo = CAMPOS_EDITAVEIS[campo]
        
        # Validação
        if not info_campo["validar"](valor):
            await ctx.reply(embed=embed_erro("Valor inválido", info_campo["erro"]))
            return
        
        # Conversão (se precisar)
        valor_final = info_campo.get("converter", lambda v: v)(valor)
        
        # Salva
        sucesso = db.editar_personagem_pessoal(personagem["id"], campo, valor_final)
        if not sucesso:
            await ctx.reply(embed=embed_erro("Erro", "Não foi possível editar. Tenta de novo."))
            return
        
        # Mensagem de sucesso personalizada
        if campo == "nome":
            msg = f"🎭 Nome atualizado pra **{valor_final}**! Agora tu é esse, mano."
        elif campo == "idade":
            msg = f"🎂 Idade atualizada pra **{valor_final} anos**! O tempo não para, hein."
        elif campo == "genero":
            msg = f"🌈 Gênero atualizado pra **{NOMES_GENERO.get(valor_final, valor_final)}**! Respeito é tudo."
        elif campo == "sexualidade":
            msg = f"💖 Sexualidade atualizada pra **{NOMES_SEXUALIDADE.get(valor_final, valor_final)}**! Cada um é quem é."
        elif campo == "pronomes":
            msg = f"🗣️ Pronomes atualizados pra **{NOMES_PRONOMES.get(valor_final, valor_final)}**! Anotado."
        elif campo == "objetivos":
            msg = f"🎯 Objetivos atualizados! Agora tu quer: **{valor_final}**\n💡 Bora correr atrás!"
        else:
            msg = f"✅ **{campo}** atualizado pra **{valor_final}**! Ficou show, mano."
        
        await ctx.reply(embed=embed_sucesso("Personagem editado", msg))

    @commands.command(name="editarlist", aliases=["editarlista", "campos"])
    async def editarlist_cmd(self, ctx: commands.Context):
        """Mostra todos os campos que tu pode editar."""
        personagem = db.obter_personagem_ativo(str(ctx.author.id))
        if not personagem:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.")
            return
        
        embed = embed_padrao("📝 Campos Editáveis", cor=COR_PADRAO)
        embed.description = "Aqui estão os campos que tu pode mudar no teu personagem:\n\n💡 Usa `?editar <campo> <valor>` pra editar."
        
        for campo, info in CAMPOS_EDITAVEIS.items():
            valor_atual = personagem.get(campo, "—")
            if valor_atual is None:
                valor_atual = "—"
            embed.add_field(
                name=f"🔹 {campo}",
                value=f"**Atual:** {valor_atual}\n**Exemplo:** `{info['exemplo']}`",
                inline=True,
            )
        
        embed.set_footer(text="💡 Tu NÃO pode editar saldo, profissão, nível, XP, etc. Isso se conquista jogando!")
        await ctx.reply(embed=embed)

    @commands.command(name="tentareditar", hidden=True)
    async def tentareditar_cmd(self, ctx: commands.Context, campo: str = None, *, valor: str = None):
        """Comando escondido que mostra o que acontece se tentar editar algo proibido."""
        if not campo:
            await ctx.reply("🤔 Quer tentar editar o quê, mano?")
            return
        
        campo = campo.lower()
        if campo in CAMPOS_PROIBIDOS:
            await ctx.reply(f"🚫 {CAMPOS_PROIBIDOS[campo]}")
        else:
            await ctx.reply("💡 Esse campo tu pode editar sim! Usa `?editar {campo} <valor>`.".format(campo=campo))


async def setup(bot: commands.Bot):
    await bot.add_cog(Editar(bot))
