#!/usr/bin/env python3
"""
Script para testar e validar seletores CSS do TJSP
"""
import asyncio
from playwright.async_api import async_playwright
import sys

async def test_selectors():
    """Testa diferentes seletores para encontrar os corretos"""
    print("=" * 60)
    print("TESTE DE SELETORES CSS - TJSP")
    print("=" * 60)
    
    async with async_playwright() as p:
        print("\n1. Iniciando browser...")
        browser = await p.chromium.launch(headless=False)
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        try:
            print("\n2. Acessando página de busca...")
            await page.goto("https://esaj.tjsp.jus.br/cpopg/search.do")
            await asyncio.sleep(3)
            
            print("\n3. Testando seletores para SELECT de tipo de pesquisa...")
            selectors_select = [
                'select[name="cbPesquisa"]',
                '#cbPesquisa',
                'select#cbPesquisa',
                'select.form-control[name="cbPesquisa"]'
            ]
            
            select_found = None
            for selector in selectors_select:
                element = await page.query_selector(selector)
                if element:
                    print(f"   ✓ ENCONTRADO: {selector}")
                    select_found = selector
                    break
                else:
                    print(f"   ✗ Não encontrado: {selector}")
            
            print("\n4. Testando seletores para INPUT de consulta...")
            selectors_input = [
                'input[name="dadosConsulta.valorConsulta"]',
                '#dadosConsulta\\.valorConsulta',
                'input#dadosConsulta\\.valorConsulta',
                'input[id="dadosConsulta.valorConsulta"]',
                'input.form-control[name="dadosConsulta.valorConsulta"]'
            ]
            
            input_found = None
            for selector in selectors_input:
                element = await page.query_selector(selector)
                if element:
                    print(f"   ✓ ENCONTRADO: {selector}")
                    input_found = selector
                    break
                else:
                    print(f"   ✗ Não encontrado: {selector}")
            
            print("\n5. Testando seletores para BOTÃO de consulta...")
            selectors_button = [
                'input[type="submit"][value="Consultar"]',
                'input[value="Pesquisar"]',
                'button[type="submit"]',
                'input.btn-primary[type="submit"]',
                '#botaoConsultar',
                'input[name="pbEnviar"]'
            ]
            
            button_found = None
            for selector in selectors_button:
                element = await page.query_selector(selector)
                if element:
                    value = await element.get_attribute('value')
                    print(f"   ✓ ENCONTRADO: {selector} (value='{value}')")
                    button_found = selector
                    break
                else:
                    print(f"   ✗ Não encontrado: {selector}")
            
            # Teste prático
            if select_found and input_found and button_found:
                print("\n6. Testando busca real com seletores encontrados...")
                
                # Selecionar tipo de busca
                await page.select_option(select_found, 'NMPARTE')
                print(f"   ✓ Selecionado tipo: NMPARTE usando {select_found}")
                
                # Preencher campo
                await page.fill(input_found, 'Rio Nieva')
                print(f"   ✓ Campo preenchido usando {input_found}")
                
                # Clicar botão
                await page.click(button_found)
                print(f"   ✓ Botão clicado usando {button_found}")
                
                # Aguardar resultado
                await page.wait_for_load_state('networkidle', timeout=30000)
                print("   ✓ Página de resultados carregada")
                
                # Verificar resultados
                content = await page.content()
                
                if "Não existem informações" in content:
                    print("   ⚠️  Nenhum resultado encontrado")
                else:
                    # Testar seletores de links de processos
                    print("\n7. Testando seletores para links de processos...")
                    selectors_links = [
                        'a.linkProcesso',
                        'a.linkMovVincProc',
                        'a[href*="processo"]',
                        'table a'
                    ]
                    
                    for selector in selectors_links:
                        links = await page.query_selector_all(selector)
                        if links:
                            print(f"   ✓ {len(links)} links encontrados com: {selector}")
                            # Mostrar primeiro link
                            if links:
                                text = await links[0].inner_text()
                                print(f"      Exemplo: {text.strip()}")
                        else:
                            print(f"   ✗ Nenhum link com: {selector}")
                
                # Salvar HTML
                with open('debug_selectors.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("\n   📄 HTML salvo: debug_selectors.html")
            
            print("\n" + "=" * 60)
            print("RESUMO DOS SELETORES CORRETOS:")
            print("=" * 60)
            if select_found:
                print(f"SELECT: {select_found}")
            if input_found:
                print(f"INPUT:  {input_found}")
            if button_found:
                print(f"BUTTON: {button_found}")
            print("=" * 60)
            
            # Aguardar para visualização
            print("\nAguardando 10 segundos para visualização...")
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(test_selectors())
    except KeyboardInterrupt:
        print("\n\nTeste interrompido")
        sys.exit(0)
