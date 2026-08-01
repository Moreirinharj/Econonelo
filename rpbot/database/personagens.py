import time
from utils.logger import log_acao
from utils.cache import cache
from database.conexao import conectar


def _invalidar_cache_personagem(personagem_id: int):
    """Invalida cache do personagem E do usuário dono."""
    cache.invalidate(f"personagem:{personagem_id}")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM personagens WHERE id = ?", (personagem_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        cache.invalidate_pattern(f"user:{row['user_id']}")


def contar_personagens(user_id: str) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM personagens WHERE user_id = ?", (user_id,))
    total = cur.fetchone()["c"]
    conn.close()
    return total


def criar_personagem(user_id: str, dados: dict) -> int:
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET ativo = 0 WHERE user_id = ?", (user_id,))
    cur.execute("""

    # Garantir que a coluna CPF existe
    try:
        cur.execute("ALTER TABLE personagens ADD COLUMN cpf TEXT")
        conn.commit()
    except Exception:
        pass  # Coluna já existe
    
    # Gerar CPF sequencial (001-999)
    cur.execute("SELECT cpf FROM personagens WHERE cpf IS NOT NULL AND cpf != ''")
    cpfs_em_uso = set(row['cpf'] for row in cur.fetchall())
    
    cpf_gerado = None
    for num in range(1, 1000):
        cpf_candidato = f"{num:03d}"
        if cpf_candidato not in cpfs_em_uso:
            cpf_gerado = cpf_candidato
            break
    
    if cpf_gerado is None:
        raise Exception("Todos os 999 CPFs estão em uso!")
    
        INSERT INTO personagens
        (user_id, nome, idade, cor_pele, tipo_cabelo, cor_cabelo, estado, religiao,
         saldo, ativo, data_nascimento, objetivos, genero, sexualidade, pronomes, cpf, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, dados["nome"], dados["idade"], dados["cor_pele"], dados["tipo_cabelo"],
        dados["cor_cabelo"], dados["estado"], dados["religiao"], dados.get("saldo", 500),
        dados.get("data_nascimento"), dados.get("objetivos"),
        dados.get("genero", "nao_informado"),
        dados.get("sexualidade", "nao_informado"),
        dados.get("pronomes", "nao_informado"),
        cpf_gerado,
        time.time(),
    ))
    conn.commit()
    novo_id = cur.lastrowid
    conn.close()
    cache.invalidate_pattern(f"user:{user_id}")
    log_acao("PERSONAGEM_CRIADO", f"user_id={user_id} id={novo_id} nome={dados['nome']}")
    return novo_id


def listar_personagens(user_id: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE user_id = ? ORDER BY id", (user_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows




def obter_personagem_ativo(user_id: str) -> dict:
    """Obtém o personagem ativo do usuário."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE user_id = ? AND ativo = 1", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def obter_personagem_por_id(personagem_id: int) -> dict:
    """Obtém personagem pelo ID."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE id = ?", (personagem_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def definir_personagem_ativo(user_id: str, personagem_id: int) -> bool:
    """Define qual personagem está ativo."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET ativo = 0 WHERE user_id = ?", (user_id,))
    cur.execute("UPDATE personagens SET ativo = 1 WHERE id = ? AND user_id = ?", (personagem_id, user_id))
    conn.commit()
    conn.close()
    return True


def atualizar_saldo_personagem(personagem_id: int, delta: float) -> bool:
    """Atualiza saldo (adiciona ou remove)."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET saldo = saldo + ? WHERE id = ?", (delta, personagem_id))
    conn.commit()
    conn.close()
    return True


def definir_profissao_personagem(personagem_id: int, profissao: str) -> bool:
    """Define a profissão do personagem."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET profissao = ? WHERE id = ?", (profissao, personagem_id))
    conn.commit()
    conn.close()
    return True


def registrar_trabalho_personagem(personagem_id: int, valor: float) -> bool:
    """Registra que personagem trabalhou e recebe pagamento."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET saldo = saldo + ? WHERE id = ?", (valor, personagem_id))
    conn.commit()
    conn.close()
    return True


def listar_top_saldos(limite: int = 10) -> list:
    """Lista personagens com maior saldo."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens ORDER BY saldo DESC LIMIT ?", (limite,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def listar_todos_personagens() -> list:
    """Lista todos os personagens."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def prender_personagem(personagem_id: int) -> bool:
    """Prende um personagem."""
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE personagens ADD COLUMN preso INTEGER DEFAULT 0")
        conn.commit()
    except:
        pass
    cur.execute("UPDATE personagens SET preso = 1 WHERE id = ?", (personagem_id,))
    conn.commit()
    conn.close()
    return True


def soltar_personagem(personagem_id: int) -> bool:
    """Solta um personagem preso."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET preso = 0 WHERE id = ?", (personagem_id,))
    conn.commit()
    conn.close()
    return True


