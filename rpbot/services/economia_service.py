"""Lógica econômica: banco, PIX, cartão, transferências."""
import database as db
from utils.logger import log_acao


def depositar(personagem_id: int, valor: int) -> dict:
    """Deposita dinheiro do bolso pro banco."""
    if valor <= 0:
        return {"sucesso": False, "mensagem": "Valor inválido."}
    
    personagem = db.obter_personagem_por_id(personagem_id)
    if personagem["saldo"] < valor:
        return {"sucesso": False, "mensagem": "Dinheiro insuficiente no bolso."}
    
    db.atualizar_saldo_personagem(personagem_id, -valor)
    db.modificar_saldo_banco(personagem_id, valor)
    db.registrar_transacao(personagem_id, "deposito", valor, "Depósito em dinheiro")
    
    log_acao("DEPOSITO", f"personagem_id={personagem_id} valor={valor}")
    return {"sucesso": True, "mensagem": f"Você depositou ${valor} no banco."}


def sacar(personagem_id: int, valor: int) -> dict:
    """Saca dinheiro do banco pro bolso."""
    if valor <= 0:
        return {"sucesso": False, "mensagem": "Valor inválido."}
    
    saldo_banco = db.obter_saldo_banco(personagem_id)
    if saldo_banco < valor:
        return {"sucesso": False, "mensagem": f"Saldo insuficiente no banco. Você tem ${saldo_banco}."}
    
    db.modificar_saldo_banco(personagem_id, -valor)
    db.atualizar_saldo_personagem(personagem_id, valor)
    db.registrar_transacao(personagem_id, "saque", valor, "Saque em dinheiro")
    
    log_acao("SAQUE", f"personagem_id={personagem_id} valor={valor}")
    return {"sucesso": True, "mensagem": f"Você sacou ${valor} do banco."}


def pix_enviar(personagem_id: int, chave_destino: str, valor: int) -> dict:
    """Envia PIX pra outro personagem via chave."""
    if valor <= 0:
        return {"sucesso": False, "mensagem": "Valor inválido."}
    
    destino = db.buscar_personagem_por_pix(chave_destino)
    if destino is None:
        return {"sucesso": False, "mensagem": "Chave PIX não encontrada."}
    
    if destino["id"] == personagem_id:
        return {"sucesso": False, "mensagem": "Você não pode enviar PIX pra si mesmo."}
    
    saldo_banco = db.obter_saldo_banco(personagem_id)
    if saldo_banco < valor:
        return {"sucesso": False, "mensagem": f"Saldo insuficiente no banco. Você tem ${saldo_banco}."}
    
    db.modificar_saldo_banco(personagem_id, -valor)
    db.modificar_saldo_banco(destino["id"], valor)
    db.registrar_transacao(personagem_id, "pix_enviado", valor, f"PIX para {destino['nome']}", destino["id"])
    db.registrar_transacao(destino["id"], "pix_recebido", valor, f"PIX de {db.obter_personagem_por_id(personagem_id)['nome']}", personagem_id)
    
    log_acao("PIX_ENVIADO", f"de={personagem_id} para={destino['id']} valor={valor}")
    return {
        "sucesso": True,
        "mensagem": f"PIX de ${valor} enviado para {destino['nome']}!",
        "destino": destino,
    }


def pagar_cartao(personagem_id: int, valor: int) -> dict:
    """Paga fatura do cartão usando saldo do banco."""
    return db.pagar_fatura(personagem_id, valor)


def extrato_resumido(personagem_id: int) -> dict:
    """Retorna resumo financeiro completo."""
    personagem = db.obter_personagem_por_id(personagem_id)
    cartao = db.obter_dados_cartao(personagem_id)
    transacoes = db.listar_transacoes(personagem_id, 10)
    
    return {
        "bolso": personagem["saldo"],
        "banco": db.obter_saldo_banco(personagem_id),
        "cartao": cartao,
        "chave_pix": personagem.get("chave_pix"),
        "ultimas_transacoes": transacoes,
    }
