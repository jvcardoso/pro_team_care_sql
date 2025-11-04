#!/bin/bash

# Script para executar testes automatizados
# Uso: ./run_tests.sh [opções]

set -e

echo "🚀 Executando testes automatizados..."

# Verificar se estamos no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Execute este script do diretório backend/"
    exit 1
fi

# Ativar virtual environment se existir
if [ -d "venv" ]; then
    echo "📦 Ativando virtual environment..."
    source venv/bin/activate
fi

    # Instalar dependências se necessário
    if ! python -c "import pytest, httpx, pytest_mock" 2>/dev/null; then
        echo "📦 Instalando dependências de teste..."
        pip install pytest pytest-asyncio httpx pytest-cov pytest-mock
    fi

# Executar testes
echo "🧪 Executando testes..."
if [ "$1" = "--coverage" ]; then
    pytest --cov=app --cov-report=html --cov-report=term-missing
elif [ "$1" = "--verbose" ]; then
    pytest -v
else
    pytest
fi

echo "✅ Testes concluídos!"