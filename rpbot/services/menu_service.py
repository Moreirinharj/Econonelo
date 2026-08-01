"""Dados do menu interativo de comandos por categoria."""

CATEGORIAS = {
    "🎭 personagem": {
        "titulo": "🎭 Personagem",
        "descricao": "Criação, edição e visualização do teu personagem.",
        "comandos": [
            ("?jogar <nome>", "Cria um novo personagem"),
            ("?personagens", "Lista teus personagens"),
            ("?ativar <id>", "Ativa um personagem específico"),
            ("?perfil", "Mostra perfil completo"),
            ("?meucpf", "Mostra teu CPF"),
            ("?editar <campo> <valor>", "Edita campos pessoais"),
            ("?editarlist", "Lista campos editáveis"),
        ]
    },
    "📊 status": {
        "titulo": "📊 Status e Saúde",
        "descricao": "Acompanha teu estado físico e mental.",
        "comandos": [
            ("?status", "Mostra todos os status"),
            ("?saude", "Mostra saúde"),
            ("?energia", "Mostra energia"),
            ("?fome", "Mostra fome"),
            ("?felicidade", "Mostra felicidade"),
            ("?estresse", "Mostra estresse"),
            ("?higiene", "Mostra higiene"),
            ("?reputacao", "Mostra reputação"),
            ("?ficha", "Mostra ficha criminal"),
            ("?objetivos", "Mostra/define objetivos"),
        ]
    },
    "💼 profissao": {
        "titulo": "💼 Profissões",
        "descricao": "Escolhe e gerencia tua carreira.",
        "comandos": [
            ("?profissoes", "Lista profissões disponíveis"),
            ("?escolherprofissao <nome>", "Escolhe uma profissão"),
            ("?fazerprova <profissao>", "Faz prova pra profissões com requisito"),
            ("?comandos", "Mostra comandos da tua profissão"),
            ("?pedirdemissao", "Pede demissão"),
            ("?escolherespecialidade", "Escolhe especialidade (professor)"),
            ("?concursos", "Lista concursos abertos"),
            ("?fazerconcurso <id>", "Faz prova de concurso"),
            ("?meusconcursos", "Mostra histórico de concursos"),
        ]
    },
    "🛠️ trabalho": {
        "titulo": "🛠️ Trabalho",
        "descricao": "Trabalha e ganha dinheiro.",
        "comandos": [
            ("?trabalhar", "Inicia minigame da profissão"),
            ("?trabalharrapido", "Trabalho rápido (50% recompensa)"),
            ("?daraula <curso_id>", "Professor dá aula"),
            ("?aplicarprova <@user>", "Professor aplica prova"),
            ("?diagnosticar [@user]", "Médico/SAMU diagnostica"),
            ("?prescrever <@user> <receita>", "Médico prescreve"),
            ("?multar <@user> <motivo>", "Policial multa"),
            ("?revistar <@user>", "Policial revista"),
            ("?roubar <@user>", "Criminoso rouba (risco!)"),
            ("?consultar <@user> <assunto>", "Advogado consulta"),
            ("?contratar <@user> <prof>", "Empresário contrata"),
        ]
    },
    "💰 economia": {
        "titulo": "💰 Economia",
        "descricao": "Gerencia teu dinheiro.",
        "comandos": [
            ("?carteira", "Mostra resumo financeiro"),
            ("?depositar <valor>", "Deposita no banco"),
            ("?sacar <valor>", "Saca do banco"),
            ("?pixchave <chave>", "Define chave PIX"),
            ("?pix <chave> <valor>", "Envia PIX"),
            ("?cartao", "Mostra dados do cartão"),
            ("?pagarcartao <valor>", "Paga fatura do cartão"),
            ("?extrato", "Mostra últimas transações"),
            ("?top", "Ranking de mais ricos"),
            ("?pagar <@user> <valor>", "Paga alguém"),
        ]
    },
    "🎓 educacao": {
        "titulo": "🎓 Educação",
        "descricao": "Estuda e se forma.",
        "comandos": [
            ("?universidades", "Lista cursos disponíveis"),
            ("?infouniversidade [sigla]", "Info de uma universidade"),
            ("?vestibular <id>", "Faz vestibular"),
            ("?matricular <id>", "Matricula no curso"),
            ("?estudar", "Estuda um semestre"),
            ("?minhaseducacao", "Mostra histórico educacional"),
            ("?trancar", "Tranca matrícula"),
            ("?assistiraula <id>", "Assiste aula"),
            ("?aulascurso <id>", "Mostra aulas de um curso"),
        ]
    },
    "⚖️ justica": {
        "titulo": "⚖️ Justiça",
        "descricao": "Sistema judicial completo.",
        "comandos": [
            ("?boletim <descricao>", "Registra B.O."),
            ("?meusboletins", "Mostra teus B.O.s"),
            ("?chamaroab <descricao>", "Chama advogado"),
            ("?denunciar <@user> <crime>", "Abre processo"),
            ("?processos", "Lista processos"),
            ("?assumirdefesa <id>", "Advogado assume defesa"),
            ("?julgar <id> <veredito>", "Juiz julga"),
            ("?pagarfianca <id> <valor>", "Paga fiança"),
            ("?subornar <@user> <valor>", "Tenta subornar"),
            ("?aceitarsuborno <id>", "Aceita suborno"),
            ("?recusarsuborno <id>", "Recusa suborno"),
            ("?denunciarcorrupcao <@user>", "Denuncia corrupção"),
            ("?historiocorrupcao", "Mostra histórico"),
        ]
    },
    "🏢 empresas": {
        "titulo": "🏢 Empresas e Compras",
        "descricao": "Empresas reais e mercado de trabalho.",
        "comandos": [
            ("?empresas [tipo]", "Lista empresas"),
            ("?loja <id>", "Mostra produtos"),
            ("?comprar <id_emp> <id_prod> [qtd]", "Compra produto"),
            ("?vagas", "Mostra vagas compatíveis"),
            ("?candidatar <id>", "Se candidata a vaga"),
            ("?statusempresa <id>", "Status da empresa"),
            ("?rankingempresas", "Ranking por saldo"),
        ]
    },
    "🛵 delivery": {
        "titulo": "🛵 Delivery",
        "descricao": "Pede e entrega comida/produtos.",
        "comandos": [
            ("?ifood", "Empresas com delivery"),
            ("?cardapio <id>", "Cardápio da empresa"),
            ("?pedir <id_emp> <id_prod> [qtd]", "Faz pedido"),
            ("?meuspedidos", "Teus pedidos"),
            ("?pedidospendentes", "Pedidos pra motoboy"),
            ("?aceitarentrega <id>", "Aceita entrega"),
            ("?completarentrega <id>", "Completa entrega"),
        ]
    },
    "🏠 casa": {
        "titulo": "🏠 Casa e Veículo",
        "descricao": "Imóveis e veículos.",
        "comandos": [
            ("?casas", "Casas à venda"),
            ("?minhascasas", "Tuas casas"),
            ("?comprarcasa <id>", "Compra casa"),
            ("?vendercasa <id>", "Vende casa"),
            ("?reformar <id> <decor>", "Reforma casa"),
            ("?cofredepositar <id> <valor>", "Deposita no cofre"),
            ("?cofresacar <id> <valor>", "Saca do cofre"),
            ("?veiculos", "Veículos à venda"),
            ("?garagem", "Teus veículos"),
            ("?comprarveiculo <id>", "Compra veículo"),
            ("?venderveiculo <id>", "Vende veículo"),
            ("?abastecer <placa> <litros>", "Abastece"),
            ("?reparar <placa>", "Repara veículo"),
            ("?seguro <placa>", "Ativa/desativa seguro"),
        ]
    },
    "🌍 imersao": {
        "titulo": "🌍 Imersão e Mundo",
        "descricao": "Viagens, clima e mundo vivo.",
        "comandos": [
            ("?meuestado", "Mostra teu estado atual"),
            ("?aeroportos", "Destinos disponíveis"),
            ("?viajar <UF>", "Viaja pra outro estado"),
            ("?voltarparacasa", "Volta pra terra natal"),
            ("?infoestado [UF]", "Info de um estado"),
            ("?clima", "Previsão do tempo"),
            ("?mundo", "Estado do mundo"),
            ("?noticias", "Últimas notícias"),
            ("?locais", "Locais do mundo"),
            ("?eventos", "Eventos ativos"),
        ]
    },
    "👥 social": {
        "titulo": "👥 Social",
        "descricao": "Família, NPCs e relacionamentos.",
        "comandos": [
            ("?familia", "Mostra tua família"),
            ("?adicionarfam <@user> <tipo>", "Adiciona familiar"),
            ("?aceitarfam <id>", "Aceita pedido"),
            ("?removerfam <id>", "Remove familiar"),
            ("?npcs", "Lista NPCs"),
            ("?npc <id>", "Info de um NPC"),
            ("?conversar <id>", "Conversa com NPC"),
            ("?darnpc <id> <valor>", "Dá dinheiro ao NPC"),
            ("?adicionaramante <@user>", "Adiciona amante secreto"),
            ("?veramante", "Mostra teu amante"),
            ("?terminaramante", "Termina com amante"),
            ("?verificartraicao", "Verifica se foi descoberto"),
        ]
    },
    "🎒 acoes": {
        "titulo": "🎒 Ações e Inventário",
        "descricao": "Ações diárias e itens.",
        "comandos": [
            ("?inventario", "Mostra inventário"),
            ("?daritem <item> <@user>", "Dá item pra alguém"),
            ("?usaritem <id>", "Usa item"),
            ("?equipar <id>", "Equipa item"),
            ("?desequipar <id>", "Desequipa item"),
            ("?comer", "Come e recupera fome"),
            ("?dormir [horas]", "Dorme e recupera energia"),
            ("?banho", "Toma banho"),
            ("?relaxar", "Reduz estresse"),
            ("?verificar", "Verifica status críticos"),
        ]
    },
    "📜 heranca": {
        "titulo": "📜 Herança",
        "descricao": "Testamento e herança.",
        "comandos": [
            ("?testamento", "Vê teu testamento"),
            ("?testamento criar @user %...", "Cria testamento"),
            ("?testamento cancelar", "Cancela testamento"),
            ("?verherdeiros", "Mostra herdeiros legais"),
            ("?heranca", "Heranças pendentes"),
            ("?receberheranca <id>", "Recebe herança"),
        ]
    },
    "🆔 identificacao": {
        "titulo": "🆔 Identificação",
        "descricao": "CPF e investigação.",
        "comandos": [
            ("?meucpf", "Mostra teu CPF"),
            ("?investigar <cpf>", "Investiga CPF (autoridades)"),
        ]
    },
    "❓ ajuda": {
        "titulo": "❓ Ajuda",
        "descricao": "Comandos de ajuda.",
        "comandos": [
            ("?ajuda", "Lista de comandos"),
            ("?ajuda <comando>", "Detalhes de um comando"),
            ("?menu", "Este menu interativo"),
        ]
    },
}


def obter_categorias() -> dict:
    """Retorna todas as categorias."""
    return CATEGORIAS


def obter_categoria(chave: str) -> dict:
    """Retorna uma categoria específica."""
    return CATEGORIAS.get(chave)


def formatar_categoria_embed(categoria: dict) -> str:
    """Formata uma categoria como texto legível."""
    linhas = []
    for cmd, desc in categoria["comandos"]:
        linhas.append(f"• `{cmd}` — {desc}")
    return "\n".join(linhas)
