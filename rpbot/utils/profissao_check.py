"""Utilitários para verificar profissão e mostrar comandos exclusivos."""
import discord
from discord.ext import commands
import database as db
from data.constantes import EMOJI_ERRO


# Mapeamento de profissões -> comandos exclusivos
COMANDOS_POR_PROFISSAO = {
    "policial_militar": {
        "nome": "Policial Militar",
        "comandos": [
            ("?trabalhar", "Iniciar patrulha (minigame)"),
            ("?patrulha", "Iniciar patrulha (alias)"),
            ("?multar <@user> <motivo> [valor]", "Aplicar multa em alguém"),
            ("?revistar <@user>", "Revistar alguém (ver itens/ficha)"),
            ("?acionar190 <desc>", "Chamar reforço policial"),
            ("?atender <id>", "Atender chamado 190"),
            ("?boletim <desc>", "Registrar B.O."),
        ],
        "descricao": "🚓 Comandos exclusivos de Policial Militar"
    },
    "policial_civil": {
        "nome": "Policial Civil",
        "comandos": [
            ("?trabalhar", "Iniciar investigação (minigame)"),
            ("?multar <@user> <motivo> [valor]", "Aplicar multa em alguém"),
            ("?revistar <@user>", "Revistar alguém (ver itens/ficha)"),
            ("?boletim <desc>", "Registrar B.O."),
            ("?processos", "Ver processos em andamento"),
        ],
        "descricao": "🔍 Comandos exclusivos de Policial Civil"
    },
    "samu": {
        "nome": "Médico SAMU",
        "comandos": [
            ("?trabalhar", "Iniciar emergência (minigame)"),
            ("?diagnosticar [(@user)]", "Ver status de saúde de alguém"),
            ("?acionar192 <desc>", "Chamar ambulância"),
            ("?atender <id>", "Atender chamado 192"),
        ],
        "descricao": "🚑 Comandos exclusivos de SAMU"
    },
    "medico": {
        "nome": "Médico",
        "comandos": [
            ("?trabalhar", "Iniciar consulta (minigame)"),
            ("?diagnosticar [(@user)]", "Ver status de saúde de alguém"),
            ("?prescrever <@user> <receita>", "Prescrever receita pra alguém"),
            ("?usaritem <id>", "Usar remédio do inventário"),
        ],
        "descricao": "🩺 Comandos exclusivos de Médico"
    },
    "professor": {
        "nome": "Professor",
        "comandos": [
            ("?trabalhar", "Iniciar aula (minigame)"),
            ("?aplicarprova <@user>", "Aplicar prova em alguém"),
        ],
        "descricao": "📚 Comandos exclusivos de Professor"
    },
    "motoboy": {
        "nome": "Motoboy",
        "comandos": [
            ("?trabalhar", "Iniciar entrega (minigame)"),
            ("?aceitarpedido", "Aceitar pedido de entrega (alias)"),
        ],
        "descricao": "🛵 Comandos exclusivos de Motoboy"
    },
    "criminoso": {
        "nome": "Criminoso",
        "comandos": [
            ("?trabalhar", "Iniciar atividade criminosa (minigame)"),
            ("?roubar <@user>", "Tentar roubar alguém (risco!)"),
            ("?ficha", "Ver ficha criminal"),
        ],
        "descricao": "🔫 Comandos exclusivos de Criminoso"
    },
    "advogado": {
        "nome": "Advogado",
        "comandos": [
            ("?trabalhar", "Iniciar audiência (minigame)"),
            ("?consultar <@user> <assunto>", "Fazer consulta jurídica (cobra $300)"),
            ("?assumirdefesa <id>", "Assumir defesa de um processo"),
            ("?processos", "Ver processos em andamento"),
        ],
        "descricao": "⚖️ Comandos exclusivos de Advogado"
    },
    "advogado_criminal": {
        "nome": "Advogado Criminal",
        "comandos": [
            ("?trabalhar", "Iniciar audiência criminal (minigame)"),
            ("?consultar <@user> <assunto>", "Fazer consulta jurídica (cobra $300)"),
            ("?assumirdefesa <id>", "Assumir defesa criminal"),
            ("?processos", "Ver processos criminais"),
        ],
        "descricao": "🔨 Comandos exclusivos de Advogado Criminal"
    },
    "empresario": {
        "nome": "Empresário",
        "comandos": [
            ("?trabalhar", "Iniciar negócios (minigame)"),
            ("?contratar <@user> <profissao>", "Contratar alguém (custa $500)"),
            ("?demitir <@user>", "Demitir alguém"),
        ],
        "descricao": "💼 Comandos exclusivos de Empresário"
    },
    "jogador_futebol": {
        "nome": "Jogador de Futebol",
        "comandos": [
            ("?trabalhar", "Iniciar jogo (minigame)"),
        ],
        "descricao": "⚽ Comandos exclusivos de Jogador de Futebol"
    },
    "juiz": {
        "nome": "Juiz",
        "comandos": [
            ("?trabalhar", "Iniciar julgamento (minigame)"),
            ("?julgar <id> <veredito> [dias]", "Julgar um processo"),
        ],
        "descricao": "👨‍⚖️ Comandos exclusivos de Juiz"
    },
}


def obter_comandos_profissao(profissao: str) -> dict:
    """Retorna comandos exclusivos de uma profissão."""
    return COMANDOS_POR_PROFISSAO.get(profissao, None)


def verificar_profissao(profissoes_permitidas: list):
    """
    Decorator que verifica se o jogador tem uma das profissões permitidas.
    Uso: @verificar_profissao(["policial_militar", "policial_civil"])
    """
    async def predicate(ctx):
        personagem = db.obter_personagem_ativo(str(ctx.author.id))
        if not personagem:
            await ctx.reply("👻 Tu não tem personagem, mano! Usa `?jogar` pra criar.")
            return False
        
        profissao = personagem.get("profissao")
        if not profissao:
            await ctx.reply("💼 Tu não tem profissão, mano! Usa `?profissoes` pra ver as vagas.")
            return False
        
        if profissao not in profissoes_permitidas:
            nomes = ", ".join(COMANDOS_POR_PROFISSAO.get(p, {}).get("nome", p) for p in profissoes_permitidas)
            await ctx.reply(f"🚫 Esse comando é só pra: **{nomes}**\n💡 Tu é {COMANDOS_POR_PROFISSAO.get(profissao, {}).get('nome', profissao)}.")
            return False
        
        return True
    
    return commands.check(predicate)


def criar_embed_comandos_profissao(profissao: str) -> discord.Embed:
    """Cria um embed com os comandos exclusivos da profissão."""
    dados = COMANDOS_POR_PROFISSAO.get(profissao)
    if not dados:
        return None
    
    embed = discord.Embed(
        title=dados["descricao"],
        description="Aqui estão os comandos que tu pode usar:",
        color=discord.Color.blue()
    )
    
    for cmd, desc in dados["comandos"]:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="💡 Usa ?pedirdemissao pra sair da profissão")
    return embed
