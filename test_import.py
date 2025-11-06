#!/usr/bin/env python3
"""
Teste direto da importação de CSV do BusinessMap
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def preprocess_multiline_csv(content: str, expected_columns: int = 18) -> str:
    """
    Junta linhas que fazem parte de campos multilinha.
    """
    lines = content.split('\n')
    processed_lines = []
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
            
        delimiter_count = line.count(';')
        
        if i == 0:
            # Cabeçalho
            processed_lines.append(line)
            print(f"📋 Cabeçalho: {delimiter_count} delimitadores")
        elif delimiter_count >= expected_columns - 1:
            # Linha completa
            processed_lines.append(line)
            print(f"✅ Linha {len(processed_lines)}: {delimiter_count} delimitadores - COMPLETA")
        else:
            # Linha incompleta
            if processed_lines:
                processed_lines[-1] += ' ' + line.strip()
                print(f"🔄 Linha {i}: {delimiter_count} delimitadores - JUNTADA com anterior")
    
    return '\n'.join(processed_lines)


def test_csv_preprocessing():
    """Testa o pré-processamento do CSV"""
    
    csv_file = 'docs/dasa-20251105161442-BPX.csv'
    
    print("=" * 80)
    print("🧪 TESTE DE PRÉ-PROCESSAMENTO CSV")
    print("=" * 80)
    
    # Ler arquivo
    with open(csv_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n📁 Arquivo: {csv_file}")
    print(f"📄 Tamanho: {len(content)} bytes")
    print(f"📄 Linhas originais: {len(content.split(chr(10)))}")
    
    # Pré-processar
    print("\n🔄 Pré-processando...")
    processed = preprocess_multiline_csv(content, expected_columns=18)
    
    print(f"\n✅ Pré-processamento concluído")
    print(f"📄 Linhas processadas: {len(processed.split(chr(10)))}")
    
    # Analisar resultado
    import csv
    import io
    
    csv_reader = csv.reader(io.StringIO(processed), delimiter=';')
    
    header = next(csv_reader)
    print(f"\n📋 Cabeçalho: {len(header)} colunas")
    print(f"   Colunas: {header[:5]}...")
    
    rows = list(csv_reader)
    print(f"\n📊 Total de linhas de dados: {len(rows)}")
    
    # Verificar linhas
    valid_rows = 0
    invalid_rows = 0
    
    for i, row in enumerate(rows, 1):
        if len(row) >= 17:
            valid_rows += 1
        else:
            invalid_rows += 1
            print(f"❌ Linha {i}: {len(row)} colunas - INVÁLIDA")
            if i <= 5:  # Mostrar primeiras 5 inválidas
                print(f"   Dados: {row[:3]}...")
    
    print(f"\n📊 RESULTADO:")
    print(f"   ✅ Linhas válidas: {valid_rows}")
    print(f"   ❌ Linhas inválidas: {invalid_rows}")
    print(f"   📈 Taxa de sucesso: {(valid_rows/len(rows)*100):.1f}%")
    
    if valid_rows == len(rows):
        print("\n🎉 SUCESSO! Todas as linhas foram processadas corretamente!")
        return True
    else:
        print(f"\n⚠️  FALHA! {invalid_rows} linhas ainda estão inválidas")
        return False


if __name__ == '__main__':
    success = test_csv_preprocessing()
    sys.exit(0 if success else 1)
