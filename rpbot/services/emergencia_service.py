import random
import database as db
from utils.logger import log_acao

CHANCE_PRISAO_BASE = 0.40


class EmergenciaService:
    def __init__(self):
        self.tentativas_prisao = {}
    
    def abrir_chamado(self, personagem_id: int, tipo: str, descricao: str) -> int:
        """Abre um chamado de emergência."""
        chamado_id = db.abrir_chamado_emergencia(personagem_id, tipo, descricao)
        log_acao("SERVICE_CHAMADO_ABERTO", f"id={chamado_id} tipo={tipo}")
        return chamado_id
    
    def atender_chamado(self, chamado_id: int, atendente_id: int, profissao_atendente: str) -> dict:
        """
        Atende um chamado. Retorna dict com:
        - sucesso: bool
        - mensagem: str
        - tipo_resultado: 'prisao' | 'atendimento' | 'fuga'
        """
        chamado = db.obter_chamado_emergencia(chamado_id)
        if chamado is None:
            return {"sucesso": False, "mensagem": "Chamado não encontrado."}
        
        if chamado["status"] != "aberto":
            return {"sucesso": False, "mensagem": "Chamado já foi atendido."}
        
        tipo_esperado = "samu" if chamado["tipo"] == "192" else "policial_militar"
        if profissao_atendente != tipo_esperado:
            return {"sucesso": False, "mensagem": f"Esse chamado é do tipo {chamado['tipo']}, não é sua área."}
        
        alvo = db.obter_personagem_por_id(chamado["personagem_id"])
        
        if chamado["tipo"] == "190":
            return self._tentar_prender(chamado_id, atendente_id, alvo)
        else:
            db.atender_chamado_emergencia(chamado_id, atendente_id)
            return {
                "sucesso": True,
                "mensagem": f"Atendimento concluído. {alvo['nome']} foi atendido.",
                "tipo_resultado": "atendimento",
                "alvo": alvo,
            }
    
    def _tentar_prender(self, chamado_id: int, atendente_id: int, alvo: dict) -> dict:
        """Tenta prender o suspeito."""
        tentativas = self.tentativas_prisao.get(chamado_id, 0)
        chance = min(0.95, CHANCE_PRISAO_BASE + tentativas * 0.15)
        conseguiu = random.random() < chance
        
        if conseguiu:
            db.prender_personagem(alvo["id"])
            db.atender_chamado_emergencia(chamado_id, atendente_id)
            self.tentativas_prisao.pop(chamado_id, None)
            log_acao("SERVICE_PRISAO_EFETUADA", f"chamado_id={chamado_id} alvo_id={alvo['id']}")
            return {
                "sucesso": True,
                "mensagem": f"{alvo['nome']} foi detido e está em prisão temporária.",
                "tipo_resultado": "prisao",
                "alvo": alvo,
            }
        else:
            self.tentativas_prisao[chamado_id] = tentativas + 1
            return {
                "sucesso": False,
                "mensagem": f"{alvo['nome']} escapou (chance era {int(chance * 100)}%).",
                "tipo_resultado": "fuga",
                "alvo": alvo,
                "chance": chance,
            }
