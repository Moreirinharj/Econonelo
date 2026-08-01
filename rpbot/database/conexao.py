import sqlite3
import time
from utils.logger import log_acao

DB_PATH = "rpbot.db"
SCHEMA_VERSION = 24


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_schema_version():
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        return row["version"] if row else 0
    except sqlite3.OperationalError:
        conn.close()
        return 0


def set_schema_version(version):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO schema_version (version, applied_at) VALUES (?, ?)", (version, time.time()))
    conn.commit()
    conn.close()


def aplicar_migracoes(conn, from_version):
    cur = conn.cursor()
    
    if from_version < 1:
        log_acao("MIGRACAO_V1", "FOREIGN KEY habilitado")
    
    if from_version < 2:
        log_acao("MIGRACAO_V2", "Criando índices")
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_personagens_user_id ON personagens(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_personagens_ativo ON personagens(user_id, ativo)",
            "CREATE INDEX IF NOT EXISTS idx_personagens_profissao ON personagens(profissao)",
            "CREATE INDEX IF NOT EXISTS idx_personagens_saldo ON personagens(saldo)",
            "CREATE INDEX IF NOT EXISTS idx_relacionamentos_personagem ON relacionamentos(personagem_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_relacionamentos_alvo ON relacionamentos(alvo_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_relacionamentos_tipo ON relacionamentos(tipo, status)",
            "CREATE INDEX IF NOT EXISTS idx_chamados_emergencia_status ON chamados_emergencia(status)",
            "CREATE INDEX IF NOT EXISTS idx_chamados_oab_status ON chamados_oab(status)",
            "CREATE INDEX IF NOT EXISTS idx_processos_oab_status ON processos_oab(status)",
            "CREATE INDEX IF NOT EXISTS idx_boletins_personagem ON boletins(personagem_id)",
        ]
        for idx in indices:
            try:
                cur.execute(idx)
            except:
                pass
        conn.commit()
    
    if from_version < 3:
        log_acao("MIGRACAO_V3", "Status do personagem")
        colunas = [
            ("saude", "INTEGER NOT NULL DEFAULT 100"),
            ("energia", "INTEGER NOT NULL DEFAULT 100"),
            ("fome", "INTEGER NOT NULL DEFAULT 100"),
            ("felicidade", "INTEGER NOT NULL DEFAULT 100"),
            ("estresse", "INTEGER NOT NULL DEFAULT 0"),
            ("higiene", "INTEGER NOT NULL DEFAULT 100"),
            ("reputacao", "INTEGER NOT NULL DEFAULT 50"),
            ("escolaridade", "TEXT NOT NULL DEFAULT 'medio'"),
            ("data_nascimento", "TEXT"),
            ("objetivos", "TEXT"),
            ("ficha_criminal", "TEXT NOT NULL DEFAULT 'limpa'"),
        ]
        for coluna, tipo in colunas:
            try:
                cur.execute(f"ALTER TABLE personagens ADD COLUMN {coluna} {tipo}")
            except:
                pass
        conn.commit()
    
    if from_version < 4:
        log_acao("MIGRACAO_V4", "Inventário")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personagem_id INTEGER NOT NULL,
                item_nome TEXT NOT NULL,
                item_tipo TEXT NOT NULL,
                quantidade INTEGER NOT NULL DEFAULT 1,
                peso REAL NOT NULL DEFAULT 1.0,
                equipado INTEGER NOT NULL DEFAULT 0,
                dados_extra TEXT,
                criado_em REAL NOT NULL,
                FOREIGN KEY (personagem_id) REFERENCES personagens(id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_inventario_personagem ON inventario(personagem_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_inventario_tipo ON inventario(item_tipo)")
        conn.commit()
    
    if from_version < 5:
        log_acao("MIGRACAO_V5", "Economia")
        colunas = [
            ("saldo_banco", "INTEGER NOT NULL DEFAULT 0"),
            ("limite_cartao", "INTEGER NOT NULL DEFAULT 1000"),
            ("fatura_cartao", "INTEGER NOT NULL DEFAULT 0"),
            ("chave_pix", "TEXT"),
        ]
        for coluna, tipo in colunas:
            try:
                cur.execute(f"ALTER TABLE personagens ADD COLUMN {coluna} {tipo}")
            except:
                pass
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personagem_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                valor INTEGER NOT NULL,
                descricao TEXT,
                destino_id INTEGER,
                criado_em REAL NOT NULL,
                FOREIGN KEY (personagem_id) REFERENCES personagens(id),
                FOREIGN KEY (destino_id) REFERENCES personagens(id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_personagem ON transacoes(personagem_id, criado_em)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_tipo ON transacoes(tipo)")
        conn.commit()
    
    if from_version < 6:
        log_acao("MIGRACAO_V6", "NPCs")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS npcs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                idade INTEGER NOT NULL,
                profissao TEXT NOT NULL,
                cidade TEXT NOT NULL,
                dinheiro INTEGER NOT NULL DEFAULT 1000,
                personalidade TEXT NOT NULL DEFAULT 'neutro',
                humor INTEGER NOT NULL DEFAULT 50,
                ativo INTEGER NOT NULL DEFAULT 1,
                criado_em REAL NOT NULL
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_npcs_cidade ON npcs(cidade)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_npcs_profissao ON npcs(profissao)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_npcs_ativo ON npcs(ativo)")
        conn.commit()
    
    if from_version < 7:
        log_acao("MIGRACAO_V7", "Eventos")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                efeitos TEXT,
                ativo INTEGER NOT NULL DEFAULT 1,
                criado_em REAL NOT NULL,
                expira_em REAL
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_eventos_ativo ON eventos(ativo)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos(tipo)")
        conn.commit()
    
    if from_version < 8:
        log_acao("MIGRACAO_V8", "Casas")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS casas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                cidade TEXT NOT NULL,
                bairro TEXT NOT NULL,
                preco INTEGER NOT NULL,
                proprietario_id INTEGER,
                cofre INTEGER NOT NULL DEFAULT 0,
                decoracao TEXT NOT NULL DEFAULT 'basica',
                garagem INTEGER NOT NULL DEFAULT 0,
                vendido INTEGER NOT NULL DEFAULT 0,
                criado_em REAL NOT NULL,
                FOREIGN KEY (proprietario_id) REFERENCES personagens(id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_casas_cidade ON casas(cidade)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_casas_proprietario ON casas(proprietario_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_casas_tipo ON casas(tipo)")
        conn.commit()
    
    if from_version < 9:
        log_acao("MIGRACAO_V9", "Veículos")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS veiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modelo TEXT NOT NULL,
                placa TEXT NOT NULL UNIQUE,
                proprietario_id INTEGER,
                combustivel INTEGER NOT NULL DEFAULT 100,
                saude INTEGER NOT NULL DEFAULT 100,
                seguro_ativo INTEGER NOT NULL DEFAULT 0,
                documentacao TEXT NOT NULL DEFAULT 'regular',
                valor INTEGER NOT NULL,
                vendido INTEGER NOT NULL DEFAULT 0,
                criado_em REAL NOT NULL,
                FOREIGN KEY (proprietario_id) REFERENCES personagens(id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_veiculos_placa ON veiculos(placa)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_veiculos_proprietario ON veiculos(proprietario_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_veiculos_vendido ON veiculos(vendido)")
        conn.commit()
    
    if from_version < 10:
        log_acao("MIGRACAO_V10", "Locais")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS locais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                cidade TEXT NOT NULL,
                bairro TEXT NOT NULL,
                descricao TEXT,
                horario_abertura TEXT NOT NULL DEFAULT '08:00',
                horario_fechamento TEXT NOT NULL DEFAULT '22:00',
                ativo INTEGER NOT NULL DEFAULT 1,
                criado_em REAL NOT NULL
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_locais_cidade ON locais(cidade)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_locais_tipo ON locais(tipo)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_locais_ativo ON locais(ativo)")
        conn.commit()
    
    if from_version < 11:
        log_acao("MIGRACAO_V11", "Justiça")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processos_judiciais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reu_id INTEGER NOT NULL,
                acusador_id INTEGER,
                advogado_id INTEGER,
                juiz_id INTEGER,
                crime TEXT NOT NULL,
                descricao TEXT,
                status TEXT NOT NULL DEFAULT 'aberto',
                pena_dias INTEGER DEFAULT 0,
                fianca_valor INTEGER DEFAULT 0,
                fianca_paga INTEGER NOT NULL DEFAULT 0,
                criado_em REAL NOT NULL,
                atualizado_em REAL NOT NULL,
                FOREIGN KEY (reu_id) REFERENCES personagens(id),
                FOREIGN KEY (acusador_id) REFERENCES personagens(id),
                FOREIGN KEY (advogado_id) REFERENCES personagens(id),
                FOREIGN KEY (juiz_id) REFERENCES personagens(id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_processos_reu ON processos_judiciais(reu_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_processos_status ON processos_judiciais(status)")
        conn.commit()
    
    if from_version < 12:
        log_acao("MIGRACAO_V12", "Educação")
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
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cursos_universidade ON cursos(universidade)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_matriculas_personagem ON matriculas(personagem_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_matriculas_status ON matriculas(status)")
        conn.commit()
    
    if from_version < 13:
        log_acao("MIGRACAO_V13", "IA do Mundo")
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
        cur.execute("CREATE INDEX IF NOT EXISTS idx_noticias_categoria ON noticias(categoria)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_noticias_criado ON noticias(criado_em)")
        cur.execute("SELECT COUNT(*) as c FROM estado_mundo")
        if cur.fetchone()["c"] == 0:
            agora = time.time()
            cur.execute("INSERT INTO estado_mundo (chave, valor, atualizado_em) VALUES ('clima', 'Ensolarado', ?)", (agora,))
            cur.execute("INSERT INTO estado_mundo (chave, valor, atualizado_em) VALUES ('inflacao', '2.5', ?)", (agora,))
            cur.execute("INSERT INTO estado_mundo (chave, valor, atualizado_em) VALUES ('dia', '1', ?)", (agora,))
        conn.commit()
    
    if from_version < 14:
        log_acao("MIGRACAO_V14", "Identidade")
        colunas = [
            ("genero", "TEXT NOT NULL DEFAULT 'nao_informado'"),
            ("sexualidade", "TEXT NOT NULL DEFAULT 'nao_informado'"),
            ("pronomes", "TEXT NOT NULL DEFAULT 'nao_informado'"),
        ]
        for coluna, tipo in colunas:
            try:
                cur.execute(f"ALTER TABLE personagens ADD COLUMN {coluna} {tipo}")
            except:
                pass
        conn.commit()
    
    if from_version < 15:
        log_acao("MIGRACAO_V15", "Corrupção")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS corrupcao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subornador_id INTEGER NOT NULL,
                subornado_id INTEGER NOT NULL,
                valor INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                aceito INTEGER NOT NULL DEFAULT 0,
                denunciado INTEGER NOT NULL DEFAULT 0,
                criado_em REAL NOT NULL,
                FOREIGN KEY (subornador_id) REFERENCES personagens(id),
                FOREIGN KEY (subornado_id) REFERENCES personagens(id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_corrupcao_subornador ON corrupcao(subornador_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_corrupcao_subornado ON corrupcao(subornado_id)")
        try:
            cur.execute("ALTER TABLE personagens ADD COLUMN reputacao_corrupta INTEGER NOT NULL DEFAULT 0")
        except:
            pass
        conn.commit()
    
    if from_version < 16:
        log_acao("MIGRACAO_V16", "Concursos professores")
        colunas = [
            ("especialidade_professor", "TEXT"),
            ("cargo_atual", "TEXT"),
            ("salario_cargo", "INTEGER NOT NULL DEFAULT 0"),
            ("concurso_aprovado", "TEXT"),
        ]
        for coluna, tipo in colunas:
            try:
                cur.execute(f"ALTER TABLE personagens ADD COLUMN {coluna} {tipo}")
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
                criado_em REAL NOT NULL,
                FOREIGN KEY (personagem_id) REFERENCES personagens(id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_participacoes_concurso ON participacoes_concurso(concurso_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_participacoes_personagem ON participacoes_concurso(personagem_id)")
        try:
            cur.execute("ALTER TABLE npcs ADD COLUMN especialidade TEXT")
        except:
            pass
        try:
            cur.execute("ALTER TABLE npcs ADD COLUMN concurso_aprovado TEXT")
        except:
            pass
        conn.commit()
    
    if from_version < 17:
        log_acao("MIGRACAO_V17", "Concursos genéricos + Aulas")
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
                criado_em REAL NOT NULL,
                FOREIGN KEY (professor_id) REFERENCES personagens(id),
                FOREIGN KEY (curso_id) REFERENCES cursos(id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_aulas_professor ON aulas(professor_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_aulas_curso ON aulas(curso_id)")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS presencas_aula (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aula_id INTEGER NOT NULL,
                aluno_id INTEGER NOT NULL,
                aproveitamento REAL NOT NULL DEFAULT 0.0,
                criado_em REAL NOT NULL,
                FOREIGN KEY (aula_id) REFERENCES aulas(id),
                FOREIGN KEY (aluno_id) REFERENCES personagens(id)
            )
        """)
        conn.commit()
    
    if from_version < 18:
        log_acao("MIGRACAO_V18", "Empresas")
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
                estoque INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
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
                criado_em REAL NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES personagens(id),
                FOREIGN KEY (motoboy_id) REFERENCES personagens(id)
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
    
    if from_version < 19:
        log_acao("MIGRACAO_V19", "Imersão: Estado Atual e Viagens")
        try:
            cur.execute("ALTER TABLE personagens ADD COLUMN estado_atual TEXT")
        except:
            pass
        cur.execute("UPDATE personagens SET estado_atual = estado WHERE estado_atual IS NULL")
        conn.commit()



    if from_version < 24:
        log_acao("MIGRACAO_V24", "Escolaridade inicial = ensino médio")
        cur.execute("UPDATE personagens SET escolaridade = 'medio' WHERE escolaridade = 'nenhuma'")
        conn.commit()

def iniciar_banco():
    conn = conectar()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at REAL NOT NULL
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS personagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            nome TEXT NOT NULL,
            idade INTEGER NOT NULL,
            cor_pele TEXT NOT NULL,
            tipo_cabelo TEXT NOT NULL,
            cor_cabelo TEXT NOT NULL,
            estado TEXT NOT NULL,
            estado_atual TEXT,
            religiao TEXT NOT NULL,
            saldo INTEGER NOT NULL DEFAULT 0,
            saldo_banco INTEGER NOT NULL DEFAULT 0,
            limite_cartao INTEGER NOT NULL DEFAULT 1000,
            fatura_cartao INTEGER NOT NULL DEFAULT 0,
            chave_pix TEXT,
            profissao TEXT,
            nivel INTEGER NOT NULL DEFAULT 1,
            xp INTEGER NOT NULL DEFAULT 0,
            ultimo_trabalho REAL NOT NULL DEFAULT 0,
            ativo INTEGER NOT NULL DEFAULT 0,
            preso INTEGER NOT NULL DEFAULT 0,
            saude INTEGER NOT NULL DEFAULT 100,
            energia INTEGER NOT NULL DEFAULT 100,
            fome INTEGER NOT NULL DEFAULT 100,
            felicidade INTEGER NOT NULL DEFAULT 100,
            estresse INTEGER NOT NULL DEFAULT 0,
            higiene INTEGER NOT NULL DEFAULT 100,
            reputacao INTEGER NOT NULL DEFAULT 50,
            escolaridade TEXT NOT NULL DEFAULT 'medio',
            data_nascimento TEXT,
            objetivos TEXT,
            ficha_criminal TEXT NOT NULL DEFAULT 'limpa',
            genero TEXT NOT NULL DEFAULT 'nao_informado',
            sexualidade TEXT NOT NULL DEFAULT 'nao_informado',
            pronomes TEXT NOT NULL DEFAULT 'nao_informado',
            reputacao_corrupta INTEGER NOT NULL DEFAULT 0,
            especialidade_professor TEXT,
            cargo_atual TEXT,
            salario_cargo INTEGER NOT NULL DEFAULT 0,
            concurso_aprovado TEXT,
            concurso_profissao TEXT,
            nota_concurso REAL,
            amante_id INTEGER,
            traindo INTEGER NOT NULL DEFAULT 0,
            criado_em REAL NOT NULL
        )
    """)
    
    cur.execute("CREATE TABLE IF NOT EXISTS relacionamentos (id INTEGER PRIMARY KEY AUTOINCREMENT, personagem_id INTEGER NOT NULL, alvo_id INTEGER NOT NULL, tipo TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pendente', criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS chamados_oab (id INTEGER PRIMARY KEY AUTOINCREMENT, personagem_id INTEGER NOT NULL, descricao TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'aberto', advogado_id INTEGER, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS boletins (id INTEGER PRIMARY KEY AUTOINCREMENT, personagem_id INTEGER NOT NULL, descricao_original TEXT NOT NULL, texto_formal TEXT NOT NULL, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS processos_oab (id INTEGER PRIMARY KEY AUTOINCREMENT, personagem_id INTEGER NOT NULL, alvo_id INTEGER NOT NULL, tipo_remocao TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'aberto', criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS chamados_emergencia (id INTEGER PRIMARY KEY AUTOINCREMENT, personagem_id INTEGER NOT NULL, tipo TEXT NOT NULL, descricao TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'aberto', atendente_id INTEGER, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS inventario (id INTEGER PRIMARY KEY AUTOINCREMENT, personagem_id INTEGER NOT NULL, item_nome TEXT NOT NULL, item_tipo TEXT NOT NULL, quantidade INTEGER NOT NULL DEFAULT 1, peso REAL NOT NULL DEFAULT 1.0, equipado INTEGER NOT NULL DEFAULT 0, dados_extra TEXT, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS transacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, personagem_id INTEGER NOT NULL, tipo TEXT NOT NULL, valor INTEGER NOT NULL, descricao TEXT, destino_id INTEGER, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS npcs (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, idade INTEGER NOT NULL, profissao TEXT NOT NULL, cidade TEXT NOT NULL, dinheiro INTEGER NOT NULL DEFAULT 1000, personalidade TEXT NOT NULL DEFAULT 'neutro', humor INTEGER NOT NULL DEFAULT 50, especialidade TEXT, concurso_aprovado TEXT, ativo INTEGER NOT NULL DEFAULT 1, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT NOT NULL, titulo TEXT NOT NULL, descricao TEXT NOT NULL, efeitos TEXT, ativo INTEGER NOT NULL DEFAULT 1, criado_em REAL NOT NULL, expira_em REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS casas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, tipo TEXT NOT NULL, cidade TEXT NOT NULL, bairro TEXT NOT NULL, preco INTEGER NOT NULL, proprietario_id INTEGER, cofre INTEGER NOT NULL DEFAULT 0, decoracao TEXT NOT NULL DEFAULT 'basica', garagem INTEGER NOT NULL DEFAULT 0, vendido INTEGER NOT NULL DEFAULT 0, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS veiculos (id INTEGER PRIMARY KEY AUTOINCREMENT, modelo TEXT NOT NULL, placa TEXT NOT NULL UNIQUE, proprietario_id INTEGER, combustivel INTEGER NOT NULL DEFAULT 100, saude INTEGER NOT NULL DEFAULT 100, seguro_ativo INTEGER NOT NULL DEFAULT 0, documentacao TEXT NOT NULL DEFAULT 'regular', valor INTEGER NOT NULL, vendido INTEGER NOT NULL DEFAULT 0, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS locais (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, tipo TEXT NOT NULL, cidade TEXT NOT NULL, bairro TEXT NOT NULL, descricao TEXT, horario_abertura TEXT NOT NULL DEFAULT '08:00', horario_fechamento TEXT NOT NULL DEFAULT '22:00', ativo INTEGER NOT NULL DEFAULT 1, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS processos_judiciais (id INTEGER PRIMARY KEY AUTOINCREMENT, reu_id INTEGER NOT NULL, acusador_id INTEGER, advogado_id INTEGER, juiz_id INTEGER, crime TEXT NOT NULL, descricao TEXT, status TEXT NOT NULL DEFAULT 'aberto', pena_dias INTEGER DEFAULT 0, fianca_valor INTEGER DEFAULT 0, fianca_paga INTEGER NOT NULL DEFAULT 0, criado_em REAL NOT NULL, atualizado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS cursos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, universidade TEXT NOT NULL, tipo TEXT NOT NULL, nivel TEXT NOT NULL, duracao_semestres INTEGER NOT NULL, mensalidade INTEGER NOT NULL DEFAULT 500, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS matriculas (id INTEGER PRIMARY KEY AUTOINCREMENT, personagem_id INTEGER NOT NULL, curso_id INTEGER NOT NULL, semestre_atual INTEGER NOT NULL DEFAULT 1, status TEXT NOT NULL DEFAULT 'matriculado', nota_media REAL NOT NULL DEFAULT 0.0, matriculado_em REAL NOT NULL, formado_em REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS estado_mundo (chave TEXT PRIMARY KEY, valor TEXT NOT NULL, atualizado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS noticias (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, corpo TEXT NOT NULL, categoria TEXT NOT NULL, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS corrupcao (id INTEGER PRIMARY KEY AUTOINCREMENT, subornador_id INTEGER NOT NULL, subornado_id INTEGER NOT NULL, valor INTEGER NOT NULL, tipo TEXT NOT NULL, aceito INTEGER NOT NULL DEFAULT 0, denunciado INTEGER NOT NULL DEFAULT 0, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS concursos (id TEXT PRIMARY KEY, universidade TEXT NOT NULL, especialidade TEXT NOT NULL, vagas INTEGER NOT NULL, salario INTEGER NOT NULL, materias TEXT NOT NULL, nivel TEXT NOT NULL DEFAULT 'superior', inscricao_aberta INTEGER NOT NULL DEFAULT 1, criado_em REAL NOT NULL, encerra_em REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS participacoes_concurso (id INTEGER PRIMARY KEY AUTOINCREMENT, concurso_id TEXT NOT NULL, personagem_id INTEGER NOT NULL, nota REAL NOT NULL DEFAULT 0.0, aprovado INTEGER NOT NULL DEFAULT 0, posicao INTEGER, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS aulas (id INTEGER PRIMARY KEY AUTOINCREMENT, professor_id INTEGER NOT NULL, curso_id INTEGER NOT NULL, tema TEXT NOT NULL, duracao_min INTEGER NOT NULL DEFAULT 60, pagamento INTEGER NOT NULL DEFAULT 200, alunos_presentes INTEGER NOT NULL DEFAULT 0, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS presencas_aula (id INTEGER PRIMARY KEY AUTOINCREMENT, aula_id INTEGER NOT NULL, aluno_id INTEGER NOT NULL, aproveitamento REAL NOT NULL DEFAULT 0.0, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS empresas (id TEXT PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL, descricao TEXT, cidade TEXT NOT NULL, bairro TEXT, saldo INTEGER NOT NULL DEFAULT 10000, ativo INTEGER NOT NULL DEFAULT 1, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS produtos_empresa (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id TEXT NOT NULL, nome TEXT NOT NULL, categoria TEXT NOT NULL, preco INTEGER NOT NULL, estoque INTEGER NOT NULL DEFAULT 0)")
    cur.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL, empresa_id TEXT NOT NULL, motoboy_id INTEGER, itens TEXT NOT NULL, valor_total INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pendente', endereco_entrega TEXT, criado_em REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS vagas_emprego (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id TEXT, profissao TEXT NOT NULL, escolaridade_req TEXT NOT NULL DEFAULT 'medio', salario INTEGER NOT NULL, vagas INTEGER NOT NULL DEFAULT 1, descricao TEXT, ativa INTEGER NOT NULL DEFAULT 1, criado_em REAL NOT NULL)")
    
    conn.commit()
    
    current_version = get_schema_version()
    if current_version < SCHEMA_VERSION:
        aplicar_migracoes(conn, current_version)
        set_schema_version(SCHEMA_VERSION)
    
    conn.close()
    log_acao("BANCO_INICIADO", f"schema_version={SCHEMA_VERSION}")
