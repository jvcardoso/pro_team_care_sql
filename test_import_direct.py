#!/usr/bin/env python3
"""
Teste direto da importação BusinessMap
"""

import requests
import os

def test_import():
    """Testa a importação diretamente"""

    # URL do backend
    url = "http://localhost:8000/api/v1/kanban/import-bm"

    # Arquivo CSV
    csv_file = "test_import.csv"

    if not os.path.exists(csv_file):
        print(f"❌ Arquivo {csv_file} não encontrado")
        return

    # Token (se existir)
    token = None
    try:
        # Tentar ler token do localStorage simulado
        pass
    except:
        pass

    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    print(f"📤 Enviando arquivo {csv_file} para {url}")

    try:
        with open(csv_file, 'rb') as f:
            files = {'file': (csv_file, f, 'text/csv')}
            response = requests.post(url, files=files, headers=headers)

        print(f"📥 Status: {response.status_code}")
        print(f"📥 Resposta: {response.text}")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_import()