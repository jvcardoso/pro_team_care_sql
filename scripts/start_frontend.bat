@echo off
echo ========================================
echo Iniciando Frontend React
echo ========================================

cd frontend

REM Verificar se node_modules existe
if not exist node_modules (
    echo Instalando dependencias...
    call npm install
)

REM Verificar se .env existe
if not exist .env (
    echo AVISO: Arquivo .env nao encontrado!
    echo Copie .env.example para .env
    copy .env.example .env
)

REM Rodar servidor de desenvolvimento
echo.
echo ========================================
echo Frontend rodando em: http://localhost:3000
echo ========================================
echo.

call npm run dev
