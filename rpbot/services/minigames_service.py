"""Sistema de minigames por profissão."""
import random
import time
import database as db
from utils.logger import log_acao


def _recompensa_trabalho(personagem_id: int, profissao: str, multiplicador: float = 1.0) -> dict:
    """Calcula e aplica recompensa de trabalho."""
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    # Salário base por profissão
    salarios_base = {
        "motoboy": 50, "policial_militar": 80, "policial_civil": 100,
        "advogado": 120, "medico": 150, "samu": 100, "professor": 90,
        "vendedor": 60, "domestica": 45, "empresario": 200,
        "jogador_futebol": 150, "cozinheiro": 70, "garcom": 50,
        "programador": 130, "designer": 100, "jornalista": 90,
        "pedreiro": 65, "eletricista": 75, "encanador": 70,
        "mecanico": 80, "motorista": 60, "pintor": 55,
    }
    
    base = salarios_base.get(profissao, 50)
    recompensa = int(base * multiplicador * random.uniform(0.8, 1.2))
    
    # Aplica recompensa
    db.atualizar_saldo_personagem(personagem_id, recompensa)
    db.registrar_trabalho_personagem(personagem_id, recompensa, 10)
    
    return {
        "sucesso": True,
        "recompensa": recompensa,
        "msg": f"💰 Você ganhou ${recompensa}!"
    }


# ===== MINIGAMES ESPECÍFICOS =====

def minigame_patrulha(personagem_id: int) -> dict:
    """Minigame de patrulha policial."""
    return {
        "titulo": "🚔 Patrulha Policial",
        "descricao": "Você está em patrulha e vê uma situação suspeita. O que faz?",
        "perguntas": [
            {
                "pergunta": "Um suspeito foge ao ver a viatura. O que você faz?",
                "opcoes": ["Ignora e segue patrulha", "Persegue com sirene ligada", "Chama reforço e tenta abordar", "Atira pra parar"],
                "correta": 2,
                "xp": 15,
                "recompensa_min": 60,
                "recompensa_max": 120
            }
        ]
    }


def minigame_blitz(personagem_id: int) -> dict:
    """Minigame de blitz policial."""
    return {
        "titulo": "🚧 Blitz Policial",
        "descricao": "Você está numa blitz e um motorista parece nervoso. O que faz?",
        "perguntas": [
            {
                "pergunta": "O motorista se recusa a soprar o bafômetro. O que você faz?",
                "opcoes": ["Deixa ele ir embora", "Aplica multa por recusa e retém o veículo", "Chama a imprensa", "Ignora e manda ele sair"],
                "correta": 1,
                "xp": 15,
                "recompensa_min": 70,
                "recompensa_max": 130
            }
        ]
    }


def minigame_consulta(personagem_id: int) -> dict:
    """Minigame de consulta jurídica."""
    return {
        "titulo": "⚖️ Consulta Jurídica",
        "descricao": "Um cliente te procura com um problema. O que você recomenda?",
        "perguntas": [
            {
                "pergunta": "Cliente quer processar o vizinho por barulho. O que você faz?",
                "opcoes": ["Aconselha mediação primeiro", "Aconselha processo direto", "Recusa o caso", "Cobra caro e promete ganhar"],
                "correta": 0,
                "xp": 20,
                "recompensa_min": 100,
                "recompensa_max": 180
            }
        ]
    }


def minigame_emergencia_medica(personagem_id: int) -> dict:
    """Minigame de emergência médica."""
    return {
        "titulo": "🚑 Emergência Médica",
        "descricao": "Paciente chega com dor no peito. O que você faz primeiro?",
        "perguntas": [
            {
                "pergunta": "Paciente com dor no peito e falta de ar. Qual a primeira ação?",
                "opcoes": ["Receita remédio pra dor", "Faz ECG e avalia sinais vitais", "Manda pra casa", "Ignora os sintomas"],
                "correta": 1,
                "xp": 25,
                "recompensa_min": 120,
                "recompensa_max": 200
            }
        ]
    }


def minigame_aula(personagem_id: int) -> dict:
    """Minigame de aula do professor."""
    return {
        "titulo": "📚 Aula Universitária",
        "descricao": "Você está dando aula e um aluno faz uma pergunta difícil. O que faz?",
        "perguntas": [
            {
                "pergunta": "Aluno faz pergunta que você não sabe responder. O que faz?",
                "opcoes": ["Inventa uma resposta", "Admite que não sabe e pesquisa depois", "Manda o aluno pesquisar", "Ignora a pergunta"],
                "correta": 1,
                "xp": 20,
                "recompensa_min": 80,
                "recompensa_max": 140
            }
        ]
    }


