#!/usr/bin/env python3
"""
Teste simples para plano gratuito do Gemini API.
"""
import asyncio
import time

async def test_free_tier():
    """Testa uso básico no plano gratuito"""
    print("🆓 Testando Gemini API - Plano Gratuito")
    print("=" * 50)

    try:
        from app.services.gemini_service import gemini_service

        print("✅ Serviço Gemini inicializado")

        # Teste simples
        print("\n🔍 Testando análise básica...")
        start_time = time.time()

        result = await gemini_service.analyze_activity(
            title="Reunião SAP",
            status="Pendente",
            raw_text="João Silva solicitou reunião sobre implementação SAP com Maria Santos"
        )

        elapsed = time.time() - start_time

        print(".2f")
        print(f"📊 Resultados:")
        print(f"   👥 Pessoas: {result.get('pessoas', [])}")
        print(f"   💻 Sistemas: {result.get('sistemas', [])}")
        print(f"   🏷️ Tags: {result.get('tags', [])}")
        print(f"   📋 Pendências: {len(result.get('pendencias', []))}")

        print("\n✅ SUCESSO! IA funcionando no plano gratuito!")

    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            print("❌ QUOTA EXCEDIDA - Plano Gratuito")
            print("💡 Soluções:")
            print("   • Aguarde alguns minutos")
            print("   • Use textos mais curtos")
            print("   • Evite requests frequentes")
            print("   • Considere upgrade para plano pago")
        else:
            print(f"❌ Erro: {error_str}")

    print("\n" + "=" * 50)
    print("💡 DICAS PARA PLANO GRATUITO:")
    print("• Máximo ~60 requests/minuto")
    print("• Quota diária limitada")
    print("• Use cache (mesmas entradas)")
    print("• Textos curtos (< 1000 chars)")
    print("• Evite picos de uso")

if __name__ == "__main__":
    asyncio.run(test_free_tier())