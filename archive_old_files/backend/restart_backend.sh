#!/bin/bash
# Script para reiniciar o backend FastAPI

echo "=== REINICIANDO BACKEND FASTAPI ==="
echo ""

# Matar processo uvicorn existente
echo "🛑 Parando servidor existente..."
pkill -f "uvicorn app.main:app"
sleep 2

# Verificar se parou
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "⚠️  Processo ainda rodando, forçando..."
    pkill -9 -f "uvicorn app.main:app"
    sleep 1
fi

echo "✅ Servidor parado"
echo ""

# Iniciar novamente
echo "🚀 Iniciando servidor..."
cd /home/juliano/Projetos/meu_projeto/backend

# Ativar venv e iniciar em background
source venv/bin/activate
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > logs/uvicorn.log 2>&1 &

sleep 3

# Verificar se iniciou
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "✅ Servidor iniciado com sucesso!"
    echo ""
    echo "📋 Informações:"
    echo "   - URL: http://192.168.11.83:8000"
    echo "   - Docs: http://192.168.11.83:8000/docs"
    echo "   - Health: http://192.168.11.83:8000/health"
    echo "   - Logs: tail -f logs/uvicorn.log"
    echo ""
    echo "🔍 Verificando CORS..."
    sleep 2
    curl -s http://192.168.11.83:8000/health | python3 -m json.tool
else
    echo "❌ Falha ao iniciar servidor"
    echo "Verifique os logs: tail -f logs/uvicorn.log"
    exit 1
fi
