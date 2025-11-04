#!/usr/bin/env python3
"""
Test script para GeocodingService
"""

import asyncio
import sys
import os

# Adicionar caminho do backend ao sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.geocoding_service import geocoding_service


async def test_geocoding():
    """Testa geocoding com endereço conhecido"""
    address = "Praça da Sé, São Paulo, SP"

    print(f"Testando geocoding para endereço: {address}")

    result = await geocoding_service.geocode_address(address)

    if result:
        print("✅ Geocoding bem-sucedido!")
        print(f"Latitude: {result.get('latitude')}")
        print(f"Longitude: {result.get('longitude')}")
        print(f"Display Name: {result.get('display_name')}")
        print(f"Tipo: {result.get('type')}")
        print(f"Importância: {result.get('importance')}")
        print(f"Metadata: {result.get('_metadata')}")

        # Testar cache
        print("\nTestando cache...")
        result2 = await geocoding_service.geocode_address(address)
        if result2:
            print("✅ Cache funcionando!")
        else:
            print("❌ Cache falhou!")

        # Testar reverse geocoding
        print("\nTestando reverse geocoding...")
        lat, lng = result['latitude'], result['longitude']
        reverse_result = await geocoding_service.reverse_geocode(lat, lng)
        if reverse_result:
            print("✅ Reverse geocoding bem-sucedido!")
            print(f"Endereço reverso: {reverse_result.get('display_name')}")
        else:
            print("❌ Reverse geocoding falhou!")

    else:
        print("❌ Geocoding falhou!")
        return False

    # Testar endereço vazio
    print("\nTestando endereço vazio...")
    empty_result = await geocoding_service.geocode_address("")
    if empty_result is None:
        print("✅ Endereço vazio tratado corretamente!")
    else:
        print("❌ Endereço vazio não tratado!")

    # Estatísticas do cache
    stats = geocoding_service.get_cache_stats()
    print(f"\nEstatísticas do cache: {stats}")

    return True


if __name__ == "__main__":
    asyncio.run(test_geocoding())