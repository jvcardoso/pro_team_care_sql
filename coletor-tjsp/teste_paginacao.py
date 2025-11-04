#!/usr/bin/env python3
"""
Teste de paginação na busca por parte
"""
import asyncio
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from src.scraper import TJSPScraper

async def teste_paginacao():
    """Teste da paginação na busca por parte"""
    print("=" * 80)
    print("TESTE DE PAGINAÇÃO - BUSCA POR PARTE")
    print("=" * 80)

    async with TJSPScraper() as scraper:
        try:
            # Navegar para página de busca
            await scraper.page.goto(scraper.config.TJSP_SEARCH_URL)
            await scraper.random_delay()

            # Selecionar tipo de busca por parte
            await scraper.page.select_option('#cbPesquisa', 'NMPARTE')
            await scraper.random_delay()

            # Aguardar campo ser habilitado
            await scraper.page.wait_for_selector('#campo_NMPARTE:not([disabled])', timeout=10000)
            await scraper.page.fill('#campo_NMPARTE', 'Parque Rio Nieva')

            # Submeter busca
            await scraper.page.click('#botaoConsultarProcessos')
            await scraper.page.wait_for_load_state('networkidle')
            await scraper.random_delay()

            # Verificar se há próxima página
            has_next = await scraper.has_next_page()
            print(f"🔍 Há próxima página: {has_next}")

            if has_next:
                print("✅ Navegando para próxima página...")
                await scraper.goto_next_page()
                print("✅ Navegação realizada com sucesso!")
            else:
                print("ℹ️  Não há próxima página")

        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(teste_paginacao())