def minigame_entrega(personagem_id: int) -> dict:
    """Minigame de entrega de motoboy."""
    return {
        "titulo": "🛵 Entrega Rápida",
        "descricao": "Você tem 3 entregas pra fazer em 1 hora. Como organiza?",
        "perguntas": [
            {
                "pergunta": "Trânsito parado na rota principal. O que faz?",
                "opcoes": ["Fica parado esperando", "Pega rota alternativa pelo app", "Volta pra loja", "Entrega fora do prazo"],
                "correta": 1,
                "xp": 15,
                "recompensa_min": 50,
                "recompensa_max": 100
            }
        ]
    }


def minigame_crime(personagem_id: int) -> dict:
    """Minigame de crime (roubo/furto)."""
    return {
        "titulo": "🔪 Tentativa de Roubo",
        "descricao": "Você está planejando um golpe. Qual abordagem usa?",
        "perguntas": [
            {
                "pergunta": "Você vê uma pessoa distraída com o celular. O que faz?",
                "opcoes": ["Rouba na marra", "Finge que esbarra e rouba o celular", "Ignora e segue", "Chama a polícia"],
                "correta": 1,
                "xp": 10,
                "recompensa_min": 80,
                "recompensa_max": 200,
                "risco": 0.3
            }
        ]
    }


def minigame_audiencia(personagem_id: int) -> dict:
    """Minigame de audiência judicial."""
    return {
        "titulo": "👨‍⚖️ Audiência Judicial",
        "descricao": "Você está numa audiência e o juiz te pergunta algo. O que responde?",
        "perguntas": [
            {
                "pergunta": "Juiz pergunta sobre um precedente que você não conhece. O que faz?",
                "opcoes": ["Inventa uma resposta", "Pede prazo pra pesquisar", "Muda de assunto", "Admite que não sabe"],
                "correta": 1,
                "xp": 25,
                "recompensa_min": 150,
                "recompensa_max": 250
            }
        ]
    }


def minigame_negocio(personagem_id: int) -> dict:
    """Minigame de negócio do empresário."""
    return {
        "titulo": "💼 Negociação de Contrato",
        "descricao": "Um cliente quer fechar um contrato. Como você negocia?",
        "perguntas": [
            {
                "pergunta": "Cliente quer desconto de 30%. O que você faz?",
                "opcoes": ["Aceita sem negociar", "Oferece 10% e benefícios adicionais", "Recusa o negócio", "Aumenta o preço"],
                "correta": 1,
                "xp": 20,
                "recompensa_min": 180,
                "recompensa_max": 300
            }
        ]
    }


def minigame_jogo_futebol(personagem_id: int) -> dict:
    """Minigame de jogo de futebol."""
    return {
        "titulo": "⚽ Partida de Futebol",
        "descricao": "Você está em campo e recebe a bola. O que faz?",
        "perguntas": [
            {
                "pergunta": "Você está na área e tem 2 marcadores. O que faz?",
                "opcoes": ["Chuta de qualquer jeito", "Passa pro companheiro desmarcado", "Dribla os dois", "Fica parado"],
                "correta": 1,
                "xp": 15,
                "recompensa_min": 120,
                "recompensa_max": 200
            }
        ]
    }


# ===== MINIGAMES NOVOS =====

def minigame_venda(personagem_id: int) -> dict:
    """Minigame de venda do vendedor."""
    return {
        "titulo": "🛍️ Venda ao Cliente",
        "descricao": "Um cliente entrou na loja! Convença ele a comprar.",
        "perguntas": [
            {
                "pergunta": "O cliente diz que o produto tá caro. O que você faz?",
                "opcoes": [
                    "Ignora e atende outro cliente",
                    "Oferece um desconto e mostra os benefícios",
                    "Diz que o preço é justo e ponto final",
                    "Finge que não ouviu"
                ],
                "correta": 1,
                "xp": 15,
                "recompensa_min": 30,
                "recompensa_max": 80
            },
            {
                "pergunta": "O cliente tá indeciso entre dois produtos. O que você faz?",
                "opcoes": [
                    "Empurra o mais caro sem explicar",
                    "Diz que tanto faz, os dois são iguais",
                    "Pergunta o que ele precisa e recomenda o ideal",
                    "Deixa o cliente sozinho pra pensar"
                ],
                "correta": 2,
                "xp": 15,
                "recompensa_min": 30,
                "recompensa_max": 80
            },
            {
                "pergunta": "O cliente reclama que o produto veio com defeito. O que você faz?",
                "opcoes": [
                    "Diz que a culpa é dele",
                    "Pede desculpas, troca o produto e oferece um brinde",
                    "Manda ele falar com o gerente e sai",
                    "Diz que não tem troca"
                ],
                "correta": 1,
                "xp": 20,
                "recompensa_min": 25,
                "recompensa_max": 70
            },
            {
                "pergunta": "A loja tá vazia e entra um cliente apressado. O que você faz?",
                "opcoes": [
                    "Atende devagar pra ele ficar mais tempo",
                    "Atende rápido, mostra o que ele quer e fecha a venda",
                    "Diz que a loja vai fechar",
                    "Finge que tá no estoque"
                ],
                "correta": 1,
                "xp": 15,
                "recompensa_min": 35,
                "recompensa_max": 90
            },
            {
                "pergunta": "O cliente quer parcelar em 12x sem juros mas a política é 6x. O que você faz?",
                "opcoes": [
                    "Libera 12x sem pedir autorização",
                    "Diz que não pode e perde a venda",
                    "Explica a política, oferece 6x e um desconto à vista",
                    "Finge que o sistema não funciona"
                ],
                "correta": 2,
                "xp": 20,
                "recompensa_min": 40,
                "recompensa_max": 100
            }
        ]
    }


