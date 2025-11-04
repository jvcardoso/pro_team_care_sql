"""
Configuração do banco de dados de LOGS (pro_team_care_logs).

Este banco é SEPARADO do banco principal para:
- Isolar o crescimento de logs do banco operacional
- Proteger contra o limite de 10GB do SQL Server Express
- Melhorar performance (logs não competem com transações de negócio)
- Permitir políticas de retenção independentes
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

# ========================================
# ENGINE ASSÍNCRONO - BANCO DE LOGS
# ========================================
logs_engine = create_async_engine(
    settings.DATABASE_LOGS_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,          # Pool menor para logs (menos concorrência)
    max_overflow=10,
    pool_recycle=3600,
)

# ========================================
# SESSION FACTORY - LOGS
# ========================================
AsyncLogsSessionLocal = async_sessionmaker(
    bind=logs_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# ========================================
# BASE DECLARATIVA - LOGS
# ========================================
LogsBase = declarative_base()

# ========================================
# DEPENDENCY INJECTION - LOGS
# ========================================
async def get_logs_db():
    """
    Dependency para injetar sessão do banco de logs nas rotas.

    Uso:
        async def my_function(logs_db: AsyncSession = Depends(get_logs_db)):
            ...
    """
    async with AsyncLogsSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
