#!/usr/bin/env python3
"""
Script para configurar e executar a plataforma de testes automatizados
"""
import os
import sys
import subprocess
import json
from datetime import datetime

class TestEnvironmentSetup:
    def __init__(self):
        self.base_path = "/home/juliano/Projetos/meu_projeto/backend"
        self.test_results = {}
        
    def setup_environment(self):
        """Configura o ambiente de teste"""
        print("🔧 Configurando ambiente de teste...")
        
        # 1. Verificar variáveis de ambiente
        required_vars = [
            "TEST_DATABASE_URL",
            "TEST_ADMIN_EMAIL", 
            "TEST_ADMIN_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
            print("\n📝 Configure as variáveis:")
            print("export TEST_DATABASE_URL='mssql+pyodbc://sa:SuaSenha@IP_SERVIDOR/pro_team_care_test?driver=ODBC+Driver+17+for+SQL+Server&timeout=30'")
            print("export TEST_ADMIN_EMAIL='admin@proteancare.com'")
            print("export TEST_ADMIN_PASSWORD='admin123'")
            return False
        
        # 2. Substituir conftest.py
        conftest_path = os.path.join(self.base_path, "tests", "conftest.py")
        conftest_fixed_path = os.path.join(self.base_path, "tests", "conftest_fixed.py")
        
        if os.path.exists(conftest_fixed_path):
            if os.path.exists(conftest_path):
                os.rename(conftest_path, conftest_path + ".backup")
            os.rename(conftest_fixed_path, conftest_path)
            print("✅ conftest.py atualizado")
        
        # 3. Instalar dependências
        print("📦 Instalando dependências...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "pytest-asyncio", "httpx", "pytest-cov"
        ], check=True)
        
        return True
    
    def run_connectivity_test(self):
        """Testa conectividade básica"""
        print("\n🔍 Testando conectividade...")
        
        try:
            # Teste de conexão com banco
            from sqlalchemy import create_engine
            engine = create_engine(os.getenv("TEST_DATABASE_URL"))
            with engine.connect() as conn:
                result = conn.execute("SELECT 1 as test")
                print("✅ Conexão com banco OK")
                
            # Teste de autenticação
            import requests
            login_data = {
                "username": os.getenv("TEST_ADMIN_EMAIL"),
                "password": os.getenv("TEST_ADMIN_PASSWORD")
            }
            
            # Assumindo que o servidor está rodando
            auth_response = requests.post(
                "http://localhost:8000/api/v1/auth/login", 
                json=login_data,
                timeout=10
            )
            
            if auth_response.status_code == 200:
                print("✅ Autenticação OK")
            else:
                print(f"⚠️ Autenticação falhou: {auth_response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro de conectividade: {str(e)}")
            return False
            
        return True
    
    def run_tests(self):
        """Executa os testes"""
        print("\n🧪 Executando testes...")
        
        # Comandos de teste em ordem de prioridade
        test_commands = [
            {
                "name": "Fluxo Completo CRUD",
                "cmd": ["pytest", "tests/api/test_company_complete_flow.py", "-v", "-s"],
                "critical": True
            },
            {
                "name": "Testes de Autenticação", 
                "cmd": ["pytest", "tests/api/test_auth.py", "-v"],
                "critical": True
            },
            {
                "name": "Testes de Empresas",
                "cmd": ["pytest", "tests/api/test_company*.py", "-v", "--tb=short"],
                "critical": False
            },
            {
                "name": "Testes LGPD",
                "cmd": ["pytest", "tests/api/test_lgpd.py", "-v", "--tb=short"],
                "critical": False
            }
        ]
        
        results = {}
        
        for test_group in test_commands:
            print(f"\n📋 Executando: {test_group['name']}")
            
            try:
                result = subprocess.run(
                    test_group["cmd"],
                    cwd=self.base_path,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutos por grupo
                )
                
                results[test_group["name"]] = {
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                }
                
                if result.returncode == 0:
                    print(f"✅ {test_group['name']}: SUCESSO")
                else:
                    print(f"❌ {test_group['name']}: FALHOU")
                    if test_group["critical"]:
                        print("🚨 Teste crítico falhou - parando execução")
                        break
                        
            except subprocess.TimeoutExpired:
                print(f"⏰ {test_group['name']}: TIMEOUT")
                results[test_group["name"]] = {
                    "returncode": -1,
                    "error": "timeout",
                    "success": False
                }
                
            except Exception as e:
                print(f"💥 {test_group['name']}: ERRO - {str(e)}")
                results[test_group["name"]] = {
                    "returncode": -1,
                    "error": str(e),
                    "success": False
                }
        
        self.test_results = results
        return results
    
    def generate_report(self):
        """Gera relatório detalhado"""
        print("\n📊 Gerando relatório...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "database_url": os.getenv("TEST_DATABASE_URL", "").split("@")[1] if "@" in os.getenv("TEST_DATABASE_URL", "") else "N/A",
                "admin_email": os.getenv("TEST_ADMIN_EMAIL", "N/A")
            },
            "results": self.test_results,
            "summary": {
                "total_groups": len(self.test_results),
                "successful_groups": sum(1 for r in self.test_results.values() if r.get("success", False)),
                "failed_groups": sum(1 for r in self.test_results.values() if not r.get("success", False))
            }
        }
        
        # Salvar relatório
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(self.base_path, "tests", report_file)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Relatório salvo em: {report_path}")
        
        # Resumo no console
        print("\n" + "="*60)
        print("📊 RESUMO EXECUTIVO")
        print("="*60)
        print(f"⏰ Data/Hora: {report['timestamp']}")
        print(f"🎯 Grupos de Teste: {report['summary']['total_groups']}")
        print(f"✅ Sucessos: {report['summary']['successful_groups']}")
        print(f"❌ Falhas: {report['summary']['failed_groups']}")
        
        success_rate = (report['summary']['successful_groups'] / report['summary']['total_groups']) * 100 if report['summary']['total_groups'] > 0 else 0
        print(f"📈 Taxa de Sucesso: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 PLATAFORMA VIÁVEL - Taxa de sucesso excelente!")
        elif success_rate >= 60:
            print("⚠️ PLATAFORMA PARCIALMENTE VIÁVEL - Necessita ajustes")
        else:
            print("🚨 PLATAFORMA NÃO VIÁVEL - Correções críticas necessárias")
        
        return report

def main():
    """Função principal"""
    print("🚀 PLATAFORMA DE TESTES AUTOMATIZADOS")
    print("="*50)
    
    setup = TestEnvironmentSetup()
    
    # 1. Configurar ambiente
    if not setup.setup_environment():
        print("❌ Falha na configuração do ambiente")
        sys.exit(1)
    
    # 2. Testar conectividade
    if not setup.run_connectivity_test():
        print("❌ Falha na conectividade")
        sys.exit(1)
    
    # 3. Executar testes
    results = setup.run_tests()
    
    # 4. Gerar relatório
    report = setup.generate_report()
    
    # 5. Determinar código de saída
    success_rate = (report['summary']['successful_groups'] / report['summary']['total_groups']) * 100 if report['summary']['total_groups'] > 0 else 0
    
    if success_rate >= 60:
        sys.exit(0)  # Sucesso
    else:
        sys.exit(1)  # Falha

if __name__ == "__main__":
    main()