def minigame_domestica(personagem_id: int) -> dict:
    """Minigame de faxina da doméstica."""
    return {
        "titulo": "🧹 Faxina Completa",
        "descricao": "A casa tá uma bagunça! Organize tudo no tempo certo.",
        "perguntas": [
            {
                "pergunta": "Você chegou na casa do cliente. Por onde começa?",
                "opcoes": [
                    "Começa pelo quarto porque é mais fácil",
                    "Começa pela cozinha e banheiro (áreas mais críticas)",
                    "Começa varrendo a sala rapidinho",
                    "Fica no celular esperando o cliente sair"
                ],
                "correta": 1,
                "xp": 15,
                "recompensa_min": 25,
                "recompensa_max": 60
            },
            {
                "pergunta": "O chão da cozinha tá com gordura grudada. O que você usa?",
                "opcoes": [
                    "Água pura e pano seco",
                    "Detergente com água quente e esfregão",
                    "Passa um pano rápido e finge que limpou",
                    "Joga areia pra absorver"
                ],
                "correta": 1,
                "xp": 15,
                "recompensa_min": 25,
                "recompensa_max": 60
            },
            {
                "pergunta": "O cliente pediu pra lavar as roupas delicadas. O que você faz?",
                "opcoes": [
                    "Joga tudo na máquina com água quente",
                    "Lava à mão com sabão neutro e água fria",
                    "Mistura com as roupas normais",
                    "Deixa de molho por 3 dias"
                ],
                "correta": 1,
                "xp": 20,
                "recompensa_min": 30,
                "recompensa_max": 70
            },
            {
                "pergunta": "Você encontrou um objeto de valor caído atrás do sofá. O que faz?",
                "opcoes": [
                    "Guarda no bolso, achado não é roubado",
                    "Coloca em cima da mesa e avisa o cliente",
                    "Deixa onde tá, não é problema seu",
                    "Joga no lixo sem olhar"
                ],
                "correta": 1,
                "xp": 25,
                "recompensa_min": 35,
                "recompensa_max": 80
            },
            {
                "pergunta": "O cliente reclamou que o banheiro não ficou limpo. O que você faz?",
                "opcoes": [
                    "Diz que limpou sim e ele que tá vendo errado",
                    "Pede desculpas, volta e limpa com capricho",
                    "Diz que vai cobrar extra pra refazer",
                    "Ignora e vai embora"
                ],
                "correta": 1,
                "xp": 20,
                "recompensa_min": 30,
                "recompensa_max": 75
            }
        ]
    }


# ===== MAPEAMENTO DE PROFISSÕES PARA MINIGAMES =====



def minigame_advogado_criminal(personagem_id: int) -> dict:
    """Minigame de defesa criminal."""
    return {
        "titulo": "⚖️ Defesa Criminal",
        "descricao": "Você está defendendo um cliente acusado de crime. Qual estratégia usa?",
        "perguntas": [
            {
                "pergunta": "O cliente confessou o crime pra você em particular. O que você faz no tribunal?",
                "opcoes": [
                    "Conta pro juiz que ele é culpado",
                    "Defende ele com base na falta de provas materiais",
                    "Diz pro cliente mentir no depoimento",
                    "Abandona o caso na hora"
                ],
                "correta": 1,
                "xp": 25,
                "recompensa_min": 150,
                "recompensa_max": 280
            },
            {
                "pergunta": "A testemunha de acusação contradiz o depoimento anterior. O que você faz?",
                "opcoes": [
                    "Ignora a contradição",
                    "Aponta a contradição e questiona a credibilidade da testemunha",
                    "Pede pra testemunha sair da sala",
                    "Muda de assunto rapidamente"
                ],
                "correta": 1,
                "xp": 20,
                "recompensa_min": 120,
                "recompensa_max": 220
            },
            {
                "pergunta": "O promotor apresenta uma prova que pode ser ilegal (obtida sem mandado). O que você faz?",
                "opcoes": [
                    "Aceita a prova e continua",
                    "Pede a nulidade da prova por ilicitude",
                    "Tenta corromper o juiz",
                    "Finge que não viu"
                ],
                "correta": 1,
                "xp": 30,
                "recompensa_min": 180,
                "recompensa_max": 320
            },
            {
                "pergunta": "O juiz pergunta se você tem alguma questão preliminar. O que você argui?",
                "opcoes": [
                    "Diz que não tem nada",
                    "Argui nulidade por cerceamento de defesa",
                    "Pede pra sair da audiência",
                    "Fala sobre o clima"
                ],
                "correta": 1,
                "xp": 25,
                "recompensa_min": 140,
                "recompensa_max": 260
            },
            {
                "pergunta": "O cliente quer fazer um acordo com o Ministério Público. O que você recomenda?",
                "opcoes": [
                    "Aceita qualquer acordo sem analisar",
                    "Analisa os termos, explica as consequências e recomenda o melhor pra ele",
                    "Diz pro cliente recusar tudo",
                    "Ignora o cliente e decide sozinho"
                ],
                "correta": 1,
                "xp": 20,
                "recompensa_min": 130,
                "recompensa_max": 240
            }
        ]
    }



