#!/bin/bash

# Script para parar OpenCode.ai Server
echo "🛑 Parando OpenCode.ai Server..."

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$PROJECT_DIR"

# Função para parar servidor via PID file
stop_by_pid() {
    if [ -f "opencode.pid" ]; then
        PID=$(cat opencode.pid)

        if kill -0 $PID 2>/dev/null; then
            echo "  🔴 Parando servidor OpenCode.ai (PID: $PID)..."
            kill $PID 2>/dev/null || true
            sleep 2

            # Force kill se ainda estiver rodando
            if kill -0 $PID 2>/dev/null; then
                echo "  ⚠️  Servidor não respondeu, forçando encerramento..."
                kill -9 $PID 2>/dev/null || true
            fi

            echo -e "  ${GREEN}✅ Servidor parado${NC}"
        else
            echo -e "  ${YELLOW}⚠️  Processo não encontrado (PID: $PID)${NC}"
        fi

        rm opencode.pid
    else
        echo -e "  ${YELLOW}⚠️  Arquivo opencode.pid não encontrado${NC}"
    fi
}

# Função para parar todos processos opencode server
stop_all_opencode() {
    echo "  🔍 Procurando processos OpenCode.ai Server..."

    # Encontrar e matar processos
    if pkill -f "opencode.*server" 2>/dev/null; then
        echo -e "  ${GREEN}✅ Processos OpenCode.ai Server parados${NC}"
    else
        echo "  ℹ️  Nenhum processo OpenCode.ai Server encontrado"
    fi
}

echo
echo "=========================================="
echo -e "${BLUE}🛑 PARANDO OPENCODE.AI SERVER${NC}"
echo "=========================================="

# Parar via PID file
stop_by_pid

# Garantir que todos processos foram parados
stop_all_opencode

# Verificar se ainda há processos rodando
sleep 1
if pgrep -f "opencode.*server" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Ainda há processos OpenCode.ai rodando${NC}"
    echo "💡 Use: pkill -9 -f 'opencode.*server'"
else
    echo -e "${GREEN}✅ Todos os servidores OpenCode.ai foram parados!${NC}"
fi

echo
