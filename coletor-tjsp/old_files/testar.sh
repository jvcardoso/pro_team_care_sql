#!/bin/bash
# Script simplificado de teste

echo "=========================================="
echo "TESTE DE DIAGNÓSTICO - COLETOR TJSP"
echo "=========================================="
echo ""

cd /home/juliano/Projetos/meu_projeto/coletor-tjsp

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "Execute primeiro:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo "  playwright install chromium"
    exit 1
fi

# Ativar venv
source venv/bin/activate

# Verificar se playwright está instalado
if ! python -c "import playwright" 2>/dev/null; then
    echo "❌ Playwright não instalado!"
    echo "Execute: pip install -r requirements.txt"
    exit 1
fi

echo "✓ Ambiente configurado"
echo ""
echo "Executando teste de conexão..."
echo "(Browser vai abrir - aguarde 10 segundos)"
echo ""

# Executar teste
python test_connection.py

echo ""
echo "=========================================="
echo "TESTE CONCLUÍDO"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Se viu processos → Sistema funcionando!"
echo "2. Se viu CAPTCHA → Execute em outro horário (22h-6h)"
echo "3. Se deu erro → Abra GUIA_DEBUG.md"
echo ""
