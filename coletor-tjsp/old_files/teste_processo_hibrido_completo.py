#!/usr/bin/env python3
"""
Teste completo do coletor híbrido com enriquecimento de dados
Usa o processo 1028484-65.2019.8.26.0576 como teste de referência
"""
import asyncio
import sys
import os
import json

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from src.hybrid_collector import HybridCollector

async def teste_hibrido_completo():
    """Teste completo do coletor híbrido com enriquecimento"""
    print("=" * 100)
    print("TESTE COMPLETO - COLETOR HÍBRIDO COM ENRIQUECIMENTO")
    print("=" * 100)

    # Processo de teste (com dados de referência conhecidos)
    processo_teste = "1028484-65.2019.8.26.0576"

    print(f"🎯 Testando processo: {processo_teste}")
    print()

    # Dados esperados (baseado no exemplo fornecido)
    dados_esperados = {
        'numero': '1028484-65.2019.8.26.0576',
        'classe': 'Execução de Título Extrajudicial',
        'assunto': 'Despesas Condominiais',
        'vara': '1ª Vara Cível',
        'comarca': 'São José do Rio Preto',
        'partes': {
            'exequente': 'Parque Rio Nieva',
            'executado': 'Juliano Ventura Cardoso',
            'terceiro_interessado': 'Banco do Brasil S/A',
            'gestora': 'Alethea Carvalho Lopes'
        },
        'advogados': {
            'exequente': {
                'nome': 'Adilson Lopes Teixeira',
                'oab': '357725/SP'
            },
            'banco_brasil': {
                'nome': 'Darcio Jose da Mota',
                'oab': '67669/SP'
            }
        }
    }

    async with HybridCollector() as coletor:
        # Limpar cache para forçar nova busca e teste de enriquecimento
        print("🧹 Limpando cache para teste completo...")
        coletor.cache.invalidate('numero_processo', {'numero': processo_teste})
        print("✅ Cache limpo")
        print()

        print("🔍 Iniciando coleta híbrida...")
        print("   1. Busca via API DataJud")
        print("   2. Enriquecimento via Web Scraping")
        print("   3. Mesclagem de dados")
        print()

        # Coletar dados
        resultados = await coletor.coletar_por_numeros([processo_teste])

        if not resultados:
            print("❌ Nenhum resultado retornado")
            return False

        resultado = resultados[0]

        print("📋 RESULTADO OBTIDO:")
        print("-" * 80)

        # Verificar se encontrou o processo
        if resultado.get('status') in ['não_encontrado', 'erro']:
            print(f"❌ Processo não encontrado: {resultado.get('status')}")
            if 'erro' in resultado:
                print(f"   Erro: {resultado['erro']}")
            return False

        # Análise dos dados obtidos
        print("✅ Processo encontrado!")

        # Dados básicos
        print(f"   📄 Número: {resultado.get('numero_formatado', resultado.get('numero', 'N/A'))}")
        print(f"   🏛️  Classe: {resultado.get('classe', 'N/A')}")
        print(f"   📋 Assunto: {resultado.get('assuntos', [{}])[0].get('nome', 'N/A') if resultado.get('assuntos') else 'N/A'}")
        print(f"   ⚖️  Órgão: {resultado.get('orgao_julgador', 'N/A')}")
        print(f"   📅 Data Ajuizamento: {resultado.get('data_ajuizamento', 'N/A')[:10] if resultado.get('data_ajuizamento') else 'N/A'}")
        print(f"   🔄 Movimentações: {resultado.get('quantidade_movimentacoes', 'N/A')}")
        print(f"   🎯 Fonte: {resultado.get('fonte', 'N/A')}")

        # Verificar enriquecimento
        dados_complementares = resultado.get('dados_complementares', {})
        partes = resultado.get('partes', {})
        advogados = resultado.get('advogados', {})

        print()
        print("🔍 DADOS COMPLEMENTARES (WEB SCRAPING):")
        print("-" * 50)

        if dados_complementares:
            print(f"   ✅ Vara detalhada: {dados_complementares.get('vara_detalhada', 'N/A')}")
            print(f"   ✅ Situação: {dados_complementares.get('situacao', 'N/A')}")
            print(f"   ✅ Valor causa: {dados_complementares.get('valor_causa_formatado', 'N/A')}")
        else:
            print("   ⚠️  Dados complementares não disponíveis")

        print()
        print("👥 PARTES DO PROCESSO:")
        print("-" * 30)

        if partes:
            if 'exequente' in partes:
                print(f"   ✅ Exequente: {partes['exequente']}")
            else:
                print("   ❌ Exequente não identificado")

            if 'executado' in partes:
                print(f"   ✅ Executado: {partes['executado']}")
            else:
                print("   ❌ Executado não identificado")
        else:
            print("   ⚠️  Partes não disponíveis")

        print()
        print("⚖️  ADVOGADOS:")
        print("-" * 20)

        if advogados:
            if 'autor' in advogados:
                adv_autor = advogados['autor']
                print(f"   ✅ Adv. Exequente: {adv_autor.get('nome', 'N/A')} - OAB: {adv_autor.get('oab', 'N/A')}")
            else:
                print("   ❌ Advogado do exequente não identificado")

            if 'reu' in advogados:
                adv_reu = advogados['reu']
                print(f"   ✅ Adv. Executado: {adv_reu.get('nome', 'N/A')} - OAB: {adv_reu.get('oab', 'N/A')}")
            else:
                print("   ❌ Advogado do executado não identificado")
        else:
            print("   ⚠️  Advogados não disponíveis")

        # Comparação com dados esperados
        print()
        print("🎯 VALIDAÇÃO COM DADOS DE REFERÊNCIA:")
        print("-" * 50)

        validacoes = []

        # Classe
        classe_api = resultado.get('classe', '')
        classe_esperada = dados_esperados['classe']
        if classe_esperada.lower() in classe_api.lower():
            validacoes.append(("✅ Classe", f"Correta: {classe_api}"))
        else:
            validacoes.append(("❌ Classe", f"Esperada: {classe_esperada}, Obtida: {classe_api}"))

        # Assunto
        assuntos_api = resultado.get('assuntos', [])
        assunto_api = assuntos_api[0].get('nome', '') if assuntos_api else ''
        assunto_esperado = dados_esperados['assunto']
        if assunto_esperado.lower() in assunto_api.lower():
            validacoes.append(("✅ Assunto", f"Correto: {assunto_api}"))
        else:
            validacoes.append(("❌ Assunto", f"Esperado: {assunto_esperado}, Obtido: {assunto_api}"))

        # Partes
        exequente_api = partes.get('exequente', '')
        exequente_esperado = dados_esperados['partes']['exequente']
        if exequente_esperado.lower() in exequente_api.lower():
            validacoes.append(("✅ Exequente", f"Correto: {exequente_api}"))
        else:
            validacoes.append(("❌ Exequente", f"Esperado: {exequente_esperado}, Obtido: {exequente_api}"))

        executado_api = partes.get('executado', '')
        executado_esperado = dados_esperados['partes']['executado']
        if executado_esperado.lower() in executado_api.lower():
            validacoes.append(("✅ Executado", f"Correto: {executado_api}"))
        else:
            validacoes.append(("❌ Executado", f"Esperado: {executado_esperado}, Obtido: {executado_api}"))

        # Advogados
        adv_autor_api = advogados.get('autor', {}).get('nome', '')
        adv_autor_esperado = dados_esperados['advogados']['exequente']['nome']
        if adv_autor_esperado.lower() in adv_autor_api.lower():
            validacoes.append(("✅ Adv. Exequente", f"Correto: {adv_autor_api}"))
        else:
            validacoes.append(("❌ Adv. Exequente", f"Esperado: {adv_autor_esperado}, Obtido: {adv_autor_api}"))

        for validacao in validacoes:
            print(f"   {validacao[0]} {validacao[1]}")

        # Salvar resultado completo
        print()
        print("💾 Salvando resultado completo...")
        caminho = await coletor.salvar_resultados(resultados, f"processo_hibrido_completo_{processo_teste.replace('-', '_').replace('.', '_')}")
        print(f"✅ Resultado salvo em: {caminho}")

        # Estatísticas do cache
        print()
        print("📊 ESTATÍSTICAS DO CACHE:")
        print("-" * 30)
        cache_stats = coletor.cache.get_stats()
        print(f"   Entradas: {cache_stats['entries_in_memory']}")
        print(f"   Hits: {cache_stats['hits']}")
        print(f"   Misses: {cache_stats['misses']}")
        print(".1f")

    print()
    print("=" * 100)
    print("TESTE CONCLUÍDO!")
    print("=" * 100)

    # Verificar se conseguiu enriquecer os dados
    sucesso = bool(partes and advogados)
    if sucesso:
        print("🎉 SUCESSO: Dados da API enriquecidos com partes do processo!")
    else:
        print("⚠️  PARCIAL: Dados básicos obtidos, mas enriquecimento incompleto")

    return sucesso

if __name__ == "__main__":
    try:
        sucesso = asyncio.run(teste_hibrido_completo())
        exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        exit(1)