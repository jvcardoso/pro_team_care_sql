@echo off
echo ========================================
echo Setup Inicial do Projeto
echo ========================================

REM ========================================
REM BACKEND
REM ========================================
echo.
echo [1/5] Criando ambiente virtual Python...
cd backend
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo [2/5] Instalando dependencias Python...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [3/5] Criando arquivo .env do backend...
if not exist .env (
    copy .env.example .env
    echo.
    echo ================================================
    echo IMPORTANTE: Edite backend/.env com suas configuracoes!
    echo ================================================
)

REM ========================================
REM FRONTEND
REM ========================================
echo.
echo [4/5] Instalando dependencias Node.js...
cd ..\frontend
call npm install

echo.
echo [5/5] Criando arquivo .env do frontend...
if not exist .env (
    copy .env.example .env
)

cd ..

echo.
echo ========================================
echo Setup concluido!
echo ========================================
echo.
echo Proximos passos:
echo 1. Edite backend/.env com dados do SQL Server
echo 2. Crie as tabelas no SQL Server (ver sql_scripts/)
echo 3. Execute: scripts\start_all.bat
echo.
pause
