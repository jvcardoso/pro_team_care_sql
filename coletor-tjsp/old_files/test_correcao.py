#!/usr/bin/env python3
"""
Teste automatizado para validar correções dos seletores
"""
import asyncio
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from src.scraper import TJSPScraper
from loguru import logger

# Configurar logging simples
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")

async def test_search_party():
    """Testa busca por parte (Rio Nieva)"""
    print("=" * 60)
    print("TESTE DE VALIDAÇÃO - BUSCA POR PARTE")
    print("=" * 60)
    
    async with TJSPScraper() as scraper:
        try:
            print("\n1. Testando busca por 'Rio Nieva'...")
            processos = await scraper.search_by_party("Rio Nieva", max_pages=1)
            
            if processos:
                print(f"\n✅ SUCESSO! {len(processos)} processos encontrados:")
                for i, proc in enumerate(processos[:5], 1):
                    print(f"   {i}. {proc}")
                
                if len(processos) > 5:
                    print(f"   ... e mais {len(processos) - 5} processos")
                
                return True
            else:
                print("\n⚠️ Nenhum processo encontrado")
                print("Possíveis causas:")
                print("  - Nome 'Rio Nieva' não tem processos públicos")
                print("  - Processos estão em segredo de justiça")
                print("  - CAPTCHA bloqueou a busca")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
            return False

async def test_search_lawyer():
    """Testa busca por advogado"""
    print("\n" + "=" * 60)
    print("TESTE DE VALIDAÇÃO - BUSCA POR ADVOGADO")
    print("=" * 60)
    
    async with TJSPScraper() as scraper:
        try:
            print("\n2. Testando busca por 'Adilson Lopes Teixeira'...")
            processos = await scraper.search_by_lawyer("Adilson Lopes Teixeira", max_pages=1)
            
            if processos:
                print(f"\n✅ SUCESSO! {len(processos)} processos encontrados:")
                for i, proc in enumerate(processos[:5], 1):
                    print(f"   {i}. {proc}")
                
                if len(processos) > 5:
                    print(f"   ... e mais {len(processos) - 5} processos")
                
                return True
            else:
                print("\n⚠️ Nenhum processo encontrado")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
            return False

async def test_process_number():
    """Testa busca por número de processo"""
    print("\n" + "=" * 60)
    print("TESTE DE VALIDAÇÃO - BUSCA POR NÚMERO")
    print("=" * 60)
    
    # Usar um número de processo público conhecido
    # NOTA: Substitua por um processo real se souber algum
    processo_teste = "1000032-02.2024.8.26.0100"
    
    async with TJSPScraper() as scraper:
        try:
            print(f"\n3. Testando busca por processo {processo_teste}...")
            resultado = await scraper.search_by_process_number(processo_teste)
            
            if resultado:
                print(f"\n✅ SUCESSO! Processo encontrado:")
                print(f"   Número: {resultado.get('processo_numero')}")
                print(f"   Vara: {resultado.get('vara')}")
                print(f"   Movimentações: {len(resultado.get('movimentacoes', []))}")
                return True
            else:
                print("\n⚠️ Processo não encontrado ou em segredo")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
            return False

async def main():
    """Executa todos os testes"""
    print("\n🔍 INICIANDO TESTES DE VALIDAÇÃO")
    print("Este teste vai verificar se os seletores CSS foram corrigidos\n")
    
    resultados = {
        'busca_parte': False,
        'busca_advogado': False,
        'busca_numero': False
    }
    
    # Teste 1: Busca por parte
    try:
        resultados['busca_parte'] = await test_search_party()
    except Exception as e:
        print(f"Erro no teste de busca por parte: {e}")
    
    await asyncio.sleep(3)  # Delay entre testes
    
    # Teste 2: Busca por advogado
    try:
        resultados['busca_advogado'] = await test_search_lawyer()
    except Exception as e:
        print(f"Erro no teste de busca por advogado: {e}")
    
    await asyncio.sleep(3)  # Delay entre testes
    
    # Teste 3: Busca por número (opcional)
    # Descomente se tiver um número de processo válido
    # try:
    #     resultados['busca_numero'] = await test_process_number()
    # except Exception as e:
    #     print(f"Erro no teste de busca por número: {e}")
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    total = len(resultados)
    sucesso = sum(1 for v in resultados.values() if v)
    
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{teste.replace('_', ' ').title()}: {status}")
    
    print(f"\nTotal: {sucesso}/{total} testes passaram")
    
    if sucesso == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("Sistema está funcionando corretamente.")
    elif sucesso > 0:
        print("\n⚠️ ALGUNS TESTES PASSARAM")
        print("Sistema parcialmente funcional.")
    else:
        print("\n❌ TODOS OS TESTES FALHARAM")
        print("Verifique:")
        print("  1. Conexão com internet")
        print("  2. Site TJSP está acessível")
        print("  3. CAPTCHA pode estar bloqueando")
        print("  4. Execute em horário de baixo tráfego (22h-6h)")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
