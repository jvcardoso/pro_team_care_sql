#!/usr/bin/env python3
"""
Teste de consulta de processo específico
"""
import asyncio
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from src.hybrid_collector import HybridCollector

async def consultar_processo_especifico():
    """Consulta um processo específico"""
    print("=" * 80)
    print("CONSULTA DE PROCESSO ESPECÍFICO")
    print("=" * 80)

    # Processo fornecido pelo usuário
    numero_processo = "1028484-65.2019.8.26.0576"

    print(f"🔍 Consultando processo: {numero_processo}")
    print()

    async with HybridCollector() as coletor:
        # Consultar apenas este processo
        resultados = await coletor.coletar_por_numeros([numero_processo])

        if resultados:
            resultado = resultados[0]

            print("📋 RESULTADO DA CONSULTA:")
            print("-" * 50)

            if resultado.get('status') == 'não_encontrado':
                print("❌ Processo não encontrado em nenhuma fonte")
                print(f"   Número: {resultado.get('numero')}")
                print(f"   Status: {resultado.get('status')}")
                print(f"   Fonte: {resultado.get('fonte')}")

            elif resultado.get('status') == 'erro':
                print("❌ Erro na consulta")
                print(f"   Número: {resultado.get('numero')}")
                print(f"   Erro: {resultado.get('erro')}")
                print(f"   Fonte: {resultado.get('fonte')}")

            else:
                print("✅ Processo encontrado!")
                print(f"   Número: {resultado.get('numero', 'N/A')}")
                print(f"   Status: {resultado.get('status', 'N/A')}")
                print(f"   Fonte: {resultado.get('fonte', 'N/A')}")

                # Mostrar dados principais se disponíveis
                if 'classe' in resultado:
                    print(f"   Classe: {resultado.get('classe', 'N/A')}")
                if 'assunto' in resultado:
                    print(f"   Assunto: {resultado.get('assunto', 'N/A')}")
                if 'juiz' in resultado:
                    print(f"   Juiz: {resultado.get('juiz', 'N/A')}")
                if 'vara' in resultado:
                    print(f"   Vara: {resultado.get('vara', 'N/A')}")

                # Mostrar partes se disponíveis
                if 'partes' in resultado and resultado['partes']:
                    print("   Partes:")
                    for parte in resultado['partes'][:3]:  # Máximo 3 partes
                        tipo = parte.get('tipo', 'N/A')
                        nome = parte.get('nome', 'N/A')
                        print(f"     - {tipo}: {nome}")

                # Data de distribuição
                if 'data_distribuicao' in resultado:
                    print(f"   Data distribuição: {resultado.get('data_distribuicao', 'N/A')}")

            print()
            print("💾 Salvando resultado...")

            # Salvar resultado
            caminho = await coletor.salvar_resultados(resultados, f"processo_{numero_processo.replace('-', '_').replace('.', '_')}")
            print(f"✅ Resultado salvo em: {caminho}")

        else:
            print("❌ Nenhum resultado retornado")

    print("\n" + "=" * 80)
    print("CONSULTA CONCLUÍDA")
    print("=" * 80)

if __name__ == "__main__":
    try:
        asyncio.run(consultar_processo_especifico())
    except KeyboardInterrupt:
        print("\n\nConsulta interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()