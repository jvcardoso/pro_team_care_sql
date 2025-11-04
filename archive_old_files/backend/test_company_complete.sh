#!/bin/bash
# Script para testar o cadastro completo de empresa via API

echo "=== TESTE: Cadastro Completo de Empresa ==="
echo ""

# 1. Obter token de autenticação
echo "1. Fazendo login para obter token..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "admin@proteamcare.com.br",
    "password": "admin123"
  }' | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', 'ERROR'))")

if [ "$TOKEN" = "ERROR" ]; then
    echo "❌ ERRO: Falha no login"
    exit 1
fi

echo "✅ Token obtido com sucesso"
echo ""

# 2. Criar empresa completa
echo "2. Criando empresa completa..."

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "http://localhost:8000/api/v1/companies/complete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "access_status": "contract_signed",
    "pj_profile": {
        "name": "Clinica Saúde e Vida LTDA",
        "trade_name": "Clínica Viva Bem",
        "tax_id": "11222333000144",
        "incorporation_date": "2015-08-22",
        "tax_regime": "Simples Nacional",
        "legal_nature": "Sociedade Empresária Limitada",
        "municipal_registration": "987654"
    },
    "addresses": [
        {
            "street": "Rua das Flores",
            "number": "123",
            "details": "Sala 10",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01001000",
            "country": "BR",
            "type": "commercial",
            "is_principal": true
        }
    ],
    "phones": [
        {
            "country_code": "55",
            "number": "1155551234",
            "type": "landline",
            "is_principal": true,
            "is_whatsapp": true,
            "phone_name": "Recepção Principal"
        },
        {
            "country_code": "55",
            "number": "1155555678",
            "type": "mobile",
            "is_principal": false,
            "is_whatsapp": false,
            "phone_name": "Financeiro"
        }
    ],
    "emails": [
        {
            "email_address": "contato@vivabem.com.br",
            "type": "work",
            "is_principal": true
        },
        {
            "email_address": "financeiro@vivabem.com.br",
            "type": "billing",
            "is_principal": false
        }
    ]
  }')

# Separar resposta JSON do status HTTP
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')
HTTP_STATUS=$(echo "$RESPONSE" | tail -1 | cut -d: -f2)

echo "Status HTTP: $HTTP_STATUS"
echo "Resposta:"
echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"

echo ""
if [ "$HTTP_STATUS" = "201" ]; then
    echo "✅ SUCESSO: Empresa criada com sucesso!"
    echo ""
    echo "=== VERIFICAÇÃO: Consultando empresa criada ==="

    # Extrair IDs da resposta
    COMPANY_ID=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('new_company_id', ''))")
    PERSON_ID=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('new_person_id', ''))")

    if [ -n "$COMPANY_ID" ]; then
        echo "Verificando Company ID: $COMPANY_ID"
        curl -s -X GET "http://localhost:8000/api/v1/companies/$COMPANY_ID" \
          -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
    fi

    if [ -n "$PERSON_ID" ]; then
        echo ""
        echo "Verificando Person ID: $PERSON_ID"
        curl -s -X GET "http://localhost:8000/api/v1/people/$PERSON_ID" \
          -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
    fi
else
    echo "❌ FALHA: Erro ao criar empresa"
fi
