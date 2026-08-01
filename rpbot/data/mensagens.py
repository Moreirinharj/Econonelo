"""
Mensagens do bot em linguagem Geração Z, brasileiras, com gírias e humor.
Cada mensagem tem um "helper" sugerindo o comando certo pro jogador.
"""
import random

# ===== SEM DINHEIRO =====
SEM_DINHEIRO_COMPRA = [
    {"msg": "💸 Tá liso, mano! Essa grana não tá nem nos seus sonhos. 💀", "helper": "💡 Tenta `?trabalhar` pra fazer uma grana ou `?trabalharrapido` se tiver com pressa."},
    {"msg": "🫠 Tá duro(a)? Dorme, betinha. Essa compra vai ter que esperar. 😴", "helper": "💡 Usa `?profissoes` pra ver as vagas disponíveis e começar a ganhar."},
    {"msg": "😭 A conta bancária tá mais vazia que a geladeira de estudante. Vacilou!", "helper": "💡 Dica: `?trabalhar` paga bem se tu manjar da profissão."},
    {"msg": "💀 Perdeu play, parceiro. Grana insuficiente pra essa parada.", "helper": "💡 Tenta `?saldo` pra ver quanto tu tem, e `?trabalhar` pra ganhar mais."},
    {"msg": "🤡 Quis bancar o playboy mas a conta não deixou. Clássico.", "helper": "💡 Usa `?carteira` pra ver teu dinheiro todo e planejar melhor."},
]

# ===== SEM ENERGIA / STATUS BAIXO =====
SEM_ENERGIA = [
    {"msg": "😵 Tu tá mais morto que vivo, mano. Vai dormir, pelo amor!", "helper": "💡 Usa `?dormir 8` pra recuperar a energia (padrão 8h)."},
    {"msg": "🪫 Bateria em 1%. Tu não vai render nada assim, parceiro.", "helper": "💡 `?dormir` é teu melhor amigo agora. Descansa um pouco!"},
    {"msg": "🧟 Parece zumbi de The Last of Us. Vai descansar, vai.", "helper": "💡 `?dormir [horas]` — quanto mais horas, mais energia volta."},
]

SEM_FOME = [
    {"msg": "🍽️ Tua barriga tá roncando mais que moto sem escapamento. Come algo aí!", "helper": "💡 Usa `?comer` pra encher a pança ou `?usaritem <id>` se tiver comida no inventário."},
    {"msg": "😩 Fome de leão, parceiro. Tu vai desmaiar se não comer.", "helper": "💡 `?comer` recupera 30 de fome. Ou compra comida com `?daritem comida`."},
]

SEM_HIGIENE = [
    {"msg": "🤢 Mano, tu tá fedendo. Ninguém aguenta mais ficar perto. 🤮", "helper": "💡 Usa `?banho` pra tomar aquele banho e voltar a ser gente."},
    {"msg": "🧼 Higiene tá osso, hein? Parece que tu mora na rua.", "helper": "💡 `?banho` resolve isso rapidinho. Vai, toma um banho!"},
]

MUITO_ESTRESSADO = [
    {"msg": "😤 Tu tá a ponto de explodir, mano. Respira fundo aí.", "helper": "💡 Usa `?relaxar` pra baixar o estresse em 20 pontos."},
    {"msg": "🤯 Cabeça a mil, parceiro. Tu precisa de um tempo.", "helper": "💡 `?relaxar` é teu salvador agora. Usa sem moderação."},
]

# ===== SUCESSO =====
SUCESSO_TRABALHO = [
    {"msg": "🔥 Mandou bem demais, lenda! Grana no bolso e XP na conta.", "helper": ""},
    {"msg": "💪 Tankou geral! Tu é o bicho, parceiro.", "helper": ""},
    {"msg": "🎯 Acertou na mosca! Tu é foda, hein.", "helper": ""},
    {"msg": "✨ Brilhou, estrela! Mais uma grana entrando.", "helper": ""},
    {"msg": "🏆 MVP do dia! Ninguém te segura.", "helper": ""},
]

SUBIU_NIVEL = [
    {"msg": "🎉 LEVEL UP, BEBÊ! Subiu de nível, tá voando! 🚀", "helper": ""},
    {"msg": "⬆️ EVOLUÍ! Agora tu é nível {nivel}, lenda! 💎", "helper": ""},
    {"msg": "🌟 SUBIU! Tu tá cada dia mais forte, mano!", "helper": ""},
]

