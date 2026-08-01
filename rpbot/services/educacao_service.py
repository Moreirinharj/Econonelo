"""Sistema de educação com proteção contra duplicatas."""
import random
import database as db
from utils.logger import log_acao

CURSOS_REAIS = [
    ("Medicina", "USP", "graduação", "superior", 12, 2000),
    ("Direito", "USP", "graduação", "superior", 10, 1500),
    ("Engenharia", "USP", "graduação", "superior", 10, 1200),
    ("Administração", "USP", "graduação", "superior", 8, 1000),
    ("Psicologia", "USP", "graduação", "superior", 10, 1100),
    ("Ciência da Computação", "USP", "graduação", "superior", 8, 1000),
    ("Medicina", "UFRJ", "graduação", "superior", 12, 1800),
    ("Arquitetura", "UFRJ", "graduação", "superior", 10, 1200),
    ("Jornalismo", "UFRJ", "graduação", "superior", 8, 900),
    ("Engenharia Civil", "UFMG", "graduação", "superior", 10, 1100),
    ("Economia", "UFMG", "graduação", "superior", 8, 1000),
    ("Odontologia", "UFMG", "graduação", "superior", 10, 1400),
    ("Medicina Veterinária", "UFPR", "graduação", "superior", 10, 1300),
    ("Biologia", "UFPR", "graduação", "superior", 8, 800),
    ("Física", "UFRGS", "graduação", "superior", 8, 800),
    ("Química", "UFRGS", "graduação", "superior", 8, 800),
    ("Artes Cênicas", "UFBA", "graduação", "superior", 8, 700),
    ("Serviço Social", "UFBA", "graduação", "superior", 8, 700),
    ("MBA Executivo", "FGV", "pós", "pos", 4, 3000),
    ("Mestrado em Direito", "USP", "pós", "pos", 4, 2500),
    ("Especialização em Cardiologia", "USP", "pós", "pos", 4, 3500),
    ("Doutorado em Computação", "USP", "pós", "pos", 8, 2000),
]

ESCOLARIDADE_POR_NIVEL = {
    "fundamental": "fundamental",
    "medio": "medio",
    "superior": "superior",
    "pos": "pos",
}


def popular_cursos() -> int:
    """Popula o banco com cursos reais."""
    existentes = db.listar_cursos()
    if len(existentes) >= 10:  # ✅ CORREÇÃO: Só não popula se já tiver 10+ cursos
        return 0
    count = 0
    for nome, univ, tipo, nivel, dur, mens in CURSOS_REAIS:
        db.criar_curso(nome, univ, tipo, nivel, dur, mens)
        count += 1
    log_acao("CURSOS_POPULADOS", f"total={count}")
    return count


def ja_fez_curso(personagem_id: int, curso_id: int) -> bool:
    """Verifica se o personagem já fez (formou) nesse curso."""
    mats = db.listar_matriculas_personagem(personagem_id)
    for m in mats:
        if m["curso_id"] == curso_id and m["status"] == "formado":
            return True
    return False


def fazer_vestibular(personagem_id: int, curso_id: int) -> dict:
    """Simula vestibular com proteção contra spam."""
    curso = db.obter_curso(curso_id)
    if not curso:
        return {"sucesso": False, "msg": "Curso não encontrado."}
    
    # ✅ CORREÇÃO: Verifica se já formou nesse curso
    if ja_fez_curso(personagem_id, curso_id):
        return {
            "sucesso": False,
            "msg": f"Você já se formou em {curso['nome']}! Não precisa fazer vestibular de novo. 🎓"
        }
    
    # Verifica se já está matriculado nesse curso
    matricula_atual = db.obter_matricula_ativa(personagem_id)
    if matricula_atual and matricula_atual["curso_id"] == curso_id:
        return {
            "sucesso": False,
            "msg": f"Você já tá matriculado em {curso['nome']}! Usa `?estudar` pra avançar."
        }
    
    personagem = db.obter_personagem_por_id(personagem_id)
    escolaridade = personagem.get("escolaridade", "nenhuma")
    bonus = {"nenhuma": 0, "fundamental": 10, "medio": 25, "superior": 15, "pos": 10}.get(escolaridade, 0)
    nota = min(10.0, round(random.uniform(3.0, 8.0) + bonus / 10, 1))
    
    aprovado = nota >= 6.0
    return {
        "sucesso": True,
        "aprovado": aprovado,
        "nota": nota,
        "curso": curso,
        "msg": f"{'✅ APROVADO' if aprovado else '❌ REPROVADO'}! Nota: {nota}/10"
    }


