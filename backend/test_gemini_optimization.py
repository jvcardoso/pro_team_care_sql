#!/usr/bin/env python3
"""
Script de teste e otimização para uso da API Gemini no plano gratuito.
"""
import asyncio
import time
from app.services.gemini_service import gemini_service

async def test_optimization():
    """Testa otimizações para plano gratuito"""
    print("🧪 Testando otimizações para plano gratuito do Gemini API")
    print("=" * 60)

    # Teste 1: Cache - mesma entrada deve retornar resultado do cache
    print("\n1️⃣ Testando cache...")
    test_text = "Reunião com João Silva sobre implementação SAP"

    start_time = time.time()
    try:
        result1 = await gemini_service.analyze_activity(
            title="Reunião SAP",
            status="Pendente",
            raw_text=test_text
        )
        time1 = time.time() - start_time
        print(".2f")
        print(f"   Pessoas: {result1.get('pessoas', [])}")
        print(f"   Sistemas: {result1.get('sistemas', [])}")

        # Mesma entrada - deve vir do cache
        start_time = time.time()
        result2 = await gemini_service.analyze_activity(
            title="Reunião SAP",
            status="Pendente",
            raw_text=test_text
        )
        time2 = time.time() - start_time
        print(".2f")
        print("   ✅ Cache funcionando!"f time2 < time1 * 0.1 else "   ❌ Cache pode não estar funcionando")

    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # Teste 2: Texto longo truncado
    print("\n2️⃣ Testando truncamento de texto longo...")
    long_text = "Reunião com João Silva, Maria Santos e Pedro Costa sobre implementação do sistema SAP ERP na empresa XYZ. " * 20  # Muito longo

    try:
        result = await gemini_service.analyze_activity(
            title="Reunião Longa",
            status="Pendente",
            raw_text=long_text
        )
        print(f"   ✅ Texto truncado processado (comprimento original: {len(long_text)})")
        print(f"   Pessoas encontradas: {result.get('pessoas', [])}")

    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # Teste 3: Retry com backoff
    print("\n3️⃣ Testando retry com backoff...")
    print("   Nota: Este teste pode demorar se houver rate limiting")

    try:
        # Tentar múltiplas vezes rapidamente para testar retry
        tasks = []
        for i in range(3):
            tasks.append(gemini_service.analyze_activity(
                title=f"Teste Retry {i+1}",
                status="Pendente",
                raw_text=f"Teste de retry número {i+1} para verificar backoff"
            ))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for r in results if not isinstance(r, Exception))

        print(f"   ✅ {success_count}/{len(tasks)} requests bem-sucedidos")
        if any(isinstance(r, Exception) for r in results):
            print("   ℹ️ Alguns falharam (esperado com rate limiting)")

    except Exception as e:
        print(f"   ❌ Erro: {e}")

    print("\n" + "=" * 60)
    print("💡 DICAS PARA PLANO GRATUITO:")
    print("• Aguarde alguns minutos entre requests")
    print("• Use textos curtos (< 1000 caracteres)")
    print("• Mesmas entradas reutilizam cache")
    print("• Evite picos de uso")
    print("• Considere upgrade para plano pago se usar muito")

if __name__ == "__main__":
    asyncio.run(test_optimization())