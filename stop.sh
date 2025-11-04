#!/bin/bash

# Script para parar Meu Projeto
echo "🛑 Parando Meu Projeto..."

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Parar processos via PIDs salvos
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    echo "🔴 Parando backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || true
    rm backend.pid
    echo -e "${GREEN}✅ Backend parado${NC}"
else
    echo "ℹ️  Backend PID não encontrado"
fi

if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    echo "🔴 Parando frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || true
    rm frontend.pid
    echo -e "${GREEN}✅ Frontend parado${NC}"
else
    echo "ℹ️  Frontend PID não encontrado"
fi

# Garantir que processos nas portas foram parados
echo "🧹 Limpando portas..."

# Função para matar processo em porta
kill_port() {
    local port=$1

    if command -v lsof >/dev/null 2>&1; then
        local pids=$(lsof -ti :$port 2>/dev/null || true)
        for pid in $pids; do
            if [ "$pid" != "" ]; then
                echo "  🔴 Matando processo $pid na porta $port"
                kill -9 $pid 2>/dev/null || true
            fi
        done
    fi
}

kill_port 8000
kill_port 3000

# Matar processos específicos
pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
pkill -f "vite.*--port 3000" 2>/dev/null || true

echo
echo -e "${GREEN}✅ Todos os serviços foram parados!${NC}"
