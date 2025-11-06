#!/usr/bin/env python3
"""
Script para testar se o backend está funcionando
"""

import requests
import sys

def test_backend():
    """Testa se o backend está respondendo"""
    try:
        # Testar endpoint de teste
        response = requests.get("http://localhost:8000/api/v1/kanban/test-import")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")

        # Testar se o endpoint de import existe
        response2 = requests.get("http://localhost:8000/docs")
        if response2.status_code == 200:
            print("✅ Documentação da API acessível")
        else:
            print("❌ Documentação da API não acessível")

    except Exception as e:
        print(f"❌ Erro ao conectar com backend: {e}")
        print("Verifique se o backend está rodando na porta 8000")

if __name__ == "__main__":
    test_backend()