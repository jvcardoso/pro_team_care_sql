#!/bin/bash

# Script para limpar cache do projeto
echo "🧹 Limpando cache do Meu Projeto..."

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Cache Python
echo "🐍 Limpando cache Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo "  ✅ Cache Python limpo"

# Cache Node.js
if [ -d "frontend" ]; then
    echo "⚛️  Limpando cache Node.js..."
    cd frontend
    rm -rf .vite 2>/dev/null || true
    rm -rf dist 2>/dev/null || true
    rm -rf node_modules/.cache 2>/dev/null || true
    npm cache clean --force 2>/dev/null || true
    cd ..
    echo "  ✅ Cache Node.js limpo"
fi

# Logs antigos (opcional)
if [ -d "logs" ]; then
    echo "📝 Limpando logs antigos..."
    > logs/backend.log 2>/dev/null || true
    > logs/frontend.log 2>/dev/null || true
    echo "  ✅ Logs limpos"
fi

echo
echo -e "${GREEN}✅ Cache limpo com sucesso!${NC}"
echo -e "${BLUE}💡 Execute ./start.sh para iniciar o projeto${NC}"
