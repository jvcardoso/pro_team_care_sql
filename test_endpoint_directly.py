#!/usr/bin/env python3
"""
Test script to verify the cards endpoint directly
"""
import requests
import json

# Configurações
BASE_URL = "http://192.168.11.83:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBwcm90ZWFtY2FyZS5jb20uYnIiLCJleHAiOjE3MzA4MzY4MDB9.example_token"  # Substitua por um token real

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(url, description):
    """Testa um endpoint específico"""
    print(f"\n🔍 Testando: {description}")
    print(f"URL: {url}")

    try:
        response = requests.get(url, headers=HEADERS)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"Resultado: Array com {len(data)} items")
                if len(data) > 0:
                    print("Primeiro item:", json.dumps(data[0], indent=2, default=str)[:200] + "...")
                else:
                    print("Array vazio - Nenhum card encontrado")
            else:
                print(f"Resultado: {json.dumps(data, indent=2)[:300]}...")
        else:
            print(f"Erro: {response.text}")

    except Exception as e:
        print(f"Erro de conexão: {e}")

def main():
    print("🚀 Testando endpoint /api/v1/kanban/cards diretamente")

    # Teste 1: Período atual (últimos 30 dias)
    test_endpoint(
        f"{BASE_URL}/api/v1/kanban/cards?completed_from=2025-10-06&completed_to=2025-11-05&column_ids=1,2,3,4,5",
        "Período atual (2025-10-06 até 2025-11-05)"
    )

    # Teste 2: Ano inteiro
    test_endpoint(
        f"{BASE_URL}/api/v1/kanban/cards?completed_from=2025-01-01&completed_to=2025-12-31&column_ids=1,2,3,4,5",
        "Ano inteiro (2025-01-01 até 2025-12-31)"
    )

    # Teste 3: Apenas coluna "Concluído"
    test_endpoint(
        f"{BASE_URL}/api/v1/kanban/cards?completed_from=2025-01-01&completed_to=2025-12-31&column_ids=5",
        "Apenas coluna Concluído (ano inteiro)"
    )

    # Teste 4: Sem filtro de data (todos os cards concluídos)
    test_endpoint(
        f"{BASE_URL}/api/v1/kanban/cards?column_ids=1,2,3,4,5",
        "Todos os cards (sem filtro de data)"
    )

    # Teste 5: Verificar colunas disponíveis
    test_endpoint(
        f"{BASE_URL}/api/v1/kanban/columns",
        "Colunas disponíveis"
    )

if __name__ == "__main__":
    main()