def iniciar_minigame(personagem_id: int, profissao: str) -> dict:
    """
    Inicia um minigame para a profissão do personagem.
    Retorna os dados do minigame pra o cog exibir.
    """
    func = MINIGAMES_POR_PROFISSAO.get(profissao)
    if not func:
        return {
            "sucesso": False,
            "msg": f"❌ Não existe minigame pra profissão **{profissao}**."
        }
    
    # Chama a função do minigame
    dados_minigame = func(personagem_id)
    
    if not dados_minigame:
        return {
            "sucesso": False,
            "msg": "❌ Erro ao iniciar minigame."
        }
    
    return {
        "sucesso": True,
        "titulo": dados_minigame.get("titulo", "Minigame"),
        "descricao": dados_minigame.get("descricao", ""),
        "perguntas": dados_minigame.get("perguntas", []),
        "profissao": profissao,
        "personagem_id": personagem_id,
    }


def resolver_minigame(personagem_id: int, profissao: str, pergunta_idx: int, escolha: int) -> dict:
    """
    Resolve uma pergunta do minigame.
    Retorna resultado (acertou/errou, xp, recompensa).
    """
    func = MINIGAMES_POR_PROFISSAO.get(profissao)
    if not func:
        return {"sucesso": False, "msg": "Minigame não encontrado."}
    
    dados = func(personagem_id)
    perguntas = dados.get("perguntas", [])
    
    if pergunta_idx >= len(perguntas):
        return {"sucesso": False, "msg": "Pergunta inválida."}
    
    pergunta = perguntas[pergunta_idx]
    correta = pergunta["correta"]
    
    acertou = escolha == correta
    
    if acertou:
        xp = pergunta.get("xp", 10)
        recompensa_min = pergunta.get("recompensa_min", 30)
        recompensa_max = pergunta.get("recompensa_max", 100)
        recompensa = random.randint(recompensa_min, recompensa_max)
        
        # Aplicar recompensas
        db.modificar_xp_personagem(personagem_id, xp)
        db.atualizar_saldo_personagem(personagem_id, recompensa)
        db.registrar_trabalho_personagem(personagem_id, recompensa, 5)
        
        return {
            "sucesso": True,
            "acertou": True,
            "resposta_correta": correta,
            "xp": xp,
            "recompensa": recompensa,
            "msg": f"✅ **Acertou!** +{xp} XP, +${recompensa}"
        }
    else:
        return {
            "sucesso": True,
            "acertou": False,
            "resposta_correta": correta,
            "xp": 0,
            "recompensa": 0,
            "msg": f"❌ **Errou!** A resposta correta era: **{pergunta['opcoes'][correta]}**"
        }


MINIGAMES_POR_PROFISSAO = {
    "policial_militar": minigame_patrulha,
    "policial_civil": minigame_blitz,
    "advogado": minigame_consulta,
    "advogado_criminal": minigame_advogado_criminal,
    "medico": minigame_emergencia_medica,
    "samu": minigame_emergencia_medica,
    "professor": minigame_aula,
    "motoboy": minigame_entrega,
    "jogador_futebol": minigame_jogo_futebol,
    "empresario": minigame_negocio,
    "criminoso": minigame_crime,
    "juiz": minigame_audiencia,
    "vendedor": minigame_venda,
    "domestica": minigame_domestica,
}


def obter_minigame(profissao: str) -> dict:
    """Retorna o minigame da profissão."""
    func = MINIGAMES_POR_PROFISSAO.get(profissao)
    if not func:
        return None
    return func(None)  # Chama a função sem personagem_id pra pegar os dados
