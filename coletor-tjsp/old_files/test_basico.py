#!/usr/bin/env python3
"""
Teste básico e robusto - Valida apenas conectividade
"""
import asyncio
import sys

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright não instalado!")
    print("\nExecute primeiro:")
    print("  ./setup.sh")
    print("\nOu manualmente:")
    print("  source venv/bin/activate")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)

async def test_basic():
    """Teste básico de conectividade"""
    print("=" * 60)
    print("TESTE BÁSICO - CONECTIVIDADE TJSP")
    print("=" * 60)
    
    try:
        async with async_playwright() as p:
            print("\n1. Iniciando browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            page.set_default_timeout(30000)
            
            print("   ✓ Browser iniciado")
            
            # Teste 1: Acessar página
            print("\n2. Acessando TJSP...")
            url = "https://esaj.tjsp.jus.br/cpopg/search.do"
            
            try:
                response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                if response and response.status == 200:
                    print(f"   ✓ Página acessada (HTTP {response.status})")
                else:
                    print(f"   ⚠️ Status HTTP: {response.status if response else 'unknown'}")
                
            except Exception as e:
                print(f"   ❌ Erro ao acessar: {e}")
                await browser.close()
                return False
            
            # Teste 2: Verificar conteúdo
            print("\n3. Verificando conteúdo...")
            try:
                title = await page.title()
                print(f"   ✓ Título: {title}")
                
                body = await page.inner_text('body')
                
                if 'tribunal' in body.lower() or 'tjsp' in body.lower():
                    print("   ✓ Conteúdo TJSP detectado")
                else:
                    print("   ⚠️ Conteúdo não reconhecido")
                
            except Exception as e:
                print(f"   ❌ Erro ao verificar conteúdo: {e}")
            
            # Teste 3: Verificar elementos principais
            print("\n4. Verificando elementos da página...")
            
            elementos = {
                'Select de pesquisa': '#cbPesquisa',
                'Campo de consulta': '#dadosConsulta\\.valorConsulta',
                'Botão pesquisar': 'input[value="Pesquisar"]'
            }
            
            elementos_encontrados = 0
            
            for nome, seletor in elementos.items():
                try:
                    element = await page.query_selector(seletor)
                    if element:
                        print(f"   ✓ {nome}: ENCONTRADO")
                        elementos_encontrados += 1
                    else:
                        print(f"   ✗ {nome}: NÃO ENCONTRADO")
                except Exception as e:
                    print(f"   ✗ {nome}: ERRO ({e})")
            
            # Teste 4: Verificar CAPTCHA
            print("\n5. Verificando proteções...")
            try:
                html = await page.content()
                
                if 'recaptcha' in html.lower() or 'captcha' in html.lower():
                    print("   ⚠️ CAPTCHA detectado")
                    print("   → Execute em horário de baixo tráfego (22h-6h)")
                else:
                    print("   ✓ Sem CAPTCHA aparente")
                
            except Exception as e:
                print(f"   ⚠️ Erro ao verificar CAPTCHA: {e}")
            
            # Salvar HTML para análise
            try:
                with open('debug_teste_basico.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("\n   📄 HTML salvo: debug_teste_basico.html")
            except:
                pass
            
            await browser.close()
            
            # Resultado final
            print("\n" + "=" * 60)
            print("RESULTADO DO TESTE")
            print("=" * 60)
            
            if elementos_encontrados == 3:
                print("✅ SUCESSO TOTAL!")
                print("   Todos os elementos encontrados")
                print("   Sistema pronto para uso")
                return True
            elif elementos_encontrados >= 2:
                print("⚠️ SUCESSO PARCIAL")
                print(f"   {elementos_encontrados}/3 elementos encontrados")
                print("   Sistema pode funcionar com limitações")
                return True
            else:
                print("❌ FALHA")
                print("   Poucos elementos encontrados")
                print("   Site pode ter mudado ou CAPTCHA está bloqueando")
                return False
            
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("\n🔍 Teste Básico de Conectividade")
    print("Este teste verifica se o sistema consegue acessar o TJSP\n")
    
    try:
        resultado = asyncio.run(test_basic())
        
        print("\n" + "=" * 60)
        if resultado:
            print("✅ Sistema validado!")
            print("\nPróximos passos:")
            print("1. Teste com busca real:")
            print("   python test_correcao.py")
            print("\n2. Ou execute coleta:")
            print("   python run.py --search-party 'Rio Nieva' --output output/")
        else:
            print("⚠️ Sistema com problemas")
            print("\nPossíveis soluções:")
            print("1. Execute em outro horário (22h-6h)")
            print("2. Verifique conexão com internet")
            print("3. Abra debug_teste_basico.html para análise")
            print("4. Leia GUIA_DEBUG.md")
        print("=" * 60)
        
        sys.exit(0 if resultado else 1)
        
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
        sys.exit(0)

if __name__ == "__main__":
    main()
