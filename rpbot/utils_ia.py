import os
import requests

def ia_disponivel() -> bool:
    return os.getenv("GROQ_API_KEY") is not None


def gerar_boletim_ocorrencia(nome_personagem: str, descricao_usuario: str) -> str:
    """Transforma o relato informal do jogador em um Boletim de Ocorrência formal."""
    chave = os.getenv("GROQ_API_KEY")
    if not chave:
        return (
            "⚠️ A IA jurídica não está configurada (falta GROQ_API_KEY no .env). "
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
        resposta = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {chave}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        resposta.raise_for_status()
        dados = resposta.json()
        return dados["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Erro ao gerar o boletim pela IA: {e}"
