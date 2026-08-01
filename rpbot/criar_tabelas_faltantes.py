import sqlite3
from database.conexao import conectar

def criar_todas_tabelas():
    conn = conectar()
    cur = conn.cursor()
    
    # Verificar quais tabelas existem
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existentes = {row[0] for row in cur.fetchall()}
    print(f"Tabelas existentes: {sorted(existentes)}")
    
    # Criar TODAS as tabelas que podem estar faltando
    tabelas = {
        "cursos": """
            CREATE TABLE IF NOT EXISTS cursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                universidade TEXT NOT NULL,
                tipo TEXT NOT NULL,
                nivel TEXT NOT NULL,
                duracao_semestres INTEGER NOT NULL,
                mensalidade INTEGER NOT NULL DEFAULT 500,
                criado_em REAL NOT NULL
            )
        """,
        "matriculas": """
            CREATE TABLE IF NOT EXISTS matriculas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personagem_id INTEGER NOT NULL,
                curso_id INTEGER NOT NULL,
                semestre_atual INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'matriculado',
                nota_media REAL NOT NULL DEFAULT 0.0,
                matriculado_em REAL NOT NULL,
                formado_em REAL
            )
        """,
        "estado_mundo": """
            CREATE TABLE IF NOT EXISTS estado_mundo (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL,
                atualizado_em REAL NOT NULL
            )
        """,
        "noticias": """
            CREATE TABLE IF NOT EXISTS noticias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                corpo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                criado_em REAL NOT NULL
            )
        """,
        "concursos": """
            CREATE TABLE IF NOT EXISTS concursos (
                id TEXT PRIMARY KEY,
                universidade TEXT NOT NULL,
                especialidade TEXT NOT NULL,
                vagas INTEGER NOT NULL,
                salario INTEGER NOT NULL,
                materias TEXT NOT NULL,
                nivel TEXT NOT NULL DEFAULT 'superior',
                inscricao_aberta INTEGER NOT NULL DEFAULT 1,
                criado_em REAL NOT NULL,
                encerra_em REAL
            )
        """,
        "participacoes_concurso": """
            CREATE TABLE IF NOT EXISTS participacoes_concurso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concurso_id TEXT NOT NULL,
                personagem_id INTEGER NOT NULL,
                nota REAL NOT NULL DEFAULT 0.0,
                aprovado INTEGER NOT NULL DEFAULT 0,
                posicao INTEGER,
                criado_em REAL NOT NULL
            )
        """,
        "aulas": """
            CREATE TABLE IF NOT EXISTS aulas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER NOT NULL,
                curso_id INTEGER NOT NULL,
                tema TEXT NOT NULL,
                duracao_min INTEGER NOT NULL DEFAULT 60,
                pagamento INTEGER NOT NULL DEFAULT 200,
                alunos_presentes INTEGER NOT NULL DEFAULT 0,
                criado_em REAL NOT NULL
            )
        """,
        "presencas_aula": """
            CREATE TABLE IF NOT EXISTS presencas_aula (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aula_id INTEGER NOT NULL,
                aluno_id INTEGER NOT NULL,
                aproveitamento REAL NOT NULL DEFAULT 0.0,
                criado_em REAL NOT NULL
            )
        """,
        "empresas": """
            CREATE TABLE IF NOT EXISTS empresas (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                descricao TEXT,
                cidade TEXT NOT NULL,
                bairro TEXT,
                saldo INTEGER NOT NULL DEFAULT 10000,
                ativo INTEGER NOT NULL DEFAULT 1,
                criado_em REAL NOT NULL
            )
        """,
        "produtos_empresa": """
            CREATE TABLE IF NOT EXISTS produtos_empresa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id TEXT NOT NULL,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                preco INTEGER NOT NULL,
                estoque INTEGER NOT NULL DEFAULT 0
            )
        """,
        "pedidos": """
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                empresa_id TEXT NOT NULL,
                motoboy_id INTEGER,
                itens TEXT NOT NULL,
                valor_total INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pendente',
                endereco_entrega TEXT,
                criado_em REAL NOT NULL
            )
        """,
        "vagas_emprego": """
            CREATE TABLE IF NOT EXISTS vagas_emprego (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id TEXT,
                profissao TEXT NOT NULL,
                escolaridade_req TEXT NOT NULL DEFAULT 'medio',
                salario INTEGER NOT NULL,
                vagas INTEGER NOT NULL DEFAULT 1,
                descricao TEXT,
                ativa INTEGER NOT NULL DEFAULT 1,
                criado_em REAL NOT NULL
            )
        """,
        "corrupcao": """
            CREATE TABLE IF NOT EXISTS corrupcao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subornador_id INTEGER NOT NULL,
                subornado_id INTEGER NOT NULL,
                valor INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                aceito INTEGER NOT NULL DEFAULT 0,
                denunciado INTEGER NOT NULL DEFAULT 0,
                criado_em REAL NOT NULL
            )
        """,
    }
    
    criadas = []
    for nome, sql in tabelas.items():
        if nome not in existentes:
            cur.execute(sql)
            criadas.append(nome)
    
    conn.commit()
    
    # Adicionar colunas faltantes em personagens
    colunas_personagens = [
        ("genero", "TEXT NOT NULL DEFAULT 'nao_informado'"),
        ("sexualidade", "TEXT NOT NULL DEFAULT 'nao_informado'"),
        ("pronomes", "TEXT NOT NULL DEFAULT 'nao_informado'"),
        ("reputacao_corrupta", "INTEGER NOT NULL DEFAULT 0"),
        ("especialidade_professor", "TEXT"),
        ("cargo_atual", "TEXT"),
        ("salario_cargo", "INTEGER NOT NULL DEFAULT 0"),
        ("concurso_aprovado", "TEXT"),
        ("concurso_profissao", "TEXT"),
        ("nota_concurso", "REAL"),
        ("amante_id", "INTEGER"),
        ("traindo", "INTEGER NOT NULL DEFAULT 0"),
    ]
    
    colunas_adicionadas = []
    for col, tipo in colunas_personagens:
        try:
            cur.execute(f"ALTER TABLE personagens ADD COLUMN {col} {tipo}")
            colunas_adicionadas.append(col)
        except:
            pass
    
    conn.commit()
    conn.close()
    
    if criadas:
        print(f"✅ Tabelas criadas: {', '.join(criadas)}")
    else:
        print("✅ Todas as tabelas já existiam")
    
    if colunas_adicionadas:
        print(f"✅ Colunas adicionadas em personagens: {', '.join(colunas_adicionadas)}")

if __name__ == "__main__":
    criar_todas_tabelas()
