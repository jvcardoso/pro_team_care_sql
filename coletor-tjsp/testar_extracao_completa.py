#!/usr/bin/env python3
"""
Script para testar extração COMPLETA de dados do processo
Valida se TODOS os campos estão sendo preenchidos corretamente
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

async def testar_processo_completo(processo_numero: str):
    """
    Testa extração completa de um processo específico
    
    Args:
        processo_numero: Número do processo a testar
    
    Returns:
        True se todos os dados foram extraídos, False caso contrário
    """
    print("=" * 80)
    print(f"TESTE: EXTRAÇÃO COMPLETA DO PROCESSO {processo_numero}")
    print("=" * 80)
    
    async with TJSPScraper() as scraper:
        try:
            # Buscar processo
            print(f"\n1️⃣  Buscando processo...")
            resultado = await scraper.search_by_process_number(processo_numero)
            
            if not resultado:
                print("❌ Processo não encontrado")
                return False
            
            # Salvar resultado completo
            output_file = f"teste_extracao_completa_{processo_numero.replace('.', '_').replace('-', '_')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Dados salvos em: {output_file}")
            
            # Validar campos obrigatórios
            print(f"\n2️⃣  Validando campos extraídos...")
            
            campos_validacao = {
                'processo_numero': resultado.get('processo_numero'),
                'vara': resultado.get('vara'),
                'classe_assunto': resultado.get('classe_assunto'),
                'exequente': resultado.get('exequente'),
                'executado': resultado.get('executado'),
                'advogado_autor_nome': resultado.get('advogado_autor_nome'),
                'situacao': resultado.get('situacao'),
                'movimentacoes': resultado.get('movimentacoes', [])
            }
            
            # Verificar cada campo
            campos_vazios = []
            campos_preenchidos = []
            
            for campo, valor in campos_validacao.items():
                if campo == 'movimentacoes':
                    if valor and len(valor) > 0:
                        campos_preenchidos.append(f"   ✅ {campo}: {len(valor)} movimentações")
                    else:
                        campos_vazios.append(f"   ❌ {campo}: VAZIO")
                else:
                    if valor and valor.strip():
                        # Truncar valor longo para exibição
                        valor_display = valor[:50] + "..." if len(valor) > 50 else valor
                        campos_preenchidos.append(f"   ✅ {campo}: {valor_display}")
                    else:
                        campos_vazios.append(f"   ❌ {campo}: VAZIO")
            
            # Exibir resultados
            print("\n📊 Campos Preenchidos:")
            for campo in campos_preenchidos:
                print(campo)
            
            if campos_vazios:
                print("\n⚠️  Campos Vazios:")
                for campo in campos_vazios:
                    print(campo)
            
            # Análise de movimentações
            movimentacoes = resultado.get('movimentacoes', [])
            if movimentacoes:
                print(f"\n3️⃣  Análise de Movimentações:")
                print(f"   📋 Total: {len(movimentacoes)}")
                
                # Verificar se há movimentações com texto completo
                com_texto_completo = sum(1 for m in movimentacoes if m.get('mov_texto_completo'))
                print(f"   📝 Com texto completo: {com_texto_completo}/{len(movimentacoes)}")
                
                # Verificar decisões judiciais
                com_decisao = sum(1 for m in movimentacoes if m.get('contem_decisao_judicial'))
                print(f"   ⚖️  Com decisão judicial: {com_decisao}/{len(movimentacoes)}")
                
                # Mostrar primeiras 3 movimentações
                print(f"\n   📋 Primeiras 3 movimentações:")
                for i, mov in enumerate(movimentacoes[:3], 1):
                    data = mov.get('mov_data', 'N/A')
                    desc = mov.get('mov_descricao', '')[:60]
                    print(f"      {i}. {data} - {desc}...")
            
            # Resultado final
            print("\n" + "=" * 80)
            print("RESULTADO DA VALIDAÇÃO")
            print("=" * 80)
            
            total_campos = len(campos_validacao)
            campos_ok = len(campos_preenchidos)
            percentual = (campos_ok / total_campos) * 100
            
            print(f"\n📊 Campos preenchidos: {campos_ok}/{total_campos} ({percentual:.1f}%)")
            
            # Critério de sucesso: pelo menos 80% dos campos preenchidos
            if percentual >= 80:
                print("\n✅ TESTE PASSOU!")
                print("   Sistema está extraindo dados corretamente")
                return True
            else:
                print("\n❌ TESTE FALHOU!")
                print(f"   Apenas {percentual:.1f}% dos campos foram preenchidos")
                print("   Esperado: pelo menos 80%")
                return False
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
            return False

async def main():
    """Função principal"""
    print("\n🔍 TESTE DE EXTRAÇÃO COMPLETA DE DADOS")
    print("Valida se TODOS os campos estão sendo extraídos corretamente\n")
    
    # Processo de teste
    processo_teste = "1003389-91.2023.8.26.0576"
    
    print(f"📋 Processo de teste: {processo_teste}")
    print("   Este processo deve ter:")
    print("   • Exequente: Condomínio Parque Rio Nieva")
    print("   • Executado: Muriel Junio Rosa Ferreira")
    print("   • Advogado: Adilson Lopes Teixeira")
    print("   • Múltiplas movimentações")
    
    # Executar teste
    sucesso = await testar_processo_completo(processo_teste)
    
    # Resultado final
    print("\n" + "=" * 80)
    if sucesso:
        print("✅ EXTRAÇÃO COMPLETA VALIDADA!")
        print("   Todos os campos principais foram extraídos corretamente")
        print("   Sistema pronto para coleta em produção")
    else:
        print("❌ EXTRAÇÃO INCOMPLETA!")
        print("   Alguns campos não foram extraídos")
        print("   Verifique os logs acima para detalhes")
    print("=" * 80)
    
    return sucesso

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
