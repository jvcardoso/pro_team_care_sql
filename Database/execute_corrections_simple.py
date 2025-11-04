#!/usr/bin/env python3
"""
Script simplificado para executar as correções no banco de dados.
Uso: python3 execute_corrections_simple.py [senha]
"""
import subprocess
import sys
from pathlib import Path

# Configurações do servidor
SERVER = "192.168.11.84"
DATABASE = "pro_team_care"
USERNAME = "sa"

def run_sql_script(script_path: str, password: str) -> bool:
    """Executa um script SQL usando sqlcmd."""
    cmd = [
        '/opt/mssql-tools18/bin/sqlcmd',
        '-S', SERVER,
        '-d', DATABASE,
        '-U', USERNAME,
        '-P', password,
        '-C',  # Trust server certificate
        '-i', script_path,
        '-b'   # Exit on error
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRO ao executar script:")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 execute_corrections_simple.py <senha>")
        print(f"Servidor: {SERVER}")
        print(f"Database: {DATABASE}")
        print(f"Usuário: {USERNAME}")
        sys.exit(1)
    
    password = sys.argv[1]
    script_dir = Path(__file__).parent
    
    print("=" * 70)
    print("  EXECUTANDO CORREÇÕES NO BANCO DE DADOS")
    print("=" * 70)
    print(f"Servidor: {SERVER}")
    print(f"Database: {DATABASE}")
    print(f"Usuário: {USERNAME}")
    print("=" * 70)
    print()
    
    scripts = [
        ("022_Create_Company_From_JSON.sql", "Stored Procedure sp_create_company_from_json"),
        ("023_Create_Complete_Company_View.sql", "View vw_complete_company_data")
    ]
    
    success_count = 0
    
    for script_file, description in scripts:
        script_path = script_dir / script_file
        
        if not script_path.exists():
            print(f"❌ Arquivo não encontrado: {script_path}")
            continue
        
        print(f"📄 Executando: {description}")
        print(f"   Arquivo: {script_file}")
        print("-" * 70)
        
        if run_sql_script(str(script_path), password):
            print(f"✅ {description} executada com sucesso!")
            success_count += 1
        else:
            print(f"❌ Falha ao executar {description}")
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
    
    sys.exit(0 if success_count == len(scripts) else 1)

if __name__ == "__main__":
    main()
