"""
Entry point do FastAPI.

⚠️ DATABASE FIRST: Esta aplicação NÃO cria tabelas automaticamente.
   Certifique-se de criar as tabelas no SQL Server antes de usar.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import decode_token
from app.api.v1.router import api_router
import os

# ========================================
# CRIAR APP FASTAPI
# ========================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API RESTful com FastAPI e SQL Server (Database First)",
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # ReDoc
    openapi_url="/openapi.json",
)

# ========================================
# MIDDLEWARE CORS
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# MIDDLEWARE SESSION_CONTEXT (LGPD)
# ========================================
@app.middleware("http")
async def db_session_context_middleware(request: Request, call_next):
    """
    Middleware para definir o contexto do usuário no banco de dados.

    Define o SESSION_CONTEXT com o user_id para mascaramento dinâmico de dados.
    """
    user_id = None

    # Extrair token do header Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        if payload:
            user_id = payload.get("sub")  # Assumindo que 'sub' contém o user_id

    # Definir contexto no banco se user_id foi encontrado
    if user_id:
        async with AsyncSessionLocal() as db:
            try:
                await db.execute(
                    text("EXEC sp_set_session_context @key = N'user_id', @value = :user_id"),
                    {"user_id": user_id}
                )
                await db.commit()
            except Exception as e:
                # Se falhar, continua sem contexto (segurança por padrão)
                print(f"Warning: Failed to set session context: {e}")
                pass

    response = await call_next(request)
    return response

# ========================================
# ROUTERS
# ========================================
app.include_router(api_router, prefix="/api/v1")

# ========================================
# STATIC FILES (Uploads)
# ========================================
# Criar diretório de uploads se não existir
UPLOAD_DIR = "uploads/kanban"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Montar diretório estático
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ========================================
# HEALTH CHECK
# ========================================
@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint para verificar se API está funcionando"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz"""
    return {
        "message": f"Bem-vindo à API {settings.APP_NAME}",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# ========================================
# STARTUP EVENT
# ========================================
@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação"""
    print("=" * 50)
    print(f"🚀 {settings.APP_NAME} v{settings.VERSION}")
    print(f"📝 Documentação: http://localhost:8000/docs")
    print(f"🔍 Health Check: http://localhost:8000/health")
    print(f"⚠️  DATABASE FIRST: Certifique-se de criar as tabelas manualmente!")
    print("=" * 50)
