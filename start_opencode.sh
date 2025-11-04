#!/bin/bash

# Script para iniciar OpenCode.ai Server
echo "🤖 Iniciando OpenCode.ai Server..."

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verificar se OpenCode.ai está instalado
check_opencode() {
    echo "🔍 Verificando instalação do OpenCode.ai..."

    if ! command -v opencode >/dev/null 2>&1; then
        echo -e "${RED}❌ OpenCode.ai não está instalado!${NC}"
        echo
        echo -e "${BLUE}💡 Instale com:${NC}"
        echo "   npm install -g @opencode-ai/cli"
        echo "   ou"
        echo "   brew install opencode-ai/tap/opencode"
        echo
        exit 1
    fi

    OPENCODE_VERSION=$(opencode --version 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✅ OpenCode.ai: $OPENCODE_VERSION${NC}"
}

# Verificar se AGENTS.md existe
check_agents_file() {
    echo "🔍 Verificando AGENTS.md..."

    if [ ! -f "$PROJECT_DIR/AGENTS.md" ]; then
        echo -e "${YELLOW}⚠️  AGENTS.md não encontrado!${NC}"
        echo -e "${BLUE}💡 OpenCode.ai funciona melhor com instruções do projeto em AGENTS.md${NC}"
    else
        echo -e "${GREEN}✅ AGENTS.md encontrado${NC}"
    fi
}

# Parar servidor OpenCode.ai existente
stop_existing() {
    echo "🔄 Verificando servidor OpenCode.ai existente..."

    # Verificar PID file
    if [ -f "$PROJECT_DIR/opencode.pid" ]; then
        OLD_PID=$(cat "$PROJECT_DIR/opencode.pid")
        if kill -0 $OLD_PID 2>/dev/null; then
            echo "  🔴 Parando servidor existente (PID: $OLD_PID)..."
            kill $OLD_PID 2>/dev/null || true
            sleep 2

            # Force kill se ainda estiver rodando
            if kill -0 $OLD_PID 2>/dev/null; then
                kill -9 $OLD_PID 2>/dev/null || true
            fi
        fi
        rm "$PROJECT_DIR/opencode.pid"
    fi

    # Verificar processos opencode server
    pkill -f "opencode.*server" 2>/dev/null || true

    echo "✅ Nenhum servidor OpenCode.ai rodando"
}

# Criar diretório de logs se não existir
create_logs_dir() {
    if [ ! -d "$PROJECT_DIR/logs" ]; then
        mkdir -p "$PROJECT_DIR/logs"
    fi
}

# Verificar instalação
check_opencode

# Mudar para diretório do projeto
cd "$PROJECT_DIR"

# Verificar AGENTS.md
check_agents_file

# Parar servidor existente
stop_existing

# Criar diretório de logs
create_logs_dir

# ========================================
# INICIAR OPENCODE.AI SERVER
# ========================================
echo
echo "=========================================="
echo -e "${BLUE}🚀 INICIANDO OPENCODE.AI SERVER${NC}"
echo "=========================================="

# Iniciar servidor em background
echo "🤖 Iniciando servidor OpenCode.ai..."
opencode server > logs/opencode.log 2>&1 &
OPENCODE_PID=$!
echo $OPENCODE_PID > opencode.pid

# Aguardar inicialização
echo "⏳ Aguardando servidor inicializar..."
sleep 3

# Verificar se está rodando
if kill -0 $OPENCODE_PID 2>/dev/null; then
    echo -e "${GREEN}✅ OpenCode.ai Server rodando (PID: $OPENCODE_PID)${NC}"
else
    echo -e "${RED}❌ Falha ao iniciar OpenCode.ai Server${NC}"
    echo -e "${RED}Verifique logs em: logs/opencode.log${NC}"
    exit 1
fi

# ========================================
# RESUMO
# ========================================
echo
echo "=========================================="
echo -e "${GREEN}🎉 OpenCode.ai Server iniciado!${NC}"
echo "=========================================="
echo
echo -e "${BLUE}📊 INFORMAÇÕES:${NC}"
echo -e "   PID:              $OPENCODE_PID"
echo -e "   Logs:             logs/opencode.log"
echo -e "   Projeto:          $PROJECT_DIR"

if [ -f "AGENTS.md" ]; then
    echo -e "   Instruções:       AGENTS.md (carregado automaticamente)"
fi

echo
echo -e "${BLUE}📖 DOCUMENTAÇÃO:${NC}"
echo -e "   Docs:             https://opencode.ai/docs/server/"
echo -e "   Setup Guide:      docs/OPENCODE_SETUP.md"
echo
echo -e "${BLUE}🛠️  CONTROLE:${NC}"
echo -e "   Parar servidor:   ./stop_opencode.sh"
echo -e "   Ver logs:         tail -f logs/opencode.log"
echo -e "   Status:           ps -p $OPENCODE_PID"
echo
echo -e "${BLUE}💡 USO:${NC}"
echo -e "   Conectar cliente: opencode (em outro terminal)"
echo -e "   Modo interativo:  opencode \"criar endpoint GET /api/v1/users\""
echo
echo -e "${GREEN}✅ Servidor OpenCode.ai pronto para uso!${NC}"
echo

# Mostrar últimas linhas do log
echo "📋 Últimas linhas do log:"
echo "----------------------------------------"
sleep 1
tail -n 10 logs/opencode.log 2>/dev/null || echo "  (aguardando logs...)"
echo "----------------------------------------"
echo

echo -e "${YELLOW}💡 Dica: Use 'tail -f logs/opencode.log' para monitorar em tempo real${NC}"
echo
