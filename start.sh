#!/bin/bash

# Script para iniciar Meu Projeto (Database First)
echo "🚀 Iniciando Meu Projeto..."
echo "🔍 Verificando sistema..."

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detectar IP local (ou usar localhost)
detect_ip() {
    # Tentar pegar IP local
    if command -v hostname >/dev/null 2>&1; then
        LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi

    # Se não conseguir, usar localhost
    if [ -z "$LOCAL_IP" ] || [ "$LOCAL_IP" = "" ]; then
        LOCAL_IP="localhost"
    fi

    echo "$LOCAL_IP"
}

HOST_IP=$(detect_ip)
echo -e "${BLUE}📡 IP detectado: $HOST_IP${NC}"

# Verificar comandos necessários
check_system() {
    local missing_commands=()

    # Verificar Python
    if ! command -v python3 >/dev/null 2>&1; then
        missing_commands+=("python3")
    fi

    # Verificar se temos pelo menos um comando para verificar portas
    if ! command -v netstat >/dev/null 2>&1 && ! command -v ss >/dev/null 2>&1 && ! command -v lsof >/dev/null 2>&1; then
        missing_commands+=("netstat/ss/lsof")
    fi

    if [ ${#missing_commands[@]} -gt 0 ]; then
        echo -e "${RED}❌ Comandos necessários não encontrados: ${missing_commands[*]}${NC}"
        echo -e "${BLUE}💡 Instale com: sudo apt install net-tools python3${NC}"
        exit 1
    fi

    echo "✅ Sistema verificado - todos os comandos disponíveis"
}

# Função para limpar cache
clean_cache() {
    echo "🧹 Limpando cache..."

    # Cache Python
    echo "  🐍 Limpando cache Python..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true

    # Cache Node.js
    if [ -d "frontend" ]; then
        echo "  ⚛️  Limpando cache Node.js..."
        cd frontend
        rm -rf node_modules/.vite 2>/dev/null || true
        npm cache clean --force 2>/dev/null || true
        cd ..
    fi

    echo "✅ Cache limpo"
}

# Função para matar processos existentes
kill_existing() {
    echo "🔄 Parando processos existentes..."

    # Matar processos específicos do projeto
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    pkill -f "vite.*--port 3000" 2>/dev/null || true

    # Matar processos nas portas específicas
    echo "🧹 Limpando portas 3000, 8000..."

    # Função para matar processo em uma porta específica
    kill_port() {
        local port=$1

        # Tentar com lsof (mais confiável)
        if command -v lsof >/dev/null 2>&1; then
            local lsof_pids=$(lsof -ti :$port 2>/dev/null || true)
            for pid in $lsof_pids; do
                if [ "$pid" != "" ] && [ "$pid" != "0" ]; then
                    echo "  🔴 Matando processo $pid na porta $port"
                    kill -9 $pid 2>/dev/null || true
                fi
            done
        fi

        # Alternativa com netstat
        if command -v netstat >/dev/null 2>&1; then
            local pids=$(netstat -tulpn 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | grep -v '-' | sort -u 2>/dev/null)
            for pid in $pids; do
                if [ "$pid" != "" ] && [ "$pid" != "0" ]; then
                    echo "  🔴 Matando processo $pid na porta $port"
                    kill -9 $pid 2>/dev/null || true
                fi
            done
        fi

        # Alternativa com ss
        if command -v ss >/dev/null 2>&1; then
            local ss_pids=$(ss -tulpn 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d',' -f2 | cut -d'=' -f2 | grep -v '-' | sort -u 2>/dev/null)
            for pid in $ss_pids; do
                if [ "$pid" != "" ] && [ "$pid" != "0" ]; then
                    echo "  🔴 Matando processo $pid na porta $port"
                    kill -9 $pid 2>/dev/null || true
                fi
            done
        fi
    }

    # Limpar todas as portas que vamos usar
    kill_port 3000
    kill_port 8000

    # Aguardar processos terminarem
    sleep 2

    # Verificar se as portas estão livres
    echo "✅ Verificando portas..."
    for port in 3000 8000; do
        if command -v lsof >/dev/null 2>&1; then
            if lsof -i :$port >/dev/null 2>&1; then
                echo "  ⚠️  Porta $port ainda ocupada"
            else
                echo "  ✅ Porta $port livre"
            fi
        elif command -v netstat >/dev/null 2>&1; then
            if netstat -tulpn 2>/dev/null | grep -q ":$port "; then
                echo "  ⚠️  Porta $port ainda ocupada"
            else
                echo "  ✅ Porta $port livre"
            fi
        fi
    done
}

# Verificar estrutura do projeto
check_structure() {
    echo "🔍 Verificando estrutura do projeto..."

    if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        echo -e "${RED}❌ Estrutura do projeto incorreta!${NC}"
        echo -e "${BLUE}Esperado: backend/ e frontend/${NC}"
        exit 1
    fi

    if [ ! -f "backend/app/main.py" ]; then
        echo -e "${RED}❌ Backend não encontrado em backend/app/main.py${NC}"
        exit 1
    fi

    if [ ! -f "frontend/package.json" ]; then
        echo -e "${RED}❌ Frontend não encontrado em frontend/package.json${NC}"
        exit 1
    fi

    echo "✅ Estrutura do projeto OK"
}

# Verificar configuração
check_config() {
    echo "🔍 Verificando configuração..."

    # Backend .env
    if [ ! -f "backend/.env" ]; then
        echo -e "${YELLOW}⚠️  Arquivo backend/.env não encontrado!${NC}"
        echo -e "${BLUE}💡 Criando a partir do .env.example...${NC}"
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example backend/.env
            echo -e "${YELLOW}⚠️  IMPORTANTE: Configure backend/.env com dados do SQL Server!${NC}"
        else
            echo -e "${RED}❌ .env.example não encontrado!${NC}"
            exit 1
        fi
    fi

    # Frontend .env
    if [ ! -f "frontend/.env" ]; then
        echo -e "${YELLOW}⚠️  Arquivo frontend/.env não encontrado!${NC}"
        echo "💡 Criando..."
        echo "VITE_API_URL=http://$HOST_IP:8000" > frontend/.env
    fi

    echo "✅ Configuração verificada"
}

# Verificar sistema antes de tudo
check_system

# Mudar para o diretório do projeto
cd "$PROJECT_DIR"

# Verificar estrutura
check_structure

# Verificar se deve pular limpeza de cache
SKIP_CACHE=false
if [ "${1:-}" = "--skip-cache" ] || [ "${1:-}" = "-s" ]; then
    SKIP_CACHE=true
    echo -e "${YELLOW}⚡ Pulando limpeza de cache (--skip-cache)${NC}"
fi

# Limpar cache antes de iniciar (a menos que seja pulado)
if [ "$SKIP_CACHE" = false ]; then
    clean_cache
else
    echo -e "${BLUE}🧹 Pulando limpeza de cache...${NC}"
fi

# Parar processos existentes e limpar portas
kill_existing

# Verificar/criar configuração
check_config

# Limpar variáveis de ambiente antigas
echo "🧹 Limpando variáveis de ambiente antigas..."
unset DB_HOST DB_PASSWORD DB_USERNAME DB_DATABASE DB_SCHEMA DB_SERVER DB_PORT DB_NAME DB_USER 2>/dev/null || true
echo "✅ Variáveis de ambiente limpas"

# ========================================
# INICIAR BACKEND
# ========================================
echo
echo "=========================================="
echo -e "${BLUE}🔧 INICIANDO BACKEND${NC}"
echo "=========================================="

cd backend

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Ambiente virtual não encontrado!${NC}"
    echo "💡 Criando ambiente virtual..."
    python3 -m venv venv
    echo "📦 Instalando dependências..."
    . venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    . venv/bin/activate
fi

# Verificar se pode importar a aplicação
echo "🔍 Verificando aplicação..."
python3 -c "import app.main" 2>/dev/null || {
    echo -e "${RED}❌ Erro ao carregar aplicação Python${NC}"
    echo "💡 Reinstalando dependências..."
    pip install -r requirements.txt
}

# Iniciar uvicorn em background
echo "🚀 Iniciando servidor FastAPI..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

# Aguardar inicialização
echo "⏳ Aguardando backend inicializar..."
sleep 4

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Backend rodando (PID: $BACKEND_PID)${NC}"
    echo -e "${BLUE}📖 API Docs: http://$HOST_IP:8000/docs${NC}"
else
    echo -e "${RED}❌ Falha ao iniciar backend${NC}"
    echo -e "${RED}Verifique logs em: logs/backend.log${NC}"
    exit 1
fi

cd ..

# ========================================
# INICIAR FRONTEND
# ========================================
echo
echo "=========================================="
echo -e "${BLUE}🎨 INICIANDO FRONTEND${NC}"
echo "=========================================="

# Verificar Node.js
if ! command -v node >/dev/null 2>&1; then
    # Tentar carregar NVM
    if [ -f "$HOME/.nvm/nvm.sh" ]; then
        echo "🔄 Carregando NVM..."
        . "$HOME/.nvm/nvm.sh"
    fi
fi

if ! command -v node >/dev/null 2>&1; then
    echo -e "${RED}⚠️ Node.js não encontrado - apenas backend rodando${NC}"
    echo -e "${BLUE}💡 Instale Node.js 18+: https://nodejs.org/${NC}"
else
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js: $NODE_VERSION${NC}"

    cd frontend

    # Instalar dependências se necessário
    if [ ! -d "node_modules" ]; then
        echo "📦 Instalando dependências do frontend..."
        npm install
    fi

    # Iniciar em background
    echo "🚀 Iniciando servidor Vite..."
    npm run dev -- --host 0.0.0.0 --port 3000 > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid

    # Aguardar inicialização
    echo "⏳ Aguardando frontend inicializar..."
    sleep 5

    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Frontend rodando (PID: $FRONTEND_PID)${NC}"
        echo -e "${BLUE}🎨 Frontend: http://$HOST_IP:3000${NC}"
    else
        echo -e "${RED}⚠️ Frontend pode ter falhado${NC}"
        echo -e "${RED}Verifique logs em: logs/frontend.log${NC}"
    fi

    cd ..
fi

# ========================================
# RESUMO E TESTES
# ========================================
echo
echo "=========================================="
echo -e "${GREEN}🎉 Meu Projeto iniciado!${NC}"
echo "=========================================="
echo
echo -e "${BLUE}🌐 URLS DE ACESSO:${NC}"
echo -e "   Backend API:     http://$HOST_IP:8000"
echo -e "   Documentação:    http://$HOST_IP:8000/docs"
echo -e "   Health Check:    http://$HOST_IP:8000/health"

if [ -f "frontend.pid" ]; then
    echo -e "   Frontend App:    http://$HOST_IP:3000"
fi

echo
echo -e "${BLUE}📊 CONTROLE:${NC}"
echo -e "   Parar serviços:  ./stop.sh"
echo -e "   Logs backend:    tail -f logs/backend.log"
echo -e "   Logs frontend:   tail -f logs/frontend.log"
echo -e "   Início rápido:   ./start.sh --skip-cache"
echo

# ========================================
# TESTAR CONECTIVIDADE
# ========================================
echo "🔬 Testando conectividade dos serviços..."

# Aguardar um pouco mais
sleep 2

# Testar backend
echo "  🔍 Testando backend..."
if command -v curl >/dev/null 2>&1; then
    if curl -s http://$HOST_IP:8000/health >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Backend respondendo${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Backend ainda não está respondendo (aguarde alguns segundos)${NC}"
        echo "  💡 Teste manual: http://$HOST_IP:8000/docs"
    fi
else
    echo "  ℹ️  curl não disponível - teste manual: http://$HOST_IP:8000/docs"
fi

# Testar frontend se disponível
if [ -f "frontend.pid" ]; then
    echo "  🔍 Testando frontend..."
    if command -v curl >/dev/null 2>&1; then
        if curl -s http://$HOST_IP:3000 >/dev/null 2>&1; then
            echo -e "  ${GREEN}✅ Frontend respondendo${NC}"
        else
            echo -e "  ${YELLOW}⚠️  Frontend ainda não está respondendo (aguarde alguns segundos)${NC}"
            echo "  💡 Teste manual: http://$HOST_IP:3000"
        fi
    else
        echo "  ℹ️  curl não disponível - teste manual: http://$HOST_IP:3000"
    fi
fi

echo
echo -e "${YELLOW}⚠️  LEMBRETE IMPORTANTE:${NC}"
echo -e "${YELLOW}   Este projeto usa Database First!${NC}"
echo -e "${YELLOW}   Certifique-se de ter executado os scripts SQL:${NC}"
echo -e "   1. backend/sql_scripts/001_create_users.sql"
echo -e "   2. backend/sql_scripts/002_create_companies.sql"
echo -e "   3. backend/sql_scripts/003_create_initial_data.sql"
echo

echo -e "${GREEN}💡 Pressione Ctrl+C para parar todos os serviços${NC}"
echo

# ========================================
# FUNÇÃO CLEANUP
# ========================================
cleanup() {
    echo
    echo "🔄 Parando serviços..."

    if [ -f backend.pid ]; then
        BACKEND_PID=$(cat backend.pid)
        kill $BACKEND_PID 2>/dev/null || true
        rm backend.pid
        echo "  ✅ Backend parado"
    fi

    if [ -f frontend.pid ]; then
        FRONTEND_PID=$(cat frontend.pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm frontend.pid
        echo "  ✅ Frontend parado"
    fi

    echo -e "${GREEN}✅ Todos os serviços parados!${NC}"
    exit 0
}

# Capturar Ctrl+C
trap cleanup INT TERM

# Manter script rodando
while true; do
    sleep 1
done
