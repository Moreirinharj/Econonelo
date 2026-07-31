def formatar_moeda(valor: float) -> str:
    """Formata valores em reais seguindo a regra: r / k / m / b"""
    sinal = "-" if valor < 0 else ""
    valor = abs(valor)

    if valor < 1000:
        return f"{sinal}{int(valor)}r"
    elif valor < 1_000_000:
        texto = f"{valor / 1000:.1f}".rstrip("0").rstrip(".")
        return f"{sinal}{texto}k"
    elif valor < 1_000_000_000:
        texto = f"{valor / 1_000_000:.1f}".rstrip("0").rstrip(".")
        return f"{sinal}{texto}m"
    else:
        texto = f"{valor / 1_000_000_000:.1f}".rstrip("0").rstrip(".")
        return f"{sinal}{texto}b"
