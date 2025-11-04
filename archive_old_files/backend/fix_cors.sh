#!/bin/bash
# Script para corrigir configuração de CORS

echo "=== CORREÇÃO DE CORS ==="
echo ""

ENV_FILE="/home/juliano/Projetos/meu_projeto/backend/.env"

# Verificar se arquivo existe
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Arquivo .env não encontrado: $ENV_FILE"
    exit 1
fi

# Fazer backup
echo "📦 Criando backup do .env..."
cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ Backup criado: $ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
echo ""

# Atualizar CORS_ORIGINS
echo "🔧 Atualizando CORS_ORIGINS..."
sed -i 's|CORS_ORIGINS=.*|CORS_ORIGINS=http://localhost:3000,http://192.168.11.83:3000,http://127.0.0.1:3000,http://localhost:5173|' "$ENV_FILE"

# Verificar se funcionou
if grep -q "192.168.11.83:3000" "$ENV_FILE"; then
    echo "✅ CORS_ORIGINS atualizado com sucesso!"
    echo ""
    echo "Nova configuração:"
    grep CORS_ORIGINS "$ENV_FILE"
    echo ""
    echo "⚠️  IMPORTANTE: Reinicie o servidor FastAPI para aplicar as mudanças!"
    echo ""
    echo "Para reiniciar:"
    echo "  1. Pare o servidor (Ctrl+C)"
    echo "  2. Execute: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
else
    echo "❌ Erro ao atualizar .env"
    exit 1
fi
