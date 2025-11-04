#!/bin/bash
# Script de validação das correções

echo "=========================================="
echo "VALIDAÇÃO DAS CORREÇÕES - COLETOR TJSP"
echo "=========================================="
echo ""

cd /home/juliano/Projetos/meu_projeto/coletor-tjsp

# Verificar ambiente
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "Execute: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Ativar venv
source venv/bin/activate

echo "✓ Ambiente ativado"
echo ""
echo "Executando testes de validação..."
echo "(Isso pode levar 1-2 minutos)"
echo ""

# Executar teste
python test_correcao.py

echo ""
echo "=========================================="
echo "VALIDAÇÃO CONCLUÍDA"
echo "=========================================="
echo ""
echo "Se os testes passaram:"
echo "  → Sistema está funcionando!"
echo "  → Execute: python run.py --search-party 'Rio Nieva' --output output/"
echo ""
echo "Se os testes falharam:"
echo "  → Verifique ANALISE_SENIOR.md"
echo "  → Execute em outro horário (22h-6h)"
echo "  → Pode haver CAPTCHA bloqueando"
echo ""
