# ===== EMOJIS =====
EMOJI_DINHEIRO = "💰"
EMOJI_XP = "⭐"
EMOJI_NIVEL = "🎖️"
EMOJI_ERRO = "❌"
EMOJI_SUCESSO = "✅"
EMOJI_AVISO = "⚠️"
EMOJI_INFO = "ℹ️"
EMOJI_TRABALHO = "💼"
EMOJI_PROFISSAO = "📋"
EMOJI_EMERGENCIA = "🚨"
EMOJI_POLICIA = "🚓"
EMOJI_SAMU = "🚑"
EMOJI_PRISAO = "🔒"
EMOJI_FAMILIA = "👨‍👩‍👧"
EMOJI_OAB = "⚖️"
EMOJI_BOLETIM = "📝"
EMOJI_PROCESSO = "📄"

# ===== CORES DOS EMBEDS =====
COR_PADRAO = 0x5865F2      # blurple
COR_SUCESSO = 0x57F287      # verde
COR_ERRO = 0xED4245         # vermelho
COR_AVISO = 0xFEE75C        # amarelo
COR_INFO = 0x5865F2         # blurple
COR_EMERGENCIA = 0xED4245   # vermelho

# ===== MENSAGENS PADRONIZADAS =====
MSG_SEM_PERSONAGEM = f"{EMOJI_ERRO} Você precisa de um personagem ativo. Use `?jogar`."
MSG_PERSONAGEM_PRESO = f"{EMOJI_PRISAO} Seu personagem está preso e não pode fazer isso agora."
MSG_ERRO_GERAL = f"{EMOJI_ERRO} Deu um erro ao executar esse comando."
MSG_SEM_PERMISSAO = f"{EMOJI_ERRO} Você não tem permissão pra usar esse comando."
MSG_USUARIO_NAO_ENCONTRADO = f"{EMOJI_ERRO} Não encontrei esse usuário. Marque com @ ou use o ID correto."

# ===== NOMES DE PROFISSÕES =====
NOMES_PROFISSOES = {
    "policial_militar": "Policial Militar",
    "policial_civil": "Policial Civil",
    "samu": "Médico SAMU",
    "medico": "Médico",
    "professor": "Professor",
    "juiz": "Juiz",
    "advogado": "Advogado",
    "advogado_criminal": "Advogado Criminal",
    "motoboy": "Motoboy",
    "empresario": "Empresário",
    "jogador_futebol": "Jogador de Futebol",
    "criminoso": "Criminoso",
}

def nome_profissao_bonito(chave: str) -> str:
    return NOMES_PROFISSOES.get(chave, chave.replace("_", " ").title())

# ===== OPÇÕES DE IDENTIDADE =====
OPCOES_GENERO = [
    "masculino", "feminino", "nao_binario", "genero_fluido", "outro", "nao_informado"
]

OPCOES_SEXUALIDADE = [
    "hetero", "homo", "bi", "pan", "assexual", "outro", "nao_informado"
]

OPCOES_PRONOMES = [
    "ele/dele", "ela/dela", "elu/delu", "qualquer", "nao_informado"
]

NOMES_GENERO = {
    "masculino": "Masculino",
    "feminino": "Feminino",
    "nao_binario": "Não-binário",
    "genero_fluido": "Gênero fluido",
    "outro": "Outro",
    "nao_informado": "Não informado",
}

NOMES_SEXUALIDADE = {
    "hetero": "Hétero",
    "homo": "Homo",
    "bi": "Bi",
    "pan": "Pan",
    "assexual": "Assexual",
    "outro": "Outro",
    "nao_informado": "Não informado",
}

NOMES_PRONOMES = {
    "ele/dele": "Ele/Dele",
    "ela/dela": "Ela/Dela",
    "elu/delu": "Elu/Delu",
    "qualquer": "Qualquer pronome",
    "nao_informado": "Não informado",
}
