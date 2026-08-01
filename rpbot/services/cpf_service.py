"""Sistema de CPF sequencial (000-999) com investigação."""
import database as db
from utils.logger import log_acao
from services.heranca_service import processar_heranca


def gerar_cpf_sequencial() -> str:
    """Gera próximo CPF disponível (000-999)."""
    conn = db.conectar()
    cur = conn.cursor()
    
    # Busca todos os CPFs em uso
    cur.execute("SELECT cpf FROM personagens WHERE cpf IS NOT NULL")
    cpfs_existentes = [row["cpf"] for row in cur.fetchall()]
    conn.close()
    
    # Encontra próximo disponível
    for i in range(1000):
        cpf = f"{i:03d}"
        if cpf not in cpfs_existentes:
            return cpf
    
    return None  # Todos os 1000 CPFs estão em uso


def atribuir_cpf_ao_personagem(personagem_id: int) -> str:
    """Atribui um CPF sequencial ao personagem."""
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return None
    
    # Se já tem CPF, retorna
    if personagem.get("cpf"):
        return personagem["cpf"]
    
    novo_cpf = gerar_cpf_sequencial()
    if not novo_cpf:
        return None
    
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET cpf = ? WHERE id = ?", (novo_cpf, personagem_id))
    conn.commit()
    conn.close()
    
    log_acao("CPF_ATRIBUIDO", f"personagem={personagem_id} cpf={novo_cpf}")
    return novo_cpf


def obter_cpf_personagem(personagem_id: int) -> str:
    """Retorna o CPF do personagem (gera se não tiver)."""
    return atribuir_cpf_ao_personagem(personagem_id)


def buscar_personagem_por_cpf(cpf: str) -> dict:
    """Busca personagem pelo CPF."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE cpf = ?", (cpf,))
    row = cur.fetchone()
    conn.close()
    
    return dict(row) if row else None


def liberar_cpf(personagem_id: int):
    """Libera o CPF quando o personagem morre."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET cpf = NULL WHERE id = ?", (personagem_id,))
    conn.commit()
    conn.close()
    
    log_acao("CPF_LIBERADO", f"personagem={personagem_id}")


def matar_personagem(personagem_id: int, causa: str = "Desconhecida"):
    """Marca personagem como morto, libera o CPF e processa herança."""
    # Processa herança ANTES de liberar o CPF
    heranca_result = processar_heranca(personagem_id)
    
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE personagens SET vivo = 0, causa_morte = ?, cpf = NULL 
        WHERE id = ?
    """, (causa, personagem_id))
    conn.commit()
    conn.close()
    
    log_acao("PERSONAGEM_MORTO", f"personagem={personagem_id} causa={causa}")
    
    return heranca_result


def investigar_cpf(cpf: str, investigador_id: int) -> dict:
    """Autoridade/médico investiga um CPF."""
    personagem = buscar_personagem_por_cpf(cpf)
    
    if not personagem:
        return {"sucesso": False, "msg": "CPF não encontrado ou já foi liberado."}
    
    investigador = db.obter_personagem_por_id(investigador_id)
    if not investigador:
        return {"sucesso": False, "msg": "Investigador não encontrado."}
    
    # Verifica se é autoridade ou médico
    profissao = investigador.get("profissao", "")
    pode_investigar = profissao in [
        "policial_militar", "policial_civil", "juiz", "medico", "samu"
    ]
    
    if not pode_investigar:
        return {
            "sucesso": False, 
            "msg": "Apenas autoridades (PM, PC, Juiz) e médicos podem investigar CPFs."
        }
    
    # Retorna informações do personagem
    return {
        "sucesso": True,
        "personagem": personagem,
        "investigador": investigador,
        "msg": f"🔍 **Investigação do CPF {cpf}**\n\n"
               f"**Nome:** {personagem['nome']}\n"
               f"**Idade:** {personagem['idade']}\n"
               f"**Profissão:** {personagem.get('profissao', 'Desempregado')}\n"
               f"**Status:** {'🟢 Vivo' if personagem.get('vivo', 1) else '💀 Morto'}\n"
               f"**Ficha Criminal:** {personagem.get('ficha_criminal', 'Limpa')}\n"
               f"**Reputação:** {personagem.get('reputacao', 50)}/100\n"
               f"**Reputação Corrupta:** {personagem.get('reputacao_corrupta', 0)}/100"
    }
