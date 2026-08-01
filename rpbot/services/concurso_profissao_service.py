"""Concursos para outras profissões (PM, PC, médico, juiz, etc)."""
import random
import time
import database as db
from data.professor_data import CONCURSOS_PROFISSOES, QUESTOES_CONCURSO_PROFISSAO
from utils.logger import log_acao


def abrir_concursos_profissoes_aleatorios() -> int:
    """Abre concursos aleatórios pra várias profissões."""
    count = 0
    for profissao, dados in CONCURSOS_PROFISSOES.items():
        vagas = dados["vagas_base"] + random.randint(-2, 5)
        vagas = max(1, vagas)
        salario = dados["salario_base"] + random.randint(-500, 2000)
        encerra_em = time.time() + (72 * 3600)  # 72h
        
        concurso_id = db.abrir_concurso_profissao(
            profissao=profissao,
            orgao=dados["orgao"],
            vagas=vagas,
            salario=salario,
            encerra_em=encerra_em,
        )
        if concurso_id:
            count += 1
    
    log_acao("CONCURSOS_PROFISSOES_GERADOS", f"total={count}")
    return count


def pode_fazer_concurso_profissao(personagem_id: int, profissao: str) -> dict:
    """Verifica se pode fazer concurso pra essa profissão."""
    if profissao not in CONCURSOS_PROFISSOES:
        return {"pode": False, "msg": "Profissão não tem concurso."}
    
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return {"pode": False, "msg": "Personagem não encontrado."}
    
    # Verifica se já passou
    if db.ja_passou_concurso_profissao(personagem_id, profissao):
        return {"pode": False, "msg": f"Você já passou no concurso de {profissao.replace('_', ' ')}!"}
    
    # Verifica escolaridade
    escolaridade = personagem.get("escolaridade", "nenhuma")
    requisito = CONCURSOS_PROFISSOES[profissao]["requisito_escolaridade"]
    
    niveis = {"nenhuma": 0, "fundamental": 1, "medio": 2, "superior": 3, "pos": 4}
    if niveis.get(escolaridade, 0) < niveis.get(requisito, 0):
        return {
            "pode": False,
            "msg": f"Você precisa de {requisito} pra fazer esse concurso. Sua escolaridade: {escolaridade}.",
            "helper": "💡 Usa `?universidades` pra ver cursos e `?estudar` pra se formar."
        }
    
    return {"pode": True, "msg": "OK"}


def gerar_prova_profissao(profissao: str, num_questoes: int = 5) -> dict:
    """Gera prova de concurso de profissão."""
    if profissao not in QUESTOES_CONCURSO_PROFISSAO:
        return {"sucesso": False, "msg": "Sem questões pra essa profissão."}
    
    todas = QUESTOES_CONCURSO_PROFISSAO[profissao].copy()
    random.shuffle(todas)
    questoes = todas[:num_questoes]
    
    return {"sucesso": True, "questoes": questoes, "total": len(questoes)}


def processar_aprovacao_profissao(personagem_id: int, profissao: str, nota: float, concurso_id: str) -> dict:
    """Processa aprovação em concurso de profissão."""
    aprovado = nota >= 7.0
    
    if not aprovado:
        return {
            "sucesso": True,
            "aprovado": False,
            "msg": f"❌ REPROVADO! Nota {nota}/10 (mínimo 7.0).\n💡 Estuda mais e tenta de novo!",
        }
    
    # Registra aprovação
    db.registrar_aprovacao_profissao(personagem_id, profissao, nota, concurso_id)
    
    nome_profissao = profissao.replace("_", " ").title()
    return {
        "sucesso": True,
        "aprovado": True,
        "msg": f"🎉 APROVADO no concurso de **{nome_profissao}**!\n💡 Agora você pode usar `?escolherprofissao {profissao}` pra assumir o cargo.",
    }
