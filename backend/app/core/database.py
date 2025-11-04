"""
Configuração do banco de dados SQL Server com SQLAlchemy async.

⚠️ DATABASE FIRST: Este arquivo NÃO cria tabelas automaticamente.
   Tabelas devem ser criadas manualmente no SQL Server.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

# ========================================
# ENGINE ASSÍNCRONO
# ========================================
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log de queries SQL no console
    pool_pre_ping=True,   # Verifica conexão antes de usar
    pool_size=10,         # Tamanho do pool de conexões
    max_overflow=20,      # Conexões extras além do pool
    pool_recycle=3600,    # Recicla conexões a cada 1h
)

# ========================================
# SESSION FACTORY
# ========================================
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Não expira objetos após commit
    autoflush=False,
)

# ========================================
# BASE DECLARATIVA
# ========================================
Base = declarative_base()

# ========================================
# DEPENDENCY INJECTION
# ========================================
async def get_db():
    """
    Dependency para injetar sessão do banco nas rotas.

    Uso:
        @router.get("/users")
        async def list_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ========================================
# ⚠️ DATABASE FIRST: NÃO CRIAR TABELAS
# ========================================
# REMOVIDO: create_tables() e drop_tables()
# As tabelas devem ser criadas manualmente no SQL Server
# Ver: sql_scripts/ para exemplos de criação
