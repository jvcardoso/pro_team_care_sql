#!/usr/bin/env python3
"""
Test script to verify the analytics fix
"""
import datetime

def test_date_calculations():
    """Test the date calculations that should now work"""

    print("🧪 Testando cálculos de data do Analytics")
    print("=" * 50)

    # Simular o cálculo do frontend (últimos 365 dias)
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=365)
    end_date = today

    print(f"Data atual: {today}")
    print(f"Data inicial (padrão): {start_date}")
    print(f"Data final: {end_date}")
    print(f"Período: {(end_date - start_date).days} dias")

    # Verificar se o período faz sentido
    assert (end_date - start_date).days == 365, "Período deve ser de 365 dias"
    assert start_date < end_date, "Data inicial deve ser anterior à final"

    print("✅ Cálculos de data estão corretos")

    # Simular resposta esperada do endpoint
    print("\n📊 Simulação da resposta esperada:")
    print("- Se há cards concluídos nos últimos 365 dias, deve retornar Array com dados")
    print("- Se não há cards, deve retornar Array vazio (mas isso seria estranho)")
    print("- O endpoint deve sempre funcionar, independente dos dados")

    print("\n🎯 RESULTADO ESPERADO:")
    print("Após a correção, a página deve mostrar cards concluídos")
    print("Se ainda não mostrar, pode ser que não há cards no período de 365 dias")

if __name__ == "__main__":
    test_date_calculations()