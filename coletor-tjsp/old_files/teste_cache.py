#!/usr/bin/env python3
"""
Teste rápido do sistema de cache
"""
import sys
import os
import time

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from src.cache_manager import CacheManager
from src.config import Config

def teste_cache_basico():
    """Teste básico do sistema de cache"""
    print("=" * 60)
    print("TESTE DO SISTEMA DE CACHE")
    print("=" * 60)

    config = Config()
    cache = CacheManager(config)

    # Teste 1: Cache vazio inicialmente
    print("\n1. Estado inicial do cache:")
    stats = cache.get_stats()
    print(f"   Entradas em memória: {stats['entries_in_memory']}")
    print(f"   Taxa de acerto: {stats['hit_rate']}%")

    # Teste 2: Adicionar dados ao cache
    print("\n2. Adicionando dados ao cache...")
    test_data = {
        'numero': '1234567-89.2024.8.26.0100',
        'status': 'teste_cache',
        'fonte': 'teste'
    }

    cache.set('numero_processo', {'numero': '1234567-89.2024.8.26.0100'}, test_data, 'api_datajud')

    # Verificar se foi adicionado
    stats = cache.get_stats()
    print(f"   Entradas após adição: {stats['entries_in_memory']}")
    print(f"   Dados salvos: {stats['saved']}")

    # Teste 3: Buscar dados no cache (HIT)
    print("\n3. Buscando dados no cache (deve ser HIT)...")
    start_time = time.time()
    cached_result = cache.get('numero_processo', {'numero': '1234567-89.2024.8.26.0100'})
    end_time = time.time()

    if cached_result:
        print("   ✅ Cache HIT!")
        print(f"   Tempo: {(end_time - start_time) * 1000:.3f}ms")
        print(f"   Dados: {cached_result}")
    else:
        print("   ❌ Cache MISS!")

    # Teste 4: Estatísticas finais
    print("\n4. Estatísticas finais:")
    stats = cache.get_stats()
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Taxa de acerto: {stats['hit_rate']}%")
    print(f"   Tamanho total: {stats['total_size_mb']} MB")

    # Teste 5: Buscar dados inexistentes (MISS)
    print("\n5. Buscando dados inexistentes (deve ser MISS)...")
    miss_result = cache.get('numero_processo', {'numero': '9999999-99.2024.8.26.0100'})
    if miss_result is None:
        print("   ✅ Cache MISS correto!")
    else:
        print("   ❌ Cache deveria ter dado MISS!")

    print("\n" + "=" * 60)
    print("TESTE DO CACHE CONCLUÍDO!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        teste_cache_basico()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()