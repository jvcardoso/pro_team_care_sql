"""
Configurações centralizadas da aplicação usando Pydantic Settings.
Carrega variáveis de ambiente do arquivo .env
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # ========================================
    # APP
    # ========================================
    APP_NAME: str = "Meu Projeto"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # ========================================
    # DATABASE - SQL SERVER (PRINCIPAL)
    # ========================================
    DB_DRIVER: str = "ODBC Driver 18 for SQL Server"
    DB_SERVER: str
    DB_PORT: int = 1433
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SCHEMA: str = "core"

    @property
    def DATABASE_URL(self) -> str:
        """
        Monta a connection string para SQL Server com driver async.

        Formato: mssql+aioodbc://user:pass@server:port/database?driver=ODBC+Driver+18+for+SQL+Server

        ODBC Driver 18 requer Encrypt=yes por padrão. Para desenvolvimento local
        sem certificado SSL, usamos TrustServerCertificate=yes.

        IMPORTANTE: A senha é URL-encoded para lidar com caracteres especiais como @.
        """
        from urllib.parse import quote

        driver = self.DB_DRIVER.replace(" ", "+")
        # URL-encode da senha para lidar com caracteres especiais
        encoded_password = quote(self.DB_PASSWORD, safe='')
        return (
            f"mssql+aioodbc://{self.DB_USER}:{encoded_password}"
            f"@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}"
            f"?driver={driver}"
            f"&TrustServerCertificate=yes"
            f"&Encrypt=yes"
        )

    # ========================================
    # DATABASE - LOGS (SEPARADO)
    # ========================================
    DB_LOGS_NAME: str = "pro_team_care_logs"
    DB_LOGS_SCHEMA: str = "core"

    @property
    def DATABASE_LOGS_URL(self) -> str:
        """
        Connection string para o banco de logs (pro_team_care_logs).

        Usa as mesmas credenciais e servidor do banco principal,
        mas aponta para o banco dedicado de logs.

        IMPORTANTE: A senha é URL-encoded para lidar com caracteres especiais como @.
        """
        from urllib.parse import quote

        driver = self.DB_DRIVER.replace(" ", "+")
        # URL-encode da senha para lidar com caracteres especiais
        encoded_password = quote(self.DB_PASSWORD, safe='')
        return (
            f"mssql+aioodbc://{self.DB_USER}:{encoded_password}"
            f"@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_LOGS_NAME}"
            f"?driver={driver}"
            f"&TrustServerCertificate=yes"
            f"&Encrypt=yes"
        )

    # ========================================
    # SEGURANÇA / JWT
    # ========================================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ========================================
    # CORS
    # ========================================
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://192.168.11.83:3000,http://192.168.11.83:3001,http://127.0.0.1:3000"

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Converte string separada por vírgula em lista"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ========================================
    # LOGGING
    # ========================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # ========================================
    # GEMINI API (IA)
    # ========================================
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # ========================================
    # PYDANTIC CONFIG
    # ========================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Instância global de configurações
settings = Settings()
