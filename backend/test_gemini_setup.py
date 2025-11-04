#!/usr/bin/env python3
"""
Script de teste para verificar se a configuração do Gemini está correta.
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_gemini_configuration():
    """Testa se a configuração do Gemini está correta"""
    print("🔍 Testando configuração do Gemini API...")
    print()

    # Verificar se GEMINI_API_KEY está configurada
    gemini_api_key = os.getenv('GEMINI_API_KEY', '')

    if not gemini_api_key:
        print("❌ GEMINI_API_KEY não configurada no .env")
        print()
        print("📋 Como configurar:")
        print("1. Acesse: https://makersuite.google.com/app/apikey")
        print("2. Faça login com sua conta Google")
        print("3. Clique em 'Create API key'")
        print("4. Copie a chave gerada")
        print("5. Cole no arquivo .env:")
        print("   GEMINI_API_KEY=sua-chave-aqui")
        print()
        return False

    print(f"✅ GEMINI_API_KEY configurada (comprimento: {len(gemini_api_key)})")

    # Verificar se a dependência está instalada
    try:
        import google.generativeai as genai
        print("✅ google-generativeai instalado")
    except ImportError:
        print("❌ google-generativeai não instalado")
        print("   Execute: pip install google-generativeai==0.3.2")
        return False

    # Tentar inicializar o serviço
    try:
        from app.core.config import settings
        from app.services.gemini_service import GeminiService

        print(f"✅ Configurações carregadas (modelo: {settings.GEMINI_MODEL})")

        # Tentar criar instância do serviço
        service = GeminiService()
        print("✅ GeminiService inicializado com sucesso")

        if service.model:
            print(f"✅ Modelo Gemini carregado: {service.model.model_name}")
        else:
            print("❌ Modelo Gemini não carregado")
            return False

    except Exception as e:
        print(f"❌ Erro ao inicializar GeminiService: {e}")
        return False

    print()
    print("🎉 Configuração do Gemini está correta!")
    print("📝 O módulo de atividades agora usa dados reais da IA.")
    print()
    return True

if __name__ == "__main__":
    success = test_gemini_configuration()
    sys.exit(0 if success else 1)