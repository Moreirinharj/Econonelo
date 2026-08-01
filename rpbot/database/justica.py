import time
from utils.logger import log_acao
from database.conexao import conectar

def abrir_processo(reu_id: int, acusador_id: int, crime: str, descricao: str, fianca_valor: int = 0) -> int:
    conn = conectar()
    cur = conn.cursor()
    agora = time.time()
    cur.execute("""
        INSERT INTO processos_judiciais (reu_id, acusador_id, crime, descricao, fianca_valor, criado_em, atualizado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (reu_id, acusador_id, crime, descricao, fianca_valor, agora, agora))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    log_acao("PROCESSO_ABERTO", f"id={pid} reu={reu_id} crime={crime}")
    return pid

def obter_processo(processo_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM processos_judiciais WHERE id = ?", (processo_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def listar_processos(status: str = None, reu_id: int = None):
    conn = conectar()
    cur = conn.cursor()
    query = "SELECT * FROM processos_judiciais WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if reu_id:
        query += " AND reu_id = ?"
        params.append(reu_id)
    query += " ORDER BY criado_em DESC"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def assumir_defesa(processo_id: int, advogado_id: int) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE processos_judiciais SET advogado_id = ?, atualizado_em = ?
        WHERE id = ? AND status IN ('aberto', 'em_julgamento')
    """, (advogado_id, time.time(), processo_id))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    if sucesso:
        log_acao("DEFESA_ASSUMIDA", f"processo_id={processo_id} advogado={advogado_id}")
    return sucesso

def designar_juiz(processo_id: int, juiz_id: int) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE processos_judiciais SET juiz_id = ?, status = 'em_julgamento', atualizado_em = ?
        WHERE id = ? AND status IN ('aberto', 'em_julgamento')
    """, (juiz_id, time.time(), processo_id))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    return sucesso

def proferir_sentenca(processo_id: int, veredito: str, pena_dias: int = 0) -> bool:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE processos_judiciais SET status = ?, pena_dias = ?, atualizado_em = ?
        WHERE id = ?
    """, (veredito, pena_dias, time.time(), processo_id))
    conn.commit()
    conn.close()
    log_acao("SENTENCA_PROFERIDA", f"processo_id={processo_id} veredito={veredito} pena={pena_dias}")
    return True

def pagar_fianca(processo_id: int, pagador_id: int, valor: int) -> dict:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT fianca_valor, fianca_paga, reu_id, status FROM processos_judiciais WHERE id = ?", (processo_id,))
    p = cur.fetchone()
    if not p:
        conn.close()
        return {"sucesso": False, "msg": "Processo não encontrado."}
    if p["status"] not in ("aberto", "em_julgamento"):
        conn.close()
        return {"sucesso": False, "msg": "Processo já encerrado."}
    
    restante = p["fianca_valor"] - p["fianca_paga"]
    if valor > restante:
        valor = restante
    
    novo_pago = p["fianca_paga"] + valor
    novo_status = "fianca_paga" if novo_pago >= p["fianca_valor"] else p["status"]
    
    cur.execute("""
        UPDATE processos_judiciais SET fianca_paga = ?, status = ?, atualizado_em = ?
        WHERE id = ?
    """, (novo_pago, novo_status, time.time(), processo_id))
    conn.commit()
    conn.close()
    
    if novo_status == "fianca_paga":
        from database.personagens import soltar_personagem
        soltar_personagem(p["reu_id"])
        log_acao("FIANCA_PAGA_TOTAL", f"processo_id={processo_id} pagador={pagador_id}")
    
    return {"sucesso": True, "valor_pago": valor, "novo_status": novo_status}