def matricular_no_curso(personagem_id: int, curso_id: int) -> dict:
    """Matricula personagem em curso."""
    curso = db.obter_curso(curso_id)
    if not curso:
        return {"sucesso": False, "msg": "Curso não encontrado."}
    
    # ✅ CORREÇÃO: Verifica se já formou nesse curso
    if ja_fez_curso(personagem_id, curso_id):
        return {"sucesso": False, "msg": f"Você já se formou em {curso['nome']}! Escolhe outro curso."}
    
    if db.contar_matriculas_ativas(personagem_id) > 0:
        return {"sucesso": False, "msg": "Você já tá matriculado em um curso. Termina ou tranca antes."}
    
    personagem = db.obter_personagem_por_id(personagem_id)
    if personagem["saldo"] < curso["mensalidade"]:
        return {"sucesso": False, "msg": f"Saldo insuficiente pra 1ª mensalidade (${curso['mensalidade']})."}
    
    db.atualizar_saldo_personagem(personagem_id, -curso["mensalidade"])
    db.registrar_transacao(personagem_id, "mensalidade", curso["mensalidade"], f"Matrícula em {curso['nome']} - {curso['universidade']}")
    mid = db.matricular(personagem_id, curso_id)
    return {"sucesso": True, "msg": f"Matriculado em {curso['nome']} na {curso['universidade']}!", "matricula_id": mid}


def estudar_semestre(personagem_id: int) -> dict:
    """Estuda um semestre."""
    matricula = db.obter_matricula_ativa(personagem_id)
    if not matricula:
        return {"sucesso": False, "msg": "Você não tá matriculado em nenhum curso."}
    
    personagem = db.obter_personagem_por_id(personagem_id)
    if personagem["energia"] < 20:
        return {"sucesso": False, "msg": "Energia insuficiente (precisa de 20)."}
    
    db.modificar_status_personagem(personagem_id, "energia", -20)
    db.modificar_status_personagem(personagem_id, "estresse", 5)
    
    nota_semestre = round(random.uniform(5.0, 10.0), 1)
    nova_media = round((matricula["nota_media"] * (matricula["semestre_atual"] - 1) + nota_semestre) / matricula["semestre_atual"], 1)
    db.atualizar_nota_media(matricula["id"], nova_media)
    
    db.avancar_semestre(matricula["id"])
    novo_semestre = matricula["semestre_atual"] + 1
    
    if personagem["saldo"] >= matricula["mensalidade"]:
        db.atualizar_saldo_personagem(personagem_id, -matricula["mensalidade"])
        db.registrar_transacao(personagem_id, "mensalidade", matricula["mensalidade"], f"Mensalidade semestre {novo_semestre-1}")
    
    if novo_semestre > matricula["duracao_semestres"]:
        db.concluir_curso(matricula["id"])
        nivel_escolar = matricula.get("nivel", "superior")
        escolaridade_final = ESCOLARIDADE_POR_NIVEL.get(nivel_escolar, "superior")
        db.atualizar_escolaridade(personagem_id, escolaridade_final)
        db.modificar_status_personagem(personagem_id, "felicidade", 30)
        db.modificar_status_personagem(personagem_id, "reputacao", 10)
        return {
            "sucesso": True,
            "formatura": True,
            "msg": f"🎓 FORMADO! {matricula['curso_nome']} na {matricula['universidade']}!\nNota final: {nova_media}/10\nEscolaridade: {escolaridade_final}",
        }
    
    return {
        "sucesso": True,
        "formatura": False,
        "msg": f"📚 Semestre {novo_semestre-1} concluído!\nNota: {nota_semestre}/10\nMédia: {nova_media}/10\nPróximo: semestre {novo_semestre}/{matricula['duracao_semestres']}",
    }


def trancar_matricula(personagem_id: int) -> dict:
    """Tranca a matrícula atual."""
    matricula = db.obter_matricula_ativa(personagem_id)
    if not matricula:
        return {"sucesso": False, "msg": "Sem matrícula ativa."}
    
    import database.conexao as conn_mod
    conn = conn_mod.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE matriculas SET status = 'trancado' WHERE id = ?", (matricula["id"],))
    conn.commit()
    conn.close()
    return {"sucesso": True, "msg": "Matrícula trancada."}
