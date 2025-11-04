#!/usr/bin/env python3
"""
Teste do coletor híbrido: API DataJud + Web Scraping
"""
import asyncio
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from src.hybrid_collector import HybridCollector

async def teste_basico_hibrido():
    """Teste básico do coletor híbrido"""
    print("=" * 80)
    print("TESTE DO COLETOR HÍBRIDO")
    print("=" * 80)

    async with HybridCollector() as coletor:
        # Teste 1: Relatório comparativo
        print("\n1. Gerando relatório comparativo...")
        relatorio = await coletor.gerar_relatorio_comparativo("Banco do Brasil")

        print("✅ Relatório gerado!")
        print(f"   API DataJud: {relatorio['comparacao']['api_datajud']['resultados']} resultados")
        print(f"   Web Scraping: {relatorio['comparacao']['web_scraping']['resultados']} resultados")

        # Teste 2: Busca por parte
        print("\n2. Testando busca por parte...")
        processos = await coletor.coletar_por_parte("João Silva", max_resultados=5)

        if processos:
            print(f"✅ Encontrados {len(processos)} processos")
            for i, proc in enumerate(processos[:3], 1):
                print(f"   {i}. {proc.get('numero', 'N/A')} - {proc.get('classe', 'N/A')}")
        else:
            print("⚠️ Nenhum processo encontrado")

        # Teste 3: Busca por números específicos
        print("\n3. Testando busca por números...")
        # Usar números que podem existir ou não
        numeros_teste = [
            "1000032-02.2024.8.26.0100",  # Teste
            "0000001-01.2024.8.26.0001"   # Provavelmente não existe
        ]

        resultados = await coletor.coletar_por_numeros(numeros_teste)

        encontrados = [r for r in resultados if r.get('status') != 'não_encontrado']
        nao_encontrados = [r for r in resultados if r.get('status') == 'não_encontrado']

        print(f"   Processados: {len(resultados)}")
        print(f"   Encontrados: {len(encontrados)}")
        print(f"   Não encontrados: {len(nao_encontrados)}")

        # Salvar resultados
        if resultados:
            print("\n4. Salvando resultados...")
            caminho = await coletor.salvar_resultados(resultados, "teste_hibrido")
            print(f"✅ Resultados salvos em: {caminho}")

    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        asyncio.run(teste_basico_hibrido())
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()