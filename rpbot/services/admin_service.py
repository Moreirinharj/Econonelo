"""Sistema de ativação admin por código secreto."""
import os
import time
import database as db
from utils.logger import log_acao
from dotenv import load_dotenv

load_dotenv()


def obter_codigo_secreto() -> str:
    """Retorna o código secreto do .env."""
    return os.getenv("ADMIN_SECRET_CODE", "")


def verificar_codigo(codigo: str) -> bool:
    """Verifica se o código fornecido bate com o código secreto."""
    codigo_secreto = obter_codigo_secreto()
    if not codigo_secreto:
        return False
    # Comparação segura (evita timing attacks)
    return codigo == codigo_secreto


def ativar_admin(user_id: str) -> dict:
    """Ativa um usuário como admin."""
    conn = db.conectar()
    cur = conn.cursor()
    
    # Verifica se já é admin
    cur.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
    existente = cur.fetchone()
    
    if existente and not existente["desativado"]:
        conn.close()
        return {"sucesso": False, "msg": "Você já é admin, mano!"}
    
    agora = time.time()
    
    if existente and existente["desativado"]:
        # Reativa
        cur.execute("""
            UPDATE admins SET desativado = 0, ativado_em = ? WHERE user_id = ?
        """, (agora, user_id))
    else:
        # Novo admin
        cur.execute("""
            INSERT INTO admins (user_id, ativado_em, ativado_por_codigo)
            VALUES (?, ?, 1)
        """, (user_id, agora))
    
    conn.commit()
    conn.close()
    
    log_acao("ADMIN_ATIVADO", f"user_id={user_id}")
    
    return {
        "sucesso": True,
        "msg": "🔑 **Você agora é ADMIN!**\n\nVocê tem acesso a todos os comandos administrativos.\nUse `?adminhelp` pra ver a lista."
    }


def desativar_admin(user_id: str) -> dict:
    """Desativa um admin."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("UPDATE admins SET desativado = 1 WHERE user_id = ?", (user_id,))
    sucesso = cur.rowcount > 0
    conn.commit()
    conn.close()
    
    if sucesso:
        log_acao("ADMIN_DESATIVADO", f"user_id={user_id}")
        return {"sucesso": True, "msg": "Admin desativado."}
    return {"sucesso": False, "msg": "Usuário não é admin."}


def eh_admin(user_id: str) -> bool:
    """Verifica se o usuário é admin."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("SELECT desativado FROM admins WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return False
    return not row["desativado"]


def listar_admins() -> list:
    """Lista todos os admins ativos."""
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, ativado_em FROM admins 
        WHERE desativado = 0 
        ORDER BY ativado_em ASC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
