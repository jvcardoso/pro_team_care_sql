#!/usr/bin/env python3
"""
Script para executar as correções no banco de dados SQL Server.
Executa os scripts 022 e 023 em ordem.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_sql_script(script_path: str, server: str, database: str, username: str, password: str) -> bool:
    """Executa um script SQL usando sqlcmd."""
    cmd = [
        '/opt/mssql-tools18/bin/sqlcmd',
        '-S', server,
        '-d', database,
        '-U', username,
        '-P', password,
        '-C',  # Trust server certificate
        '-i', script_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRO: {e.stderr}")
        return False

def main():
    print("=" * 70)
    print("  EXECUTANDO CORREÇÕES NO BANCO DE DADOS")
    print("=" * 70)
    print()
    
    # Configurações do servidor
    SERVER = "192.168.11.84"
    DATABASE = "pro_team_care"
    USERNAME = "sa"
    
    # Solicitar senha
    import getpass
    PASSWORD = getpass.getpass(f"Digite a senha para {USERNAME}@{SERVER}: ")
    
    # Diretório dos scripts
    script_dir = Path(__file__).parent
    
    scripts = [
        ("022_Create_Company_From_JSON.sql", "Stored Procedure"),
        ("023_Create_Complete_Company_View.sql", "View")
    ]
    
    success_count = 0
    
    for script_file, description in scripts:
        script_path = script_dir / script_file
        
        if not script_path.exists():
            print(f"❌ Arquivo não encontrado: {script_path}")
            continue
        
        print(f"\n📄 Executando: {description}")
        print(f"   Arquivo: {script_file}")
        print("-" * 70)
        
        if run_sql_script(str(script_path), SERVER, DATABASE, USERNAME, PASSWORD):
            print(f"✅ {description} executada com sucesso!")
            success_count += 1
        else:
            print(f"❌ Falha ao executar {description}")
            response = input("\nContinuar com próximo script? (s/n): ")
            if response.lower() != 's':
                break
    
    print()
    print("=" * 70)
    if success_count == len(scripts):
        print("✅ TODAS AS CORREÇÕES FORAM APLICADAS COM SUCESSO!")
        print()
        print("📋 Próximos passos:")
        print("   1. Testar criação: cd ../backend && ./test_company_complete.sh")
        print("   2. Testar API: curl GET /api/v1/companies/complete-list")
    else:
        print(f"⚠️  {success_count}/{len(scripts)} scripts executados com sucesso")
    print("=" * 70)

if __name__ == "__main__":
    main()
