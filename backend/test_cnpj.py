#!/usr/bin/env python3
"""
Test script para CNPJService
"""

import asyncio
import sys
import os

# Adicionar caminho do backend ao sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.cnpj_service import cnpj_service


async def test_cnpj():
    """Testa consulta ReceitaWS com CNPJ conhecido"""
    # CNPJ do Google Brasil (conhecido)
    cnpj = "06990590000123"

    print(f"Testando consulta ReceitaWS para CNPJ: {cnpj}")

    result = await cnpj_service.consult_cnpj(cnpj)

    if result:
        print("✅ Consulta bem-sucedida!")
        print(f"Razão Social: {result.get('nome')}")
        print(f"Fantasia: {result.get('fantasia')}")
        print(f"Situação: {result.get('situacao')}")
        print(f"Município: {result.get('municipio')}")
        print(f"UF: {result.get('uf')}")
        print(f"Atividade Principal: {result.get('atividade_principal_descricao')}")
        print(f"Endereço Completo: {result.get('endereco_completo')}")
        print(f"Metadata: {result.get('_metadata')}")

        # Testar cache
        print("\nTestando cache...")
        result2 = await cnpj_service.consult_cnpj(cnpj)
        if result2:
            print("✅ Cache funcionando!")
        else:
            print("❌ Cache falhou!")

    else:
        print("❌ Consulta falhou!")
        return False

    # Testar CNPJ inválido
    print("\nTestando CNPJ inválido...")
    invalid_result = await cnpj_service.consult_cnpj("99999999999999")
    if invalid_result is None:
        print("✅ CNPJ inválido tratado corretamente!")
    else:
        print("❌ CNPJ inválido não tratado!")

    # Testar CNPJ com formato errado
    print("\nTestando CNPJ com formato errado...")
    wrong_format_result = await cnpj_service.consult_cnpj("123")
    if wrong_format_result is None:
        print("✅ Formato errado tratado corretamente!")
    else:
        print("❌ Formato errado não tratado!")

    # Estatísticas do cache
    stats = cnpj_service.get_cache_stats()
    print(f"\nEstatísticas do cache: {stats}")

    return True


if __name__ == "__main__":
    asyncio.run(test_cnpj())