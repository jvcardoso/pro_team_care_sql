# -*- coding: utf-8 -*-
"""
Teste específico para extração de decisões judiciais completas
Foca na captura do texto detalhado das decisões (como SISBAJUD)
"""
import asyncio
import sys
import os
import json

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from src.scraper import TJSPScraper

async def teste_extracao_decisoes():
    """Teste de extração de decisões judiciais completas"""
    print("=" * 100)
    print("TESTE DE EXTRAÇÃO DE DECISÕES JUDICIAIS COMPLETAS")
    print("=" * 100)

    processo_teste = "1028484-65.2019.8.26.0576"

    print(f"🎯 Testando extração de decisões do processo: {processo_teste}")
    print("   Procurando especificamente pela decisão sobre SISBAJUD...")
    print()

    async with TJSPScraper() as scraper:
        print("🔍 Buscando processo via sistema de busca...")

        # Usar busca normal ao invés de URL direta
        dados = await scraper.search_by_process_number(processo_teste)

        if not dados:
            print("❌ Não foi possível extrair dados do processo")
            return False

        print("✅ Dados básicos extraídos")
        print(f"   Vara: {dados.get('vara', 'N/A')}")
        print(f"   Exequente: {dados.get('exequente', 'N/A')}")
        print(f"   Executado: {dados.get('executado', 'N/A')}")
        print()

        # Verificar movimentações
        movimentacoes = dados.get('movimentacoes', [])
        print(f"📄 Movimentações encontradas: {len(movimentacoes)}")

        if not movimentacoes:
            print("⚠️  Nenhuma movimentação encontrada")
            return False

        # Procurar especificamente pela decisão sobre SISBAJUD
        decisao_sisbajud = None
        decisoes_judiciais = []

        print("\n🔍 Analisando movimentações...")
        for idx, mov in enumerate(movimentacoes, 1):
            texto = mov.get('mov_texto', '')
            contem_decisao = mov.get('contem_decisao_judicial', False)

            if contem_decisao:
                decisoes_judiciais.append(mov)
                print(f"   📋 Decisão judicial encontrada: Mov {idx}")

            # Procurar especificamente pela decisão SISBAJUD
            if 'sisbajud' in texto.lower() and 'remetido ao dje' in texto.lower():
                decisao_sisbajud = mov
                print(f"   🎯 DECISÃO SISBAJUD ENCONTRADA: Mov {idx}")
                break

        print()
        print("📊 RESULTADOS DA ANÁLISE:")
        print("-" * 50)
        print(f"   Total de movimentações: {len(movimentacoes)}")
        print(f"   Decisões judiciais identificadas: {len(decisoes_judiciais)}")

        if decisao_sisbajud:
            print("\n🎉 SUCESSO! Decisão SISBAJUD encontrada!")
            print("-" * 50)

            texto_completo = decisao_sisbajud.get('mov_texto_completo', '')
            texto_basico = decisao_sisbajud.get('mov_descricao', '')

            print(f"Data: {decisao_sisbajud.get('mov_data', 'N/A')}")
            print(f"Tipo: {decisao_sisbajud.get('mov_tipo', 'N/A')}")
            print(f"Contém decisão judicial: {decisao_sisbajud.get('contem_decisao_judicial', False)}")
            print()

            print("📝 TEXTO DA DECISÃO:")
            print("-" * 30)

            if texto_completo and len(texto_completo) > len(texto_basico):
                print("✅ Texto completo extraído:")
                print(texto_completo[:500] + "..." if len(texto_completo) > 500 else texto_completo)
            else:
                print("⚠️  Apenas texto básico disponível:")
                print(texto_basico)

            # Verificar se contém os elementos específicos da decisão
            elementos_chave = [
                'SISBAJUD', 'Providencie a Serventia', 'bloqueio de ativos',
                'Relação: 0682/2025', 'Juliano Ventura Cardoso', 'R$40.633,29'
            ]

            print()
            print("🔍 VALIDAÇÃO DO CONTEÚDO:")
            print("-" * 30)

            texto_para_validar = texto_completo or texto_basico
            for elemento in elementos_chave:
                encontrado = elemento.lower() in texto_para_validar.lower()
                status = "✅" if encontrado else "❌"
                print(f"   {status} '{elemento}': {'Encontrado' if encontrado else 'Não encontrado'}")

            # Salvar TODAS as movimentações para demonstrar extração completa
            print()
            print("💾 Salvando TODAS as movimentações do processo...")
            arquivo_todas_mov = f"output/todas_movimentacoes_{processo_teste.replace('-', '_').replace('.', '_')}.json"

            with open(arquivo_todas_mov, 'w', encoding='utf-8') as f:
                json.dump({
                    'processo': processo_teste,
                    'total_movimentacoes': len(movimentacoes),
                    'movimentacoes': movimentacoes,
                    'timestamp_extracao': asyncio.get_event_loop().time(),
                }, f, indent=2, ensure_ascii=False, default=str)

            print(f"✅ TODAS as movimentações salvas em: {arquivo_todas_mov}")

            # Salvar decisão completa
            print()
            print("💾 Salvando decisão SISBAJUD...")
            arquivo_decisao = f"output/decisao_sisbajud_{processo_teste.replace('-', '_').replace('.', '_')}.json"

            with open(arquivo_decisao, 'w', encoding='utf-8') as f:
                json.dump({
                    'processo': processo_teste,
                    'decisao_sisbajud': decisao_sisbajud,
                    'timestamp_extracao': asyncio.get_event_loop().time(),
                    'texto_completo_disponivel': bool(texto_completo and len(texto_completo) > len(texto_basico))
                }, f, indent=2, ensure_ascii=False, default=str)

            print(f"✅ Decisão salva em: {arquivo_decisao}")

            return True

        else:
            print("\n❌ DECISÃO SISBAJUD NÃO ENCONTRADA")
            print("   Possíveis causas:")
            print("   - Processo não contém essa decisão")
            print("   - Problemas na extração do texto completo")
            print("   - Decisão muito recente não indexada")

            # Mostrar algumas decisões encontradas para debug
            if decisoes_judiciais:
                print(f"\n📋 Outras decisões judiciais encontradas ({len(decisoes_judiciais)}):")
                for i, dec in enumerate(decisoes_judiciais[:3], 1):
                    print(f"   {i}. {dec.get('mov_data', 'N/A')}: {dec.get('mov_descricao', 'N/A')[:100]}...")

            return False

if __name__ == "__main__":
    try:
        sucesso = asyncio.run(teste_extracao_decisoes())
        exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        exit(1)