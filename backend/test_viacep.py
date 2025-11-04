#!/usr/bin/env python3
"""
Test script para AddressEnrichmentService
"""

import asyncio
import sys
import os

# Adicionar caminho do backend ao sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.address_enrichment_service import address_enrichment_service


async def test_viacep():
    """Testa consulta ViaCEP com CEP conhecido"""
    cep = "01001000"  # Praça da Sé, São Paulo

    print(f"Testando consulta ViaCEP para CEP: {cep}")

    result = await address_enrichment_service.consult_viacep(cep)

    if result:
        print("✅ Consulta bem-sucedida!")
        print(f"Logradouro: {result.get('logradouro')}")
        print(f"Bairro: {result.get('bairro')}")
        print(f"Cidade: {result.get('localidade')}")
        print(f"UF: {result.get('uf')}")
        print(f"IBGE Estado: {result.get('ibge_state_code')}")
        print(f"Metadata: {result.get('_metadata')}")

        # Testar cache
        print("\nTestando cache...")
        result2 = await address_enrichment_service.consult_viacep(cep)
        if result2:
            print("✅ Cache funcionando!")
        else:
            print("❌ Cache falhou!")

    else:
        print("❌ Consulta falhou!")
        return False

    # Testar CEP inválido
    print("\nTestando CEP inválido...")
    invalid_result = await address_enrichment_service.consult_viacep("99999999")
    if invalid_result is None:
        print("✅ CEP inválido tratado corretamente!")
    else:
        print("❌ CEP inválido não tratado!")

    # Estatísticas do cache
    stats = address_enrichment_service.get_cache_stats()
    print(f"\nEstatísticas do cache: {stats}")

    return True


if __name__ == "__main__":
    asyncio.run(test_viacep())