"""Sistema de seed/população automática do mundo."""
import time
import database as db
from utils.logger import log_acao, log_info


def mundo_esta_populado() -> bool:
    """Verifica se o mundo já foi populado."""
    estado = db.obter_estado_mundo("mundo_populado")
    return estado == "1"


def marcar_mundo_como_populado():
    """Marca o mundo como populado."""
    db.atualizar_estado_mundo("mundo_populado", "1")
    db.atualizar_estado_mundo("mundo_populado_em", str(time.time()))


def popular_mundo_completo() -> dict:
    """Popula TUDO do mundo automaticamente."""
    resultados = {
        "empresas": 0,
        "cursos": 0,
        "npcs": 0,
        "locais": 0,
        "casas": 0,
        "veiculos": 0,
        "concursos": 0,
    }
    
    log_info("🌍 Iniciando população automática do mundo...")
    
    # 1. Empresas reais
    try:
        from services.empresa_service import popular_empresas
        resultados["empresas"] = popular_empresas()
        log_info(f"  🏢 {resultados['empresas']} empresas populadas")
    except Exception as e:
        log_acao("ERRO_SEED_EMPRESAS", str(e))
    
    # 2. Cursos universitários
    try:
        from services.educacao_service import popular_cursos
        resultados["cursos"] = popular_cursos()
        log_info(f"  🎓 {resultados['cursos']} cursos populados")
    except Exception as e:
        log_acao("ERRO_SEED_CURSOS", str(e))
    
    # 3. NPCs (professores, médicos, policiais, etc.)
    try:
        from services.npc_service import popular_npcs
        resultados["npcs"] = popular_npcs()
        log_info(f"  👥 {resultados['npcs']} NPCs populados")
    except Exception as e:
        log_acao("ERRO_SEED_NPCS", str(e))
    
    # 4. Locais (hospitais, escolas, delegacias)
    try:
        from services.local_service import popular_mundo
        resultados["locais"] = popular_mundo()
        log_info(f"  📍 {resultados['locais']} locais populados")
    except Exception as e:
        log_acao("ERRO_SEED_LOCAIS", str(e))
    
    # 5. Casas disponíveis
    try:
        from services.casa_service import popular_casas
        resultados["casas"] = popular_casas()
        log_info(f"  🏠 {resultados['casas']} casas populadas")
    except Exception as e:
        log_acao("ERRO_SEED_CASAS", str(e))
    
    # 6. Veículos disponíveis
    try:
        from services.veiculo_service import popular_veiculos
        resultados["veiculos"] = popular_veiculos()
        log_info(f"  🚗 {resultados['veiculos']} veículos populados")
    except Exception as e:
        log_acao("ERRO_SEED_VEICULOS", str(e))
    
    # 7. Concursos abertos
    try:
        from services.concurso_service import popular_concursos
        resultados["concursos"] = popular_concursos()
        log_info(f"  📋 {resultados['concursos']} concursos populados")
    except Exception as e:
        log_acao("ERRO_SEED_CONCURSOS", str(e))
    
    # Marcar como populado
    marcar_mundo_como_populado()
    
    log_info("🌍 População do mundo concluída!")
    return resultados
