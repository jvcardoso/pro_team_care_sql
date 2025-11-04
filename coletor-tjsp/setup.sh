#!/bin/bash
# Script de setup completo do coletor TJSP

echo "=========================================="
echo "SETUP COMPLETO - COLETOR TJSP"
echo "=========================================="
echo ""

cd /home/juliano/Projetos/meu_projeto/coletor-tjsp

# 1. Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "1. Criando ambiente virtual..."
    python3 -m venv venv
    echo "   ✓ Ambiente virtual criado"
else
    echo "1. ✓ Ambiente virtual já existe"
fi

# 2. Ativar ambiente
echo ""
echo "2. Ativando ambiente virtual..."
source venv/bin/activate
echo "   ✓ Ambiente ativado"

# 3. Atualizar pip
echo ""
echo "3. Atualizando pip..."
pip install --upgrade pip -q
echo "   ✓ Pip atualizado"

# 4. Instalar dependências
echo ""
echo "4. Instalando dependências Python..."
pip install -r requirements.txt -q
echo "   ✓ Dependências instaladas"

# 5. Instalar browser Playwright
echo ""
echo "5. Instalando browser Chromium..."
playwright install chromium
echo "   ✓ Browser instalado"

# 6. Criar arquivo .env
if [ ! -f ".env" ]; then
    echo ""
    echo "6. Criando arquivo .env..."
    cp .env.example .env
    echo "   ✓ Arquivo .env criado"
else
    echo ""
    echo "6. ✓ Arquivo .env já existe"
fi

# 7. Criar diretórios
echo ""
echo "7. Criando diretórios necessários..."
mkdir -p output logs cache input
echo "   ✓ Diretórios criados"

echo ""
echo "=========================================="
echo "✅ SETUP CONCLUÍDO COM SUCESSO!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Ativar ambiente: source venv/bin/activate"
echo "2. Executar teste: python test_connection.py"
echo "3. Validar sistema: ./validar.sh"
echo ""
