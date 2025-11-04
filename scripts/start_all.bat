@echo off
echo ========================================
echo Iniciando Backend e Frontend
echo ========================================

REM Obter o diretório do script
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%.."

REM Abrir backend em nova janela
echo Iniciando Backend...
start "Backend API" cmd /k "cd /d %CD% && scripts\start_backend.bat"

REM Aguardar 5 segundos
echo Aguardando backend iniciar...
timeout /t 5 /nobreak

REM Abrir frontend em nova janela
echo Iniciando Frontend...
start "Frontend React" cmd /k "cd /d %CD% && scripts\start_frontend.bat"

echo.
echo ========================================
echo Servidores iniciados!
echo ========================================
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo Feche esta janela quando terminar.
