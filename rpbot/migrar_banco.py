import sqlite3
import time
from database.conexao import conectar, get_schema_version, set_schema_version

def aplicar_migracoes_pendentes():
    conn = conectar()
    cur = conn.cursor()
    
    versao_atual = get_schema_version()
    print(f"Versão atual do schema: {versao_atual}")
    
    # Migração v12: Educação
    if versao_atual < 12:
        print("Aplicando migração v12: Educação")
        cur.execute("""
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
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS matriculas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personagem_id INTEGER NOT NULL,
                curso_id INTEGER NOT NULL,
                semestre_atual INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'matriculado',
                nota_media REAL NOT NULL DEFAULT 0.0,
                matriculado_em REAL NOT NULL,
                formado_em REAL,
                FOREIGN KEY (personagem_id) REFERENCES personagens(id),
                FOREIGN KEY (curso_id) REFERENCES cursos(id)
            )
        """)
        conn.commit()
        versao_atual = 12
    
    # Migração v13: IA do Mundo
    if versao_atual < 13:
        print("Aplicando migração v13: IA do Mundo")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS estado_mundo (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL,
                atualizado_em REAL NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS noticias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                corpo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                criado_em REAL NOT NULL
            )
        """)
        conn.commit()
        versao_atual = 13
    
    # Migração v14: Identidade
    if versao_atual < 14:
        print("Aplicando migração v14: Identidade")
        for c, t in [("genero","TEXT NOT NULL DEFAULT 'nao_informado'"),
                     ("sexualidade","TEXT NOT NULL DEFAULT 'nao_informado'"),
                     ("pronomes","TEXT NOT NULL DEFAULT 'nao_informado'")]:
            try:
                cur.execute(f"ALTER TABLE personagens ADD COLUMN {c} {t}")
            except:
                pass
        conn.commit()
        versao_atual = 14
    
    # Migração v15: Corrupção
    if versao_atual < 15:
        print("Aplicando migração v15: Corrupção")
        cur.execute("""
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
        """)
        try:
            cur.execute("ALTER TABLE personagens ADD COLUMN reputacao_corrupta INTEGER NOT NULL DEFAULT 0")
        except:
            pass
        conn.commit()
        versao_atual = 15
    
    # Migração v16: Concursos professores
    if versao_atual < 16:
        print("Aplicando migração v16: Concursos professores")
        for c, t in [("especialidade_professor","TEXT"),
                     ("cargo_atual","TEXT"),
                     ("salario_cargo","INTEGER NOT NULL DEFAULT 0"),
                     ("concurso_aprovado","TEXT")]:
            try:
                cur.execute(f"ALTER TABLE personagens ADD COLUMN {c} {t}")
            except:
                pass
        cur.execute("""
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
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS participacoes_concurso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concurso_id TEXT NOT NULL,
                personagem_id INTEGER NOT NULL,
                nota REAL NOT NULL DEFAULT 0.0,
                aprovado INTEGER NOT NULL DEFAULT 0,
                posicao INTEGER,
                criado_em REAL NOT NULL
            )
        """)
        conn.commit()
        versao_atual = 16
    
    # Migração v17: Concursos genéricos + Aulas
    if versao_atual < 17:
        print("Aplicando migração v17: Concursos genéricos + Aulas")
        try:
            cur.execute("ALTER TABLE personagens ADD COLUMN concurso_profissao TEXT")
        except:
            pass
        try:
            cur.execute("ALTER TABLE personagens ADD COLUMN nota_concurso REAL")
        except:
            pass
        cur.execute("""
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
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS presencas_aula (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aula_id INTEGER NOT NULL,
                aluno_id INTEGER NOT NULL,
                aproveitamento REAL NOT NULL DEFAULT 0.0,
                criado_em REAL NOT NULL
            )
        """)
        conn.commit()
        versao_atual = 17
    
    # Migração v18: Empresas
    if versao_atual < 18:
        print("Aplicando migração v18: Empresas")
        cur.execute("""
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
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS produtos_empresa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id TEXT NOT NULL,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                preco INTEGER NOT NULL,
                estoque INTEGER NOT NULL DEFAULT 0
            )
        """)
        cur.execute("""
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
        """)
        cur.execute("""
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
        """)
        try:
            cur.execute("ALTER TABLE personagens ADD COLUMN amante_id INTEGER")
        except:
            pass
        try:
            cur.execute("ALTER TABLE personagens ADD COLUMN traindo INTEGER NOT NULL DEFAULT 0")
        except:
            pass
        conn.commit()
        versao_atual = 18
    
    # Atualizar versão final
    set_schema_version(18)
    conn.close()
    print(f"✅ Migrações concluídas! Versão final: 18")

if __name__ == "__main__":
    aplicar_migracoes_pendentes()
