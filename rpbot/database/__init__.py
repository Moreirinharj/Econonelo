from database.conexao import iniciar_banco, conectar, DB_PATH, SCHEMA_VERSION
from database.personagens import (contar_personagens, criar_personagem, listar_personagens, obter_personagem_ativo, obter_personagem_por_id, definir_personagem_ativo, atualizar_saldo_personagem, definir_profissao_personagem, registrar_trabalho_personagem, listar_top_saldos, listar_todos_personagens, prender_personagem, soltar_personagem, listar_profissionais, listar_advogados_disponiveis, atualizar_status_personagem, modificar_status_personagem, atualizar_escolaridade, atualizar_objetivos, adicionar_registro_criminal, limpar_ficha_criminal, atualizar_identidade, editar_personagem_pessoal, pegar_personagem_ativo, pegar_personagem_por_id, top_saldos, todos_personagens)
from database.relacionamentos import (criar_pedido_relacao, responder_pedido_relacao, remover_relacao_direta, listar_familia, ja_existe_relacao, contar_pais)
from database.chamados import (abrir_chamado_emergencia, atender_chamado_emergencia, obter_chamado_emergencia, abrir_chamado_oab, assumir_chamado_oab, pegar_chamado_emergencia)
from database.oab import (salvar_boletim, listar_boletins, abrir_processo_oab, listar_processos_abertos, resolver_processo_oab)
from database.inventario import (adicionar_item, remover_item, listar_inventario, calcular_peso_total, equipar_item, desequipar_item, obter_item)
from database.economia import (obter_saldo_banco, modificar_saldo_banco, obter_dados_cartao, comprar_cartao, pagar_fatura, definir_chave_pix, obter_chave_pix, buscar_personagem_por_pix, registrar_transacao, listar_transacoes)
from database.npcs import (criar_npc, obter_npc, listar_npcs, modificar_humor_npc, modificar_dinheiro_npc, desativar_npc, contar_npcs)
from database.eventos import (criar_evento, listar_eventos_ativos, obter_evento, desativar_evento, limpar_eventos_expirados)
from database.casas import (criar_casa, obter_casa, listar_casas_disponiveis, listar_casas_do_proprietario, comprar_casa, vender_casa, depositar_no_cofre, sacar_do_cofre, mudar_decoracao)
from database.veiculos import (gerar_placa, criar_veiculo, obter_veiculo, listar_veiculos_disponiveis, listar_veiculos_do_proprietario, comprar_veiculo, vender_veiculo, abastecer_veiculo, reparar_veiculo, toggle_seguro, aplicar_acidente)
from database.locais import (criar_local, obter_local, listar_locais, contar_locais, desativar_local, local_aberto_agora)
from database.justica import (abrir_processo, obter_processo, listar_processos, assumir_defesa, designar_juiz, proferir_sentenca, pagar_fianca)
from database.educacao import (criar_curso, listar_cursos, obter_curso, matricular, obter_matricula_ativa, listar_matriculas_personagem, avancar_semestre, concluir_curso, atualizar_nota_media, contar_matriculas_ativas)
from database.mundo import (obter_estado_mundo, atualizar_estado_mundo, adicionar_noticia, listar_noticias_recentes, simular_acao_npc_aleatoria)
from database.corrupcao import (registrar_tentativa_suborno, aceitar_suborno, denunciar_suborno, listar_subornos_envolvidos, obter_tentativa_suborno, atualizar_reputacao_corrupta, obter_reputacao_corrupta)