def listar_profissionais(profissao: str) -> list:
    """Lista personagens com uma profissão específica."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE profissao = ? AND ativo = 1", (profissao,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def listar_advogados_disponiveis() -> list:
    """Lista advogados disponíveis."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE profissao IN ('advogado', 'advogado_criminal') AND ativo = 1")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def atualizar_status_personagem(personagem_id: int, status: str) -> bool:
    """Atualiza status do personagem."""
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE personagens ADD COLUMN status TEXT DEFAULT 'normal'")
        conn.commit()
    except:
        pass
    cur.execute("UPDATE personagens SET status = ? WHERE id = ?", (status, personagem_id))
    conn.commit()
    conn.close()
    return True


def modificar_status_personagem(personagem_id: int, status: str) -> bool:
    """Modifica status do personagem (alias)."""
    return atualizar_status_personagem(personagem_id, status)


def atualizar_escolaridade(personagem_id: int, escolaridade: str) -> bool:
    """Atualiza escolaridade do personagem."""
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE personagens ADD COLUMN escolaridade TEXT DEFAULT 'nenhuma'")
        conn.commit()
    except:
        pass
    cur.execute("UPDATE personagens SET escolaridade = ? WHERE id = ?", (escolaridade, personagem_id))
    conn.commit()
    conn.close()
    return True


def atualizar_objetivos(personagem_id: int, objetivos: str) -> bool:
    """Atualiza objetivos do personagem."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET objetivos = ? WHERE id = ?", (objetivos, personagem_id))
    conn.commit()
    conn.close()
    return True


def adicionar_registro_criminal(personagem_id: int, crime: str) -> bool:
    """Adiciona registro criminal ao personagem."""
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE personagens ADD COLUMN ficha_criminal TEXT DEFAULT ''")
        conn.commit()
    except:
        pass
    cur.execute("SELECT ficha_criminal FROM personagens WHERE id = ?", (personagem_id,))
    row = cur.fetchone()
    ficha_atual = row['ficha_criminal'] if row and row['ficha_criminal'] else ''
    nova_ficha = f"{ficha_atual}|{crime}" if ficha_atual else crime
    cur.execute("UPDATE personagens SET ficha_criminal = ? WHERE id = ?", (nova_ficha, personagem_id))
    conn.commit()
    conn.close()
    return True


def limpar_ficha_criminal(personagem_id: int) -> bool:
    """Limpa a ficha criminal do personagem."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET ficha_criminal = '' WHERE id = ?", (personagem_id,))
    conn.commit()
    conn.close()
    return True


def atualizar_identidade(personagem_id: int, campo: str, valor: str) -> bool:
    """Atualiza campo de identidade do personagem."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(personagens)")
    colunas = [r['name'] for r in cur.fetchall()]
    if campo not in colunas:
        cur.execute(f"ALTER TABLE personagens ADD COLUMN {campo} TEXT")
        conn.commit()
    cur.execute(f"UPDATE personagens SET {campo} = ? WHERE id = ?", (valor, personagem_id))
    conn.commit()
    conn.close()
    return True


def editar_personagem_pessoal(personagem_id: int, campo: str, valor) -> bool:
    """Edita campo pessoal do personagem."""
    return atualizar_identidade(personagem_id, campo, str(valor))


def pegar_personagem_ativo(user_id: str) -> dict:
    """Pega personagem ativo (alias)."""
    return obter_personagem_ativo(user_id)


def pegar_personagem_por_id(personagem_id: int) -> dict:
    """Pega personagem por ID (alias)."""
    return obter_personagem_por_id(personagem_id)


def top_saldos(limite: int = 10) -> list:
    """Top saldos (alias)."""
    return listar_top_saldos(limite)


def todos_personagens() -> list:
    """Todos personagens (alias)."""
    return listar_todos_personagens()


def listar_cpfs_em_uso() -> set:
    """Lista todos os CPFs em uso (personagens vivos)."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT cpf FROM personagens WHERE cpf IS NOT NULL AND cpf != '' AND vida > 0")
    cpfs = set(row['cpf'] for row in cur.fetchall())
    conn.close()
    return cpfs


def obter_personagem_por_cpf(cpf: str) -> dict:
    """Obtém um personagem pelo CPF."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE cpf = ? AND vida > 0", (cpf,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def atualizar_vida_personagem(personagem_id: int, vida: int) -> bool:
    """Atualiza a vida de um personagem."""
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE personagens ADD COLUMN vida INTEGER DEFAULT 100")
        conn.commit()
    except:
        pass
    cur.execute("UPDATE personagens SET vida = ? WHERE id = ?", (vida, personagem_id))
    conn.commit()
    conn.close()
    return True


def liberar_cpf_na_morte(personagem_id: int) -> bool:
    """Libera o CPF quando o personagem morre (vida = 0)."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE personagens SET vida = 0 WHERE id = ?", (personagem_id,))
    conn.commit()
    conn.close()
    return True


def obter_personagem_por_discord_id(discord_id: str) -> dict:
    """Obtém personagem pelo Discord ID."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personagens WHERE user_id = ? AND ativo = 1", (discord_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
