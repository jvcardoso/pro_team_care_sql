#!/usr/bin/env python3
"""
Teste de debug para busca por parte
"""
import asyncio
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from src.scraper import TJSPScraper

async def debug_busca_parte():
    """Debug da busca por parte"""
    print("=" * 80)
    print("DEBUG - BUSCA POR PARTE")
    print("=" * 80)

    async with TJSPScraper() as scraper:
        print("🔍 Testando acesso aos campos de busca...")

        try:
            # Navegar para página de busca
            await scraper.page.goto(scraper.config.TJSP_SEARCH_URL)
            await scraper.random_delay()

            # Verificar se o select existe
            select_element = await scraper.page.query_selector('#cbPesquisa')
            if select_element:
                print("✅ Select #cbPesquisa encontrado")
            else:
                print("❌ Select #cbPesquisa NÃO encontrado")
                return

            # Selecionar tipo de busca por parte
            print("🔄 Selecionando 'Nome da parte'...")
            await scraper.page.select_option('#cbPesquisa', 'NMPARTE')
            await scraper.random_delay()

            # Verificar se o campo foi habilitado
            campo_element = await scraper.page.query_selector('#campo_NMPARTE:not([disabled])')
            if campo_element:
                print("✅ Campo #campo_NMPARTE habilitado")
            else:
                print("❌ Campo #campo_NMPARTE ainda desabilitado")
                return

            # Tentar preencher o campo
            print("🔄 Preenchendo campo com 'Parque Rio Nieva'...")
            await scraper.page.fill('#campo_NMPARTE', 'Parque Rio Nieva')

            # Verificar se foi preenchido
            value = await scraper.page.input_value('#campo_NMPARTE')
            print(f"📝 Valor no campo: '{value}'")

            # Tentar submeter
            print("🔄 Clicando em consultar...")
            await scraper.page.click('#botaoConsultarProcessos')
            await scraper.page.wait_for_load_state('networkidle')
            await scraper.random_delay()

            # Verificar resultado
            content = await scraper.page.content()
            if 'Processos encontrados' in content or 'processo' in content.lower():
                print("✅ Busca executada - resultados encontrados")
            else:
                print("⚠️  Busca executada mas sem resultados claros")

            # Salvar HTML para análise
            with open('debug_busca_parte.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("💾 HTML salvo em debug_busca_parte.html")

        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_busca_parte())