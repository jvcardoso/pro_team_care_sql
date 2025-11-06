#!/usr/bin/env python3
"""
Test script to verify the analytics endpoint is working
"""
import requests
import json

# Configurações
BASE_URL = "http://192.168.11.83:8000"

def get_token():
    """Obtém token JWT válido"""
    login_data = {
        "email_address": "admin@proteamcare.com.br",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login falhou: {response.text}")

def test_analytics_endpoint():
    """Testa o endpoint de analytics"""
    try:
        token = get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = f"{BASE_URL}/api/v1/kanban/analytics?start_date=2025-10-07&end_date=2025-11-06"
        print(f"🧪 Testando endpoint: {url}")

        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics funcionando!")
            print(f"Resposta: {json.dumps(data, indent=2)[:500]}...")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")

    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def test_cards_endpoint():
    """Testa o endpoint de cards"""
    try:
        token = get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = f"{BASE_URL}/api/v1/kanban/cards?completed_from=2025-10-07&completed_to=2025-11-06&column_ids=1,2,3,4,5"
        print(f"\n🧪 Testando endpoint: {url}")

        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cards endpoint funcionando! Retornou {len(data)} cards")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")

    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    test_analytics_endpoint()
    test_cards_endpoint()