__all__ = ["iniciar_banco", "conectar", "DB_PATH", "SCHEMA_VERSION", "contar_personagens", "criar_personagem", "listar_personagens", "obter_personagem_ativo", "obter_personagem_por_id", "definir_personagem_ativo", "atualizar_saldo_personagem", "definir_profissao_personagem", "registrar_trabalho_personagem", "listar_top_saldos", "listar_todos_personagens", "prender_personagem", "soltar_personagem", "listar_profissionais", "listar_advogados_disponiveis", "atualizar_status_personagem", "modificar_status_personagem", "atualizar_escolaridade", "atualizar_objetivos", "adicionar_registro_criminal", "limpar_ficha_criminal", "atualizar_identidade", "editar_personagem_pessoal", "criar_pedido_relacao", "responder_pedido_relacao", "remover_relacao_direta", "listar_familia", "ja_existe_relacao", "contar_pais", "abrir_chamado_emergencia", "atender_chamado_emergencia", "obter_chamado_emergencia", "abrir_chamado_oab", "assumir_chamado_oab", "salvar_boletim", "listar_boletins", "abrir_processo_oab", "listar_processos_abertos", "resolver_processo_oab", "adicionar_item", "remover_item", "listar_inventario", "calcular_peso_total", "equipar_item", "desequipar_item", "obter_item", "obter_saldo_banco", "modificar_saldo_banco", "obter_dados_cartao", "comprar_cartao", "pagar_fatura", "definir_chave_pix", "obter_chave_pix", "buscar_personagem_por_pix", "registrar_transacao", "listar_transacoes", "criar_npc", "obter_npc", "listar_npcs", "modificar_humor_npc", "modificar_dinheiro_npc", "desativar_npc", "contar_npcs", "criar_evento", "listar_eventos_ativos", "obter_evento", "desativar_evento", "limpar_eventos_expirados", "criar_casa", "obter_casa", "listar_casas_disponiveis", "listar_casas_do_proprietario", "comprar_casa", "vender_casa", "depositar_no_cofre", "sacar_do_cofre", "mudar_decoracao", "gerar_placa", "criar_veiculo", "obter_veiculo", "listar_veiculos_disponiveis", "listar_veiculos_do_proprietario", "comprar_veiculo", "vender_veiculo", "abastecer_veiculo", "reparar_veiculo", "toggle_seguro", "aplicar_acidente", "criar_local", "obter_local", "listar_locais", "contar_locais", "desativar_local", "local_aberto_agora", "abrir_processo", "obter_processo", "listar_processos", "assumir_defesa", "designar_juiz", "proferir_sentenca", "pagar_fianca", "criar_curso", "listar_cursos", "obter_curso", "matricular", "obter_matricula_ativa", "listar_matriculas_personagem", "avancar_semestre", "concluir_curso", "atualizar_nota_media", "contar_matriculas_ativas", "obter_estado_mundo", "atualizar_estado_mundo", "adicionar_noticia", "listar_noticias_recentes", "simular_acao_npc_aleatoria", "registrar_tentativa_suborno", "aceitar_suborno", "denunciar_suborno", "listar_subornos_envolvidos", "obter_tentativa_suborno", "atualizar_reputacao_corrupta", "obter_reputacao_corrupta", "pegar_personagem_ativo", "pegar_personagem_por_id", "top_saldos", "todos_personagens", "pegar_chamado_emergencia"]

from database.empresas import (
    criar_empresa,
    obter_empresa,
    listar_empresas,
    adicionar_produto,
    listar_produtos,
    obter_produto,
    comprar_produto,
    criar_vaga,
    listar_vagas,
    obter_vaga,
    contratar_personagem,
    pedir_demissao_empresa,
)

# ===== Imports adicionados pela auditoria v2 =====
from database.estados_temporarios import (
    salvar_estado,
    remover_estado,
    limpar_estados_expirados,
)
from database.concursos import (
    abrir_concurso,
    listar_concursos_abertos,
    obter_concurso,
    registrar_participacao,
    ja_participou_concurso,
    listar_participacoes_personagem,
    definir_cargo_professor,
    obter_ranking_concurso,
)
from database.concursos_profissao import (
    abrir_concurso_profissao,
    listar_concursos_profissao,
    registrar_aprovacao_profissao,
    ja_passou_concurso_profissao,
    registrar_aula,
    registrar_presenca,
    incrementar_alunos_aula,
    obter_aula,
    listar_aulas_professor,
    listar_aulas_curso,
    ja_assistiu_aula,
)

# ===== XP =====
from database.personagem import modificar_xp_personagem

# ===== vagas =====
from database.vagas import (
    criar_vaga,
    listar_vagas,
    obter_vaga,
    contratar_personagem,
    pedir_demissao,
)

# ===== produtos =====
from database.produtos import (
    adicionar_produto,
    listar_produtos,
    obter_produto,
    comprar_produto,
    atualizar_estoque,
)

# ===== processos =====
from database.processos import (
    criar_processo,
    listar_processos,
    obter_processo,
    atribuir_advogado,
    julgar_processo,
)

# ===== pedidos_delivery =====
from database.pedidos_delivery import (
    criar_pedido,
    listar_pedidos,
    obter_pedido,
    atribuir_motoboy,
    finalizar_entrega,
)

# ===== herancas =====
from database.herancas import (
    criar_heranca,
    listar_herancas,
    obter_heranca,
    processar_heranca,
)

# ===== acoes_privadas =====
from database.acoes_privadas import (
    criar_acao_privada,
    listar_acoes_privadas,
    obter_acao_privada,
    marcar_visualizada,
)

from database.personagens import obter_personagem_por_cpf, prender_personagem

from database.personagens import obter_personagem_por_cpf, atualizar_saldo_personagem, atualizar_vida_personagem, prender_personagem
from database.processos import criar_processo
from database.personagens import obter_personagem_por_discord_id, criar_personagem, listar_cpfs_em_uso, liberar_cpf_na_morte
