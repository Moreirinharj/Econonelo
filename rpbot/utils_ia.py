import os
from anthropic import Anthropic, APIError

_cliente = None


def _pegar_cliente():
    global _cliente
    if _cliente is None:
        chave = os.getenv("ANTHROPIC_API_KEY")
        if not chave:
            return None
        _cliente = Anthropic(api_key=chave)
    return _cliente


def ia_disponivel() -> bool:
    return os.getenv("ANTHROPIC_API_KEY") is not None


def gerar_boletim_ocorrencia(nome_personagem: str, descricao_usuario: str) -> str:
    """Transforma o relato informal do jogador em um Boletim de Ocorrência formal."""
    cliente = _pegar_cliente()
    if cliente is None:
        return (
            "⚠️ A IA jurídica não está configurada (falta ANTHROPIC_API_KEY no .env). "
            "Peça pra um advogado humano registrar manualmente por enquanto."
        )

    prompt = (
        "Você é a escrivã de plantão de uma delegacia, dentro de um jogo de RPG de texto no Discord. "
        "Transforme o relato abaixo, feito por um jogador em linguagem informal, em um Boletim de "
        "Ocorrência formal e curto (no máximo 150 palavras), em português do Brasil, com seções: "
        "NATUREZA DA OCORRÊNCIA, ENVOLVIDOS, RELATO e ENCAMINHAMENTO. "
        "Não invente nomes de terceiros que não foram citados. Mantenha tom sério e burocrático.\n\n"
        f"Personagem que registrou: {nome_personagem}\n"
        f"Relato original do jogador: {descricao_usuario}"
    )

    try:
        resposta = cliente.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return resposta.content[0].text
    except APIError as e:
        return f"⚠️ Erro ao gerar o boletim pela IA: {e}"
