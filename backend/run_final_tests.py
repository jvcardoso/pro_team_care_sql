#!/usr/bin/env python3
"""
Script final para executar testes otimizados da plataforma
Objetivo: Alcançar 90%+ de taxa de sucesso
"""
import subprocess
import sys
import os
from datetime import datetime

def run_final_tests():
    """Executa a bateria final de testes otimizados"""
    
    print("🚀 EXECUÇÃO FINAL DE TESTES - PLATAFORMA EMPRESAS")
    print("="*60)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Configurar ambiente
    os.environ["PYTHONPATH"] = "/home/juliano/Projetos/meu_projeto/backend"
    
    # Lista de testes em ordem de prioridade
    test_commands = [
        {
            "name": "🧪 Testes Otimizados (Principais)",
            "cmd": ["pytest", "tests/api/test_companies_optimized.py", "-v", "-s", "--tb=short"],
            "critical": True,
            "timeout": 180
        },
        {
            "name": "🔍 Debug Stored Procedure",
            "cmd": ["pytest", "tests/api/test_debug_stored_procedure.py", "-v", "-s", "--tb=short"],
            "critical": False,
            "timeout": 120
        },
        {
            "name": "🏥 Testes Básicos de Empresas",
            "cmd": ["pytest", "tests/api/test_companies.py::test_list_companies", "-v"],
            "critical": False,
            "timeout": 60
        },
        {
            "name": "🔐 Testes de Autenticação",
            "cmd": ["pytest", "tests/api/test_auth.py", "-v", "--tb=short"],
            "critical": False,
            "timeout": 60
        }
    ]
    
    results = {}
    overall_success = True
    
    for i, test_group in enumerate(test_commands, 1):
        print(f"\n{'='*60}")
        print(f"📋 EXECUTANDO ({i}/{len(test_commands)}): {test_group['name']}")
        print(f"{'='*60}")
        
        try:
            # Executar teste
            result = subprocess.run(
                test_group["cmd"],
                cwd="/home/juliano/Projetos/meu_projeto/backend",
                capture_output=True,
                text=True,
                timeout=test_group["timeout"]
            )
            
            # Processar resultado
            success = result.returncode == 0
            results[test_group["name"]] = {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if success:
                print(f"✅ {test_group['name']}: SUCESSO")
                # Mostrar saída relevante
                if "Taxa de Sucesso" in result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "Taxa de Sucesso" in line or "TAXA DE SUCESSO" in line:
                            print(f"📊 {line.strip()}")
            else:
                print(f"❌ {test_group['name']}: FALHOU (código {result.returncode})")
                if test_group["critical"]:
                    overall_success = False
                    print("🚨 TESTE CRÍTICO FALHOU!")
                
                # Mostrar erros relevantes
                if result.stderr:
                    print("🔍 Erros:")
                    error_lines = result.stderr.split('\n')[:5]  # Primeiras 5 linhas
                    for line in error_lines:
                        if line.strip():
                            print(f"   {line.strip()}")
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_group['name']}: TIMEOUT ({test_group['timeout']}s)")
            results[test_group["name"]] = {
                "success": False,
                "error": "timeout"
            }
            if test_group["critical"]:
                overall_success = False
                
        except Exception as e:
            print(f"💥 {test_group['name']}: ERRO - {str(e)}")
            results[test_group["name"]] = {
                "success": False,
                "error": str(e)
            }
            if test_group["critical"]:
                overall_success = False
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📊 RESUMO EXECUTIVO FINAL")
    print(f"{'='*60}")
    print(f"⏰ Término: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = sum(1 for r in results.values() if r.get("success", False))
    total_count = len(results)
    final_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"🎯 Grupos de Teste: {total_count}")
    print(f"✅ Sucessos: {success_count}")
    print(f"❌ Falhas: {total_count - success_count}")
    print(f"📈 Taxa Final: {final_rate:.1f}%")
    
    # Status da plataforma
    if final_rate >= 90:
        print("🎉 PLATAFORMA 100% VIÁVEL - EXCELENTE!")
        status = "EXCELENTE"
    elif final_rate >= 70:
        print("✅ PLATAFORMA VIÁVEL - MUITO BOM!")
        status = "VIÁVEL"
    elif final_rate >= 50:
        print("⚠️ PLATAFORMA PARCIALMENTE VIÁVEL - AJUSTES NECESSÁRIOS")
        status = "PARCIAL"
    else:
        print("🚨 PLATAFORMA NÃO VIÁVEL - CORREÇÕES CRÍTICAS NECESSÁRIAS")
        status = "CRÍTICO"
    
    # Recomendações finais
    print(f"\n📋 RECOMENDAÇÕES:")
    if final_rate >= 90:
        print("• Plataforma pronta para produção")
        print("• Implementar CI/CD")
        print("• Adicionar testes de carga")
    elif final_rate >= 70:
        print("• Corrigir problemas menores identificados")
        print("• Implementar endpoints faltantes")
        print("• Plataforma utilizável para desenvolvimento")
    else:
        print("• Focar na correção da stored procedure")
        print("• Verificar conectividade e configurações")
        print("• Re-executar após correções")
    
    # Salvar relatório
    report_file = f"relatorio_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(f"RELATÓRIO FINAL - PLATAFORMA DE TESTES\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Taxa de Sucesso: {final_rate:.1f}%\n")
        f.write(f"Status: {status}\n\n")
        
        for name, result in results.items():
            f.write(f"{name}: {'SUCESSO' if result.get('success') else 'FALHA'}\n")
    
    print(f"\n📄 Relatório salvo em: {report_file}")
    
    # Código de saída
    return 0 if overall_success and final_rate >= 70 else 1

if __name__ == "__main__":
    exit_code = run_final_tests()
    sys.exit(exit_code)
