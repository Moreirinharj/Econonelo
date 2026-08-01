import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("rpbot")
logger.setLevel(logging.INFO)

fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

arquivo = RotatingFileHandler(os.path.join(LOG_DIR, "rpbot.log"), maxBytes=2*1024*1024, backupCount=3, encoding="utf-8")
arquivo.setFormatter(fmt)
logger.addHandler(arquivo)

console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)

def log_info(msg): logger.info(msg)
def log_error(msg): logger.error(msg)
def log_acao(acao, detalhes=""): logger.info(f"ACAO | {acao} | {detalhes}")
