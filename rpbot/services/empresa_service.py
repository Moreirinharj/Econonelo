"""Lógica de empresas, compras e mercado de trabalho."""
import random
import database as db
from data.empresas_data import EMPRESAS_REAIS, VAGAS_EMPRESAS
from utils.logger import log_acao


def popular_empresas() -> int:
    """Popula o banco com empresas reais."""
    count = 0
    for emp_id, dados in EMPRESAS_REAIS.items():
        if db.obter_empresa(emp_id):
            continue
        db.criar_empresa(
            empresa_id=emp_id,
            nome=dados["nome"],
            tipo=dados["tipo"],
            descricao=dados["descricao"],
            cidade=dados["cidade"],
            bairro=dados.get("bairro"),
        )
        # Adiciona produtos
        for prod in dados.get("produtos", []):
            db.adicionar_produto(
                empresa_id=emp_id,
                nome=prod["nome"],
                categoria=prod["categoria"],
                preco=prod["preco"],
                estoque=prod["estoque"],
            )
        count += 1
    
    # Cria vagas
    for emp_id, vagas in VAGAS_EMPRESAS.items():
        if not db.obter_empresa(emp_id):
            continue
        for vaga in vagas:
            db.criar_vaga(
                empresa_id=emp_id,
                profissao=vaga["profissao"],
                escolaridade=vaga["escolaridade"],
                salario=vaga["salario"],
                vagas=vaga["vagas"],
                descricao=vaga["descricao"],
            )
    
    log_acao("EMPRESAS_POPULADAS", f"total={count}")
    return count


# Mapeamento: curso formado -> profissões elegíveis
PROFISSOES_POR_CURSO = {
    "medicina": ["medico", "cirurgiao", "cardiologista"],
    "direito": ["advogado", "advogado_criminal", "juiz", "promotor"],
    "engenharia": ["engenheiro_civil", "engenheiro_mecanico"],
    "administracao": ["gerente", "administrador", "analista_negocios"],
    "psicologia": ["psicologo", "terapeuta"],
    "computacao": ["desenvolvedor", "engenheiro_software", "cientista_dados"],
    "matematica": ["matematico", "estatistico", "atuário"],
    "historia": ["historiador", "professor_historia"],
    "biologia": ["biologo", "pesquisador"],
    "economia": ["economista", "analista_financeiro"],
    "jornalismo": ["jornalista", "reporter", "editor"],
    "arquitetura": ["arquiteto", "designer_interiores"],
}


def buscar_vagas_para_formado(personagem_id: int) -> list:
    """Busca vagas compatíveis com a formação do personagem."""
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return []
    
    escolaridade = personagem.get("escolaridade", "nenhuma")
    
    # Busca todas as vagas com escolaridade compatível
    vagas = db.listar_vagas(escolaridade_min=escolaridade)
    
    return vagas[:20]


def comprar_em_empresa(personagem_id: int, empresa_id: str, produto_id: int, quantidade: int = 1) -> dict:
    """Personagem compra produto em uma empresa."""
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    produto = db.obter_produto(produto_id)
    if not produto or produto["empresa_id"] != empresa_id:
        return {"sucesso": False, "msg": "Produto não encontrado nessa empresa."}
    
    valor_total = produto["preco"] * quantidade
    
    if personagem["saldo"] < valor_total:
        return {
            "sucesso": False,
            "msg": f"💸 Saldo insuficiente! Você tem ${personagem['saldo']} e precisa de ${valor_total}.",
            "helper": "💡 Usa `?trabalhar` pra fazer uma grana ou `?sacar` do banco."
        }
    
    # Reduz estoque e paga
    resultado_compra = db.comprar_produto(produto_id, quantidade)
    if not resultado_compra["sucesso"]:
        return resultado_compra
    
    db.atualizar_saldo_personagem(personagem_id, -valor_total)
    
    # Adiciona ao inventário
    db.adicionar_item(personagem_id, produto["nome"], produto["categoria"], quantidade, peso=0.5)
    
    db.registrar_transacao(personagem_id, "compra_empresa", valor_total, f"Compra em {produto['nome']} x{quantidade}")
    
    return {
        "sucesso": True,
        "msg": f"✅ Compra realizada!\n\n**Produto:** {produto['nome']} x{quantidade}\n**Total:** ${valor_total}\n**Empresa:** {db.obter_empresa(empresa_id)['nome']}\n\n💡 O item foi pro teu inventário. Usa `?inventario` pra ver.",
    }


def candidatar_vaga(personagem_id: int, vaga_id: int) -> dict:
    """Personagem se candidata a uma vaga."""
    personagem = db.obter_personagem_por_id(personagem_id)
    if not personagem:
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    vaga = db.obter_vaga(vaga_id)
    if not vaga:
        return {"sucesso": False, "msg": "Vaga não encontrada."}
    
    # Verifica escolaridade
    niveis = {"nenhuma": 0, "fundamental": 1, "medio": 2, "superior": 3, "pos": 4}
    escolaridade_personagem = niveis.get(personagem.get("escolaridade", "nenhuma"), 0)
    escolaridade_vaga = niveis.get(vaga["escolaridade_req"], 0)
    
    if escolaridade_personagem < escolaridade_vaga:
        return {
            "sucesso": False,
            "msg": f"Escolaridade insuficiente. Vaga exige {vaga['escolaridade_req']}, você tem {personagem.get('escolaridade', 'nenhuma')}.",
            "helper": "💡 Usa `?universidades` pra ver cursos e `?estudar` pra se formar."
        }
    
    # Chance de contratação baseada em reputação e nível
    chance = 0.50 + (personagem.get("reputacao", 50) / 200) + (personagem.get("nivel", 1) / 50)
    chance = min(0.90, chance)
    
    if random.random() < chance:
        # Contratado!
        resultado = db.contratar_personagem(vaga_id, personagem_id)
        if not resultado["sucesso"]:
            return resultado
        
        empresa = db.obter_empresa(vaga["empresa_id"])
        return {
            "sucesso": True,
            "contratado": True,
            "msg": f"🎉 VOCÊ FOI CONTRATADO!\n\n**Empresa:** {empresa['nome']}\n**Cargo:** {vaga['profissao'].replace('_', ' ').title()}\n**Salário:** ${vaga['salario']}/mês\n\n💡 Agora usa `?trabalhar` pra começar a trabalhar!",
        }
    else:
        return {
            "sucesso": True,
            "contratado": False,
            "msg": f"😕 Você não foi contratado dessa vez. A empresa escolheu outro candidato.\n\n💡 Continua tentando! Usa `?vagas` pra ver outras oportunidades.",
        }
