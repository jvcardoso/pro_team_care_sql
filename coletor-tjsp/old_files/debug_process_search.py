#!/usr/bin/env python3
"""
Debug script for process search
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
logger.add(sys.stdout, level="DEBUG", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")

async def debug_process_search():
    """Debug process search"""
    print("=" * 60)
    print("DEBUG - BUSCA POR PROCESSO")
    print("=" * 60)

    processo_teste = "1028484-65.2019.8.26.0576"

    async with TJSPScraper() as scraper:
        try:
            print(f"\nTestando busca por processo {processo_teste}...")

            # Primeiro, vamos navegar para a página de busca e verificar os elementos
            await scraper.page.goto(scraper.config.TJSP_SEARCH_URL)
            await scraper.random_delay()

            print("Verificando elementos da página...")

            # Verificar se o select existe
            select_element = await scraper.page.query_selector('#cbPesquisa')
            if select_element:
                print("✓ Select #cbPesquisa encontrado")
            else:
                print("✗ Select #cbPesquisa NÃO encontrado")
                return

            # Selecionar NUMPROC
            await scraper.page.select_option('#cbPesquisa', 'NUMPROC')
            await scraper.random_delay()
            print("✓ Selecionado NUMPROC")

            # Verificar campos do processo
            campo_numero = await scraper.page.query_selector('#numeroDigitoAnoUnificado')
            campo_foro = await scraper.page.query_selector('#foroNumeroUnificado')

            if campo_numero and campo_foro:
                print("✓ Campos do processo encontrados")
            else:
                print("✗ Campos do processo NÃO encontrados")
                return

            # Preencher campos
            await scraper.page.fill('#numeroDigitoAnoUnificado', processo_teste[:13])  # primeiros 13 dígitos
            await scraper.page.fill('#foroNumeroUnificado', processo_teste[-4:])  # últimos 4 dígitos
            print("✓ Campos preenchidos")

            # Verificar botão
            botao = await scraper.page.query_selector('#botaoConsultarProcessos')
            if botao:
                print("✓ Botão de consulta encontrado")
            else:
                print("✗ Botão de consulta NÃO encontrado")
                return

            # Clicar no botão
            await scraper.page.click('#botaoConsultarProcessos')
            await scraper.page.wait_for_load_state('networkidle')
            await scraper.random_delay()
            print("✓ Busca submetida")

            # Verificar resultado
            content = await scraper.page.content()

            if "Não existem informações" in content:
                print("⚠️ Processo não encontrado - 'Não existem informações'")
                return
            elif "segredo de justiça" in content:
                print("⚠️ Processo em segredo de justiça")
                return
            else:
                print("✓ Resultados encontrados")

            # Salvar HTML para análise
            with open('debug_search_results.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("📄 HTML dos resultados salvo: debug_search_results.html")

            # Procurar links de processos
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'lxml')
            links = soup.find_all('a', {'class': 'linkMovVincProc'})

            print(f"Links encontrados: {len(links)}")

            for i, link in enumerate(links[:3], 1):
                texto = link.get_text(strip=True)
                href = link.get('href')
                print(f"  {i}. {texto} -> {href}")

            if links:
                # Tentar clicar no primeiro link
                primeiro_link = links[0]
                href = primeiro_link.get('href')
                if href.startswith('/'):
                    href = f"{scraper.config.TJSP_BASE_URL}{href}"

                print(f"\nNavegando para: {href}")
                await scraper.page.goto(href)
                await scraper.page.wait_for_load_state('networkidle')
                await scraper.random_delay()

                # Salvar HTML da página de detalhes
                detail_content = await scraper.page.content()
                with open('debug_process_detail.html', 'w', encoding='utf-8') as f:
                    f.write(detail_content)
                print("📄 HTML da página de detalhes salvo: debug_process_detail.html")

                # Verificar se é página de detalhes
                if "dadosDoProcesso" in detail_content:
                    print("✓ Página de detalhes do processo carregada")
                else:
                    print("⚠️ Página não parece ser de detalhes do processo")

                # Tentar extrair dados
                resultado = await scraper.extract_process_data(detail_content, processo_teste)
                print(f"Resultado da extração: {len(resultado.get('movimentacoes', []))} movimentações")

        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(debug_process_search())
    except KeyboardInterrupt:
        print("\n\nDebug interrompido pelo usuário")
        sys.exit(0)