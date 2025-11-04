#!/usr/bin/env python3
import asyncio
from src.scraper import TJSPScraper

async def test_party():
    async with TJSPScraper() as scraper:
        processos = await scraper.search_by_party('João Silva', max_pages=1)
        print(f'Encontrados: {len(processos)} processos')
        if processos:
            print(f'Primeiro processo: {processos[0]}')
            # Tentar buscar detalhes do primeiro processo
            detalhes = await scraper.search_by_process_number(processos[0])
            if detalhes:
                print(f'Detalhes encontrados: {len(detalhes.get("movimentacoes", []))} movimentações')
            else:
                print('Detalhes não encontrados')

if __name__ == "__main__":
    asyncio.run(test_party())