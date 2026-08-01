"""Service pra consultar e ajustar balanceamento."""
import data.balanceamento as bal
from utils.logger import log_acao


def obter_resumo_balanceamento() -> dict:
    """Retorna resumo dos principais valores de balanceamento."""
    return {
        "economia": {
            "saldo_inicial": bal.SALDO_INICIAL,
            "limite_cartao_inicial": bal.LIMITE_CARTAO_INICIAL,
            "preco_combustivel": bal.PRECO_LITRO_COMBUSTIVEL,
            "imposto_renda": f"{bal.IMPOSTO_RENDA_PERCENTUAL*100:.0f}%",
        },
        "salarios": bal.SALARIOS,
        "progressao": {
            "xp_base": bal.XP_BASE_PROXIMO_NIVEL,
            "xp_multiplicador": bal.XP_MULTIPLICADOR_POR_NIVEL,
            "xp_nivel_1_para_2": bal.xp_para_proximo_nivel(1),
            "xp_nivel_5_para_6": bal.xp_para_proximo_nivel(5),
            "xp_nivel_10_para_11": bal.xp_para_proximo_nivel(10),
        },
        "chances": {
            "prisao_base": f"{bal.CHANCE_PRISAO_BASE*100:.0f}%",
            "prisao_max": f"{bal.CHANCE_PRISAO_MAX*100:.0f}%",
            "roubo": f"{bal.CHANCE_ROUBO_SUCESSO*100:.0f}%",
            "assalto": f"{bal.CHANCE_ASSALTO_SUCESSO*100:.0f}%",
            "fugir_policia": f"{bal.CHANCE_FUGIR_POLICIA*100:.0f}%",
        },
        "status": {
            "deterioracao_fome_hora": bal.DETERIORACAO_FOME,
            "deterioracao_energia_hora": bal.DETERIORACAO_ENERGIA,
            "deterioracao_higiene_hora": bal.DETERIORACAO_HIGIENE,
            "deterioracao_felicidade_hora": bal.DETERIORACAO_FELICIDADE,
        },
        "limites": {
            "max_personagens": bal.MAX_PERSONAGENS_POR_USUARIO,
            "peso_max_base": bal.PESO_MAXIMO_BASE,
        },
    }


def validar_salario_profissao(profissao: str, min_val: int, max_val: int) -> bool:
    """Valida se salário de profissão é razoável."""
    if min_val < 0 or max_val < min_val:
        return False
    if max_val > 10000:
        return False
    return True


def simular_progressao(nivel_inicial: int = 1, trabalhos: int = 100, profissao: str = "motoboy") -> dict:
    """Simula progressão de XP pra uma profissão."""
    import data.balanceamento as bal
    
    salario = bal.obter_salario(profissao)
    xp_por_trabalho = salario["xp"]
    
    nivel = nivel_inicial
    xp_acumulado = 0
    trabalhos_realizados = 0
    
    for _ in range(trabalhos):
        xp_acumulado += xp_por_trabalho
        trabalhos_realizados += 1
        
        while xp_acumulado >= bal.xp_para_proximo_nivel(nivel):
            xp_acumulado -= bal.xp_para_proximo_nivel(nivel)
            nivel += 1
    
    return {
        "profissao": profissao,
        "nivel_inicial": nivel_inicial,
        "nivel_final": nivel,
        "trabalhos": trabalhos_realizados,
        "xp_por_trabalho": xp_por_trabalho,
    }