# ===== FALHOU =====
FALHOU_MINIGAME = [
    {"msg": "💀 FOI DE BASE, PARCEIRO. Decisão errada, vacilou geral.", "helper": "💡 Tenta de novo com `?trabalhar` — na próxima tu manda bem!"},
    {"msg": "😭 Perdeu play, mano. Essa tu errou feio.", "helper": "💡 Relaxa, `?trabalhar` de novo e tenta outra escolha."},
    {"msg": "🤡 Deu ruim, zé. Tu se deu mal nessa.", "helper": "💡 Dica: presta atenção nas opções, nem tudo que parece é."},
    {"msg": "🫠 Foi de arrasta pra cima. Melhor sorte na próxima.", "helper": "💡 `?trabalhar` é teu amigo. Bora tentar de novo!"},
]

# ===== PRESO =====
PRESO = [
    {"msg": "🔒 FOI CANA, MANO! Tu tá preso agora. A vida é assim mesmo. 😬", "helper": "💡 Precisa de um advogado? `?chamaroab` pode ajudar. Ou espera a fiança ser paga."},
    {"msg": "⛓️ Preso em flagrante! Agora é rezar pro juiz ser bonzinho. 🙏", "helper": "💡 Usa `?processos` pra ver teu caso e `?pagarfianca` pra sair mais rápido."},
    {"msg": "🚔 Deu merda, parceiro. Tu tá na cadeia agora.", "helper": "💡 `?ficha` mostra teu histórico criminal. Toma juízo!"},
]

# ===== SEM PERSONAGEM =====
SEM_PERSONAGEM = [
    {"msg": "👻 Ei, tu não tem personagem ainda, mano! Cria um aí.", "helper": "💡 Usa `?jogar` pra criar teu personagem e começar a aventura!"},
    {"msg": "🎭 Cadê teu personagem? Sumiu? Cria um novo, ué.", "helper": "💡 `?jogar` é o comando mágico pra começar tua jornada."},
]

# ===== SEM PROFISSÃO =====
SEM_PROFISSAO = [
    {"msg": "💼 Desempregado, hein? Tá na hora de arrumar um trampo.", "helper": "💡 Usa `?profissoes` pra ver as vagas e `?escolherprofissao <nome>` pra escolher."},
    {"msg": "🤷 Sem profissão? Tu tá de brincadeira, mano.", "helper": "💡 `?profissoes` mostra tudo. Escolhe uma e vai trabalhar!"},
]

# ===== ITEM NÃO ENCONTRADO =====
ITEM_NAO_ENCONTRADO = [
    {"msg": "🔍 Esse item não existe no teu inventário, parceiro.", "helper": "💡 Usa `?inventario` pra ver o que tu tem."},
    {"msg": "❌ Cadê esse item? Sumiu, mano.", "helper": "💡 `?inventario` mostra tudo que tu carrega."},
]

# ===== CASA/VEÍCULO =====
CASA_NAO_ENCONTRADA = [
    {"msg": "🏚️ Essa casa não existe, mano. Tu tá sonhando?", "helper": "💡 `?casas` mostra as disponíveis pra comprar."},
]

VEICULO_NAO_ENCONTRADO = [
    {"msg": "🚗 Que veículo é esse? Nunca vi na tua garagem, parceiro.", "helper": "💡 `?garagem` mostra teus veículos. `?veiculos` mostra os da loja."},
]

# ===== AJUDA GENÉRICA =====
AJUDA_GENERICA = [
    "💡 Dica: usa `?ajuda` pra ver todos os comandos disponíveis.",
    "💡 Se perdeu? `?ajuda <comando>` mostra detalhes de qualquer comando.",
    "💡 Tá com dúvida? `?status` mostra como tu tá. `?carteira` mostra teu dinheiro.",
]


def escolher_mensagem(categoria: str) -> dict:
    """Escolhe uma mensagem aleatória de uma categoria."""
    lista = globals().get(categoria.upper(), [])
    if not lista:
        return {"msg": "Ops, algo deu errado.", "helper": ""}
    return random.choice(lista)


def mensagem_com_helper(categoria: str) -> str:
    """Retorna mensagem + helper formatados juntos."""
    dados = escolher_mensagem(categoria)
    if dados["helper"]:
        return f"{dados['msg']}\n\n{dados['helper']}"
    return dados["msg"]


def escolher_aleatorio(lista: list) -> str:
    """Escolhe uma mensagem aleatória de uma lista qualquer."""
    if not lista:
        return ""
    return random.choice(lista)
