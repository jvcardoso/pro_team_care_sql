#!/usr/bin/env python3
"""
Teste simples para verificar se a nova Stored Procedure funciona no endpoint.
"""
import requests
import json

def test_analytics_cards_endpoint():
    """Testa o endpoint /api/v1/kanban/analytics/cards-in-period"""

    # URL do backend
    base_url = "http://192.168.11.83:8000"

    # Primeiro, fazer login para obter token
    login_data = {
        "email_address": "admin@proteamcare.com.br",
        "password": "admin123"
    }

    try:
        # Login
        login_response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
        login_response.raise_for_status()

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        print("✅ Login realizado com sucesso!")

        # Testar endpoint de analytics cards
        params = {
            "start_date": "2025-01-01",
            "end_date": "2025-11-30"
        }

        response = requests.get(
            f"{base_url}/api/v1/kanban/analytics/cards-in-period",
            headers=headers,
            params=params
        )

        print(f"📊 Status da resposta: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! Retornou {len(data)} cards.")
            if data:
                print(f"📋 Primeiro card: {data[0]['Title']}")
                print(f"📅 Concluído em: {data[0]['CompletedDate']}")
        else:
            print(f"❌ Erro: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_analytics_cards_endpoint()