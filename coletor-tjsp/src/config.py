"""
Configurações do coletor TJSP
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configurações centralizadas do sistema"""
    
    # --- PATHS ---
    BASE_DIR = Path(__file__).parent.parent
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))
    LOG_DIR = Path(os.getenv("LOG_DIR", "./logs"))
    CACHE_DIR = Path(os.getenv("CACHE_DIR", "./cache"))
    INPUT_DIR = BASE_DIR / "input"
    
    # --- DELAYS E TIMEOUTS ---
    MIN_DELAY = int(os.getenv("MIN_DELAY", "5"))
    MAX_DELAY = int(os.getenv("MAX_DELAY", "15"))
    PAGE_TIMEOUT = int(os.getenv("PAGE_TIMEOUT", "30")) * 1000  # em ms
    ELEMENT_TIMEOUT = int(os.getenv("ELEMENT_TIMEOUT", "10")) * 1000  # em ms
    
    # --- RETRY E RESILIÊNCIA ---
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "10"))
    BACKOFF_MULTIPLIER = float(os.getenv("BACKOFF_MULTIPLIER", "1.5"))
    
    # --- CONTROLE DE TAXA ---
    MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "1"))
    MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "6"))
    
    # --- USER AGENT ---
    USER_AGENT = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    # --- MODO DEBUG ---
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    SAVE_SCREENSHOTS = os.getenv("SAVE_SCREENSHOTS", "true").lower() == "true"
    
    # --- LIMITES ---
    MAX_MOVIMENTACOES = int(os.getenv("MAX_MOVIMENTACOES", "0"))  # 0 = sem limite
    MAX_SEARCH_PAGES = int(os.getenv("MAX_SEARCH_PAGES", "10"))
    
    # --- BROWSER ---
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    BROWSER_WIDTH = int(os.getenv("BROWSER_WIDTH", "1920"))
    BROWSER_HEIGHT = int(os.getenv("BROWSER_HEIGHT", "1080"))
    
    # --- LOGS ---
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ROTATE_LOGS = os.getenv("ROTATE_LOGS", "true").lower() == "true"
    MAX_LOG_SIZE = int(os.getenv("MAX_LOG_SIZE", "10"))
    LOG_RETENTION = int(os.getenv("LOG_RETENTION", "7"))
    
    # --- URLs TJSP ---
    TJSP_BASE_URL = "https://esaj.tjsp.jus.br"
    TJSP_SEARCH_URL = f"{TJSP_BASE_URL}/cpopg/search.do"
    TJSP_OPEN_URL = f"{TJSP_BASE_URL}/cpopg/show.do"
    
    # --- CLASSIFICAÇÃO ---
    DECISION_CONFIDENCE_THRESHOLD = float(
        os.getenv("DECISION_CONFIDENCE_THRESHOLD", "0.7")
    )
    
    @classmethod
    def create_directories(cls):
        """Cria diretórios necessários se não existirem"""
        for directory in [cls.OUTPUT_DIR, cls.LOG_DIR, cls.CACHE_DIR, cls.INPUT_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_output_path(cls, filename: str) -> Path:
        """Retorna caminho completo para arquivo de saída"""
        return cls.OUTPUT_DIR / filename
    
    @classmethod
    def get_cache_path(cls, filename: str) -> Path:
        """Retorna caminho completo para arquivo de cache"""
        return cls.CACHE_DIR / filename
    
    @classmethod
    def get_log_path(cls, filename: str) -> Path:
        """Retorna caminho completo para arquivo de log"""
        return cls.LOG_DIR / filename

# Cria diretórios na importação
Config.create_directories()
