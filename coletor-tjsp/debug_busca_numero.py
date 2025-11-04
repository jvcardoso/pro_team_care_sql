#!/usr/bin/env python3
"""
Debug da busca por número de processo
"""
import asyncio
from src.scraper import TJSPScraper

async def debug_busca():
    """Debug da busca por número"""
    print("🔍 DEBUG - BUSCA POR NÚMERO DE PROCESSO")
    print("=" * 50)

    async with TJSPScraper() as scraper:
        # Testar com um processo que sabemos que apareceu na busca por parte
        processo_teste = "1024444-30.2025.8.26.0576"

        print(f"Testando processo: {processo_teste}")
        print(f"Primeiros 15 dígitos: {processo_teste[:15]}")
        print(f"Últimos 4 dígitos: {processo_teste[-4:]}")

        # Construir URL igual ao código atual
        search_params = {
            'cbPesquisa': 'NUMPROC',
            'numeroDigitoAnoUnificado': processo_teste[:15],  # primeiros 15 dígitos
            'foroNumeroUnificado': processo_teste[-4:],  # últimos 4 dígitos
            'dadosConsulta.valorConsultaNuUnificado': processo_teste,
            'dadosConsulta.tipoNuProcesso': 'UNIFICADO'
        }

        query_string = '&'.join([f"{k}={v}" for k, v in search_params.items()])
        search_url = f"{scraper.config.TJSP_SEARCH_URL}?{query_string}"

        print(f"URL construída: {search_url}")

        try:
            print("Navegando para URL...")
            await scraper.page.goto(search_url)
            await scraper.page.wait_for_load_state('networkidle')
            await scraper.random_delay()

            content = await scraper.page.content()
            print(f"Conteúdo da página tem {len(content)} caracteres")

            # Verificar se encontrou algo
            if "dadosDoProcesso" in content:
                print("✅ ENCONTROU PÁGINA DE DETALHES!")
            elif "Não existem informações" in content:
                print("❌ NÃO EXISTEM INFORMAÇÕES")
            elif "segredo de justiça" in content:
                print("🔒 SEGREDO DE JUSTIÇA")
            elif "tipo de pesquisa informado é inválido" in content:
                print("❌ TIPO DE PESQUISA INVÁLIDO")
            else:
                print("❓ RESULTADO DESCONHECIDO")

                # Salvar HTML para análise
                with open("debug_busca_numero.html", "w", encoding="utf-8") as f:
                    f.write(content)
                print("HTML salvo em debug_busca_numero.html")

        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    asyncio.run(debug_busca())