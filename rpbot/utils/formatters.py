"""Funções de formatação."""


def formatar_moeda(valor: int) -> str:
    """Formata valor em moeda (ex: 1500 -> $1.500)."""
    return f"${valor:,}".replace(",", ".")
