#!/usr/bin/env python3
"""
Script de diagnóstico simplificado para testar conexão com TJSP
"""
import asyncio
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright não instalado. Execute:")
    print("source venv/bin/activate && pip install playwright")
    sys.exit(1)

async def test_simple_connection():
    """Testa conexão básica com TJSP"""
    print("=" * 50)
    print("TESTE SIMPLIFICADO - CONEXÃO TJSP")
    print("=" * 50)

    async with async_playwright() as p:
        print("\n1. Iniciando browser...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        page = await context.new_page()
        page.set_default_timeout(30000)

        try:
            print("\n2. Testando acesso à página...")
            url = "https://esaj.tjsp.jus.br/cpopg/search.do"
            response = await page.goto(url, wait_until='domcontentloaded')

            if response.status == 200:
                print("   ✓ Página acessada com sucesso")
            else:
                print(f"   ✗ Erro HTTP: {response.status}")
                return

            # Verificar título
            title = await page.title()
            print(f"   ✓ Título da página: {title}")

            # Verificar se há elementos básicos
            body_text = (await page.inner_text('body')).lower()

            if 'tribunal' in body_text and 'justiça' in body_text:
                print("   ✓ Conteúdo TJSP detectado")
            else:
                print("   ⚠️ Conteúdo suspeito - pode não ser a página correta")

            # Verificar CAPTCHA
            if 'recaptcha' in body_text or 'captcha' in body_text:
                print("   ⚠️ CAPTCHA detectado")
            else:
                print("   ✓ Sem CAPTCHA aparente")

            # Salvar HTML básico
            content = await page.content()
            with open('debug_basico.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("   📄 HTML salvo: debug_basico.html")

            print("\n" + "=" * 50)
            print("TESTE BÁSICO CONCLUÍDO")
            print("Se chegou aqui, conexão funciona!")
            print("Próximo: testar seletores específicos")
            print("=" * 50)

        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_simple_connection())
