#!/usr/bin/env python3
"""
Converte CSV do BusinessMap para XLSX
Resolve problemas de multilinha e parsing
"""
import pandas as pd
import sys
import os

def convert_csv_to_xlsx(csv_file: str):
    """Converte CSV para XLSX"""
    
    if not os.path.exists(csv_file):
        print(f"❌ Arquivo não encontrado: {csv_file}")
        return False
    
    xlsx_file = csv_file.replace('.csv', '.xlsx')
    
    print("=" * 60)
    print("🔄 CONVERSÃO CSV → XLSX")
    print("=" * 60)
    
    try:
        print(f"\n📄 Lendo CSV: {csv_file}")
        df = pd.read_csv(
            csv_file, 
            delimiter=';', 
            encoding='utf-8-sig',
            on_bad_lines='skip'  # Pular linhas problemáticas
        )
        
        print(f"📊 Linhas lidas: {len(df)}")
        print(f"📋 Colunas: {len(df.columns)}")
        print(f"📋 Colunas: {list(df.columns[:5])}...")
        
        # Remover linhas completamente vazias
        df = df.dropna(how='all')
        print(f"📊 Linhas após limpeza: {len(df)}")
        
        print(f"\n💾 Salvando XLSX: {xlsx_file}")
        df.to_excel(xlsx_file, index=False, engine='openpyxl')
        
        print(f"✅ Conversão concluída!")
        print(f"📁 Arquivo criado: {xlsx_file}")
        print(f"📊 Tamanho: {os.path.getsize(xlsx_file)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conversão: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = 'docs/dasa-20251105161442-BPX.csv'
        print(f"ℹ️  Usando arquivo padrão: {csv_file}")
    
    success = convert_csv_to_xlsx(csv_file)
    sys.exit(0 if success else 1)
