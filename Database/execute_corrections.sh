#!/bin/bash
# Script para executar as correções no banco de dados

echo "=== Executando Correções no Banco de Dados ==="
echo ""

# Configurações do banco
SERVER="192.168.11.84"
DATABASE="pro_team_care"
USERNAME="sa"
# Senha será solicitada

echo "Servidor: $SERVER"
echo "Database: $DATABASE"
echo "Usuário: $USERNAME"
echo ""

# Solicitar senha
read -sp "Digite a senha do SQL Server: " PASSWORD
echo ""
echo ""

# Caminho dos scripts
SCRIPT_DIR="/home/juliano/Projetos/meu_projeto/Database"

# 1. Executar Stored Procedure
echo "1/2: Executando Stored Procedure (022_Create_Company_From_JSON.sql)..."
sqlcmd -S "$SERVER" -d "$DATABASE" -U "$USERNAME" -P "$PASSWORD" -i "$SCRIPT_DIR/022_Create_Company_From_JSON.sql"

if [ $? -eq 0 ]; then
    echo "✅ Stored Procedure executada com sucesso!"
else
    echo "❌ Erro ao executar Stored Procedure"
    exit 1
fi

echo ""

# 2. Executar View
echo "2/2: Executando View (023_Create_Complete_Company_View.sql)..."
sqlcmd -S "$SERVER" -d "$DATABASE" -U "$USERNAME" -P "$PASSWORD" -i "$SCRIPT_DIR/023_Create_Complete_Company_View.sql"

if [ $? -eq 0 ]; then
    echo "✅ View executada com sucesso!"
else
    echo "❌ Erro ao executar View"
    exit 1
fi

echo ""
echo "=== ✅ TODAS AS CORREÇÕES FORAM APLICADAS COM SUCESSO! ==="
echo ""
echo "Próximos passos:"
echo "1. Testar criação de empresa: ./test_company_complete.sh"
echo "2. Testar listagem: curl GET /api/v1/companies/complete-list"
