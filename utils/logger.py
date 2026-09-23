import logging
from pathlib import Path

def configurar_logger(nome_modulo: str) -> logging.Logger:
    """
    Configura um logger profissional para salvar o histórico de execução 
    e as ações do Auditor (QA) no servidor.
    """
    Path("logs").mkdir(exist_ok=True) # Garante que a pasta logs existe
    
    logger = logging.getLogger(nome_modulo)
    logger.setLevel(logging.DEBUG)
    
    if not logger.handlers:
        # Formato da mensagem: [DATA] - [MÓDULO] - NÍVEL - MENSAGEM
        formatter = logging.Formatter('%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')
        
        # Salva em arquivo
        file_handler = logging.FileHandler("logs/pipeline_execucao.log", encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Mostra no terminal do SSH
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger