@echo off
echo ========================================
echo Iniciando Backend FastAPI
echo ========================================

cd backend

REM Ativar ambiente virtual
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute: scripts\setup_env.bat
    pause
    exit
)

REM Verificar se .env existe
if not exist .env (
    echo ERRO: Arquivo .env nao encontrado!
    echo Copie .env.example para .env e configure.
    pause
    exit
)

REM Rodar servidor
echo.
echo ========================================
echo Servidor rodando em: http://localhost:8000
echo Documentacao: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo ========================================
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
