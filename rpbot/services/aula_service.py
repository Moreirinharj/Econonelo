"""Sistema de aulas dos professores."""
import random
import database as db
from utils.logger import log_acao

TEMAS_POR_ESPECIALIDADE = {
    "direito": ["Direito Constitucional", "Direito Civil", "Direito Penal", "Processo Civil", "Ética Jurídica"],
    "medicina": ["Anatomia Humana", "Fisiologia", "Patologia", "Clínica Médica", "Ética Médica"],
    "engenharia": ["Cálculo Diferencial", "Resistência dos Materiais", "Termodinâmica", "Mecânica dos Fluidos", "Projeto Estrutural"],
    "administracao": ["Gestão Empresarial", "Marketing Digital", "Finanças Corporativas", "Comportamento Organizacional", "Empreendedorismo"],
    "psicologia": ["Psicologia Clínica", "Psicanálise", "Neuropsicologia", "Psicologia Social", "Terapia Cognitiva"],
    "computacao": ["Algoritmos Avançados", "Banco de Dados", "Inteligência Artificial", "Engenharia de Software", "Redes de Computadores"],
    "matematica": ["Cálculo Avançado", "Álgebra Linear", "Estatística", "Análise Real", "Geometria Diferencial"],
    "historia": ["História do Brasil", "História Medieval", "História Contemporânea", "Historiografia", "Movimentos Sociais"],
    "biologia": ["Genética Molecular", "Ecologia", "Biologia Celular", "Evolução", "Microbiologia"],
    "economia": ["Microeconomia", "Macroeconomia", "Econometria", "Economia Brasileira", "Economia Internacional"],
    "jornalismo": ["Redação Jornalística", "Jornalismo Investigativo", "Mídia Digital", "Ética Jornalística", "Teoria da Comunicação"],
    "arquitetura": ["Projeto Arquitetônico", "Urbanismo", "História da Arte", "Design Sustentável", "Construção Civil"],
}


def dar_aula(professor_id: int, curso_id: int) -> dict:
    """Professor dá uma aula pra um curso."""
    professor = db.obter_personagem_por_id(professor_id)
    if not professor:
        return {"sucesso": False, "msg": "Professor não encontrado."}
    
    if professor.get("profissao") != "professor":
        return {"sucesso": False, "msg": "Você não é professor."}
    
    especialidade = professor.get("especialidade_professor")
    if not especialidade:
        return {"sucesso": False, "msg": "Você não tem especialidade. Usa `?escolherespecialidade`."}
    
    curso = db.obter_curso(curso_id)
    if not curso:
        return {"sucesso": False, "msg": "Curso não encontrado."}
    
    # Verifica compatibilidade (simplificado: nome do curso contém nome da especialidade)
    nome_esp = especialidade.lower()
    nome_curso = curso["nome"].lower()
    # Aceita se o curso for da mesma área (simplificação)
    compativel = True  # Em produção, verificar melhor
    
    # Escolhe tema aleatório
    temas = TEMAS_POR_ESPECIALIDADE.get(especialidade, ["Tema Geral"])
    tema = random.choice(temas)
    
    # Calcula pagamento baseado em duração
    duracao = 60  # minutos
    pagamento_base = 200
    pagamento = pagamento_base + (professor.get("nivel", 1) * 20)
    
    # Registra aula
    aula_id = db.registrar_aula(professor_id, curso_id, tema, duracao, pagamento)
    
    # Conta alunos matriculados no curso que podem assistir
    matriculas = db.listar_matriculas_personagem(None)  # todos
    alunos_potenciais = 0
    for m in matriculas:
        if m.get("curso_id") == curso_id and m.get("status") == "matriculado":
            alunos_potenciais += 1
    
    # Simula presença (30-70% dos alunos)
    alunos_presentes = int(alunos_potenciais * random.uniform(0.3, 0.7))
    
    # Paga o professor
    db.atualizar_saldo_personagem(professor_id, pagamento)
    db.registrar_transacao(professor_id, "salario_aula", pagamento, f"Aula de {tema} - {curso['nome']}")
    
    # Ganha XP e reputação
    db.registrar_trabalho_personagem(professor_id, 0, 20)
    db.modificar_status_personagem(professor_id, "reputacao", 2)
    db.modificar_status_personagem(professor_id, "energia", -10)
    
    return {
        "sucesso": True,
        "aula_id": aula_id,
        "tema": tema,
        "curso": curso["nome"],
        "universidade": curso["universidade"],
        "pagamento": pagamento,
        "alunos_presentes": alunos_presentes,
        "msg": f"📚 Aula ministrada com sucesso!\n\n**Tema:** {tema}\n**Curso:** {curso['nome']} ({curso['universidade']})\n**Alunos presentes:** {alunos_presentes}\n**Pagamento:** ${pagamento}",
    }


def assistir_aula(aluno_id: int, aula_id: int) -> dict:
    """Aluno assiste uma aula."""
    aluno = db.obter_personagem_por_id(aluno_id)
    if not aluno:
        return {"sucesso": False, "msg": "Aluno não encontrado."}
    
    aula = db.obter_aula(aula_id)
    if not aula:
        return {"sucesso": False, "msg": "Aula não encontrada."}
    
    # Verifica se aluno tá matriculado no curso
    matricula = db.obter_matricula_ativa(aluno_id)
    if not matricula or matricula["curso_id"] != aula["curso_id"]:
        return {"sucesso": False, "msg": "Você não tá matriculado nesse curso."}
    
    # Verifica se já assistiu
    if db.ja_assistiu_aula(aluno_id, aula_id):
        return {"sucesso": False, "msg": "Você já assistiu essa aula."}
    
    # Calcula aproveitamento (baseado em energia e felicidade)
    energia = aluno.get("energia", 100)
    felicidade = aluno.get("felicidade", 100)
    aproveitamento = round((energia + felicidade) / 200 * 10, 1)
    aproveitamento = max(5.0, min(10.0, aproveitamento + random.uniform(-1, 1)))
    
    # Registra presença
    db.registrar_presenca(aula_id, aluno_id, aproveitamento)
    db.incrementar_alunos_aula(aula_id)
    
    # Ganha XP e bônus na nota
    xp_ganho = int(aproveitamento * 3)
    db.registrar_trabalho_personagem(aluno_id, 0, xp_ganho)
    
    # Consome energia
    db.modificar_status_personagem(aluno_id, "energia", -5)
    
    return {
        "sucesso": True,
        "aproveitamento": aproveitamento,
        "xp_ganho": xp_ganho,
        "tema": aula["tema"],
        "msg": f"📖 Aula assistida!\n\n**Tema:** {aula['tema']}\n**Aproveitamento:** {aproveitamento}/10\n**XP ganho:** +{xp_ganho}",
    }
