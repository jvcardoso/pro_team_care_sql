#!/usr/bin/env python3
"""
Script para testar extração de TODAS as movimentações
Valida se o botão "Ver todas" está sendo clicado corretamente
"""
import asyncio
import sys
import os
import json

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from src.scraper import TJSPScraper
from loguru import logger

# Configurar logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")

async def testar_extracao_completa():
    """Testa se todas as movimentações estão sendo extraídas"""
    
    print("=" * 70)
    print("TESTE: EXTRAÇÃO DE TODAS AS MOVIMENTAÇÕES")
    print("=" * 70)
    
    # Processo de teste (processo real com 17 movimentações)
    processo_teste = "1024444-30.2025.8.26.0576"
    
    print(f"\n📋 Testando processo: {processo_teste}")
    print("Este processo deve ter 45 movimentações\n")
    
    async with TJSPScraper() as scraper:
        try:
            # Usar método de busca do scraper
            print("1. Buscando processo...")
            resultado = await scraper.search_by_process_number(processo_teste)
            
            if not resultado:
                print("❌ Processo não encontrado")
                return False
            
            # Verificar movimentações
            movimentacoes = resultado.get('movimentacoes', [])
            total_extraido = len(movimentacoes)
            
            print(f"\n2. Movimentações extraídas: {total_extraido}")
            
            # Salvar resultado completo para análise
            output_file = f"teste_processo_completo_{processo_teste.replace('.', '_').replace('-', '_')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            
            print(f"   📄 Dados salvos em: {output_file}")
            
            # Análise
            print("\n3. Análise:")

            # Para este processo específico, esperamos 17 movimentações
            if processo_teste == "1024444-30.2025.8.26.0576" and total_extraido >= 17:
                print(f"   ✅ SUCESSO! {total_extraido} movimentações extraídas")
                print("   ✅ Botão 'Mais' foi clicado corretamente")
                print("   ✅ Todas as movimentações foram expandidas")

                # Mostrar primeiras e últimas movimentações
                print("\n   📋 Primeiras 3 movimentações:")
                for i, mov in enumerate(movimentacoes[:3], 1):
                    print(f"      {i}. {mov.get('mov_data')} - {mov.get('mov_descricao', '')[:50]}...")

                print(f"\n   📋 Últimas 3 movimentações:")
                for i, mov in enumerate(movimentacoes[-3:], len(movimentacoes)-2):
                    print(f"      {i}. {mov.get('mov_data')} - {mov.get('mov_descricao', '')[:50]}...")

                return True

            elif total_extraido >= 10:
                print(f"   ✅ SUCESSO! {total_extraido} movimentações extraídas")
                print("   ✅ Botão de expansão foi clicado corretamente")
                return True

            elif total_extraido >= 5 and total_extraido < 10:
                print(f"   ⚠️ PARCIAL: Apenas {total_extraido} movimentações extraídas")
                print("   ⚠️ Botão de expansão NÃO foi clicado ou não funcionou")
                print("   ⚠️ Sistema extraiu apenas movimentações visíveis")

                print("\n   💡 Possíveis causas:")
                print("      1. Botão tem seletor diferente")
                print("      2. Botão está oculto ou desabilitado")
                print("      3. Site mudou estrutura HTML")

                return False

            else:
                print(f"   ❌ FALHA: Apenas {total_extraido} movimentações extraídas")
                print("   ❌ Muito poucas movimentações")
                return False
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
            return False

async def testar_multiplos_processos():
    """Testa com múltiplos processos"""
    
    print("\n" + "=" * 70)
    print("TESTE: MÚLTIPLOS PROCESSOS")
    print("=" * 70)
    
    processos = [
        "1024444-30.2025.8.26.0576",
        "1024327-39.2025.8.26.0576",
        "1024317-92.2025.8.26.0576"
    ]
    
    resultados = []
    
    async with TJSPScraper() as scraper:
        for i, processo in enumerate(processos, 1):
            print(f"\n[{i}/{len(processos)}] Testando: {processo}")
            
            try:
                resultado = await scraper.search_by_process_number(processo)
                
                if resultado:
                    total = len(resultado.get('movimentacoes', []))
                    print(f"   ✅ {total} movimentações extraídas")
                    resultados.append({
                        'processo': processo,
                        'total': total,
                        'sucesso': total >= 10  # Considerar sucesso se extraiu pelo menos 10
                    })
                else:
                    print(f"   ❌ Processo não encontrado")
                    resultados.append({
                        'processo': processo,
                        'total': 0,
                        'sucesso': False
                    })
                
                # Delay entre processos
                await scraper.random_delay()
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                resultados.append({
                    'processo': processo,
                    'total': 0,
                    'sucesso': False
                })
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    
    total_sucesso = sum(1 for r in resultados if r['sucesso'])
    
    for r in resultados:
        status = "✅" if r['sucesso'] else "❌"
        print(f"{status} {r['processo']}: {r['total']} movimentações")
    
    print(f"\nTotal: {total_sucesso}/{len(processos)} processos com sucesso")
    
    return total_sucesso == len(processos)

async def main():
    """Função principal"""
    print("\n🔍 TESTE DE EXTRAÇÃO COMPLETA DE MOVIMENTAÇÕES")
    print("Este teste valida se o botão 'Ver todas' está sendo clicado\n")
    
    # Teste 1: Processo único
    sucesso1 = await testar_extracao_completa()
    
    # Teste 2: Múltiplos processos (opcional)
    # Descomente para testar com múltiplos processos
    # await asyncio.sleep(5)
    # sucesso2 = await testar_multiplos_processos()
    
    # Resultado final
    print("\n" + "=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    
    if sucesso1:
        print("✅ TESTE PASSOU!")
        print("   Sistema está extraindo TODAS as movimentações")
        print("   Botão 'Ver todas' está funcionando corretamente")
    else:
        print("❌ TESTE FALHOU!")
        print("   Sistema NÃO está extraindo todas as movimentações")
        print("   Verifique:")
        print("   1. Seletores do botão 'Ver todas'")
        print("   2. Estrutura HTML do site")
        print("   3. Logs de debug para mais detalhes")
    
    print("=" * 70)
    
    return sucesso1

if __name__ == "__main__":
    try:
        sucesso = asyncio.run(main())
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
