"""
Script para analisar banco antigo e extrair estrutura de tabelas
para os itens da Fase 2.

Itens a analisar:
1. Sessões Seguras (switch profile, impersonate)
2. Dashboard (stats, activity)
3. Notificações
4. Menus Dinâmicos
"""
import pyodbc
import json
from datetime import datetime

# Configuração de conexão - BANCO ATUAL (pro_team_care)
# Se houver banco antigo separado, ajustar database
OLD_DB_CONFIG = {
    'server': '192.168.11.83',
    'database': 'pro_team_care',  # Banco atual - ajustar se houver banco antigo separado
    'username': 'sa',
    'password': 'SuaSenha',  # Ajustar conforme .env
    'driver': '{ODBC Driver 18 for SQL Server}',
    'TrustServerCertificate': 'yes',
    'timeout': 5  # Timeout de 5 segundos
}

def conectar_banco_antigo():
    """Conecta ao banco antigo"""
    conn_str = (
        f"DRIVER={OLD_DB_CONFIG['driver']};"
        f"SERVER={OLD_DB_CONFIG['server']};"
        f"DATABASE={OLD_DB_CONFIG['database']};"
        f"UID={OLD_DB_CONFIG['username']};"
        f"PWD={OLD_DB_CONFIG['password']};"
        f"TrustServerCertificate={OLD_DB_CONFIG['TrustServerCertificate']};"
        f"Connection Timeout={OLD_DB_CONFIG['timeout']};"
    )
    return pyodbc.connect(conn_str)

def listar_schemas(conn):
    """Lista todos os schemas do banco"""
    query = """
    SELECT DISTINCT TABLE_SCHEMA
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_SCHEMA
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]

def buscar_tabelas_relacionadas(conn, palavras_chave):
    """Busca tabelas que contenham palavras-chave"""
    placeholders = ','.join(['?' for _ in palavras_chave])
    query = f"""
    SELECT 
        TABLE_SCHEMA,
        TABLE_NAME,
        TABLE_TYPE
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    AND (
        {' OR '.join([f"TABLE_NAME LIKE '%' + ? + '%'" for _ in palavras_chave])}
    )
    ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    cursor = conn.cursor()
    cursor.execute(query, palavras_chave)
    return cursor.fetchall()

def obter_estrutura_tabela(conn, schema, tabela):
    """Obtém estrutura completa de uma tabela"""
    query = """
    SELECT 
        c.COLUMN_NAME,
        c.DATA_TYPE,
        c.CHARACTER_MAXIMUM_LENGTH,
        c.IS_NULLABLE,
        c.COLUMN_DEFAULT,
        CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 'YES' ELSE 'NO' END as IS_PRIMARY_KEY,
        CASE WHEN fk.COLUMN_NAME IS NOT NULL THEN 'YES' ELSE 'NO' END as IS_FOREIGN_KEY,
        fk.REFERENCED_TABLE_SCHEMA,
        fk.REFERENCED_TABLE_NAME,
        fk.REFERENCED_COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS c
    LEFT JOIN (
        SELECT ku.TABLE_SCHEMA, ku.TABLE_NAME, ku.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
            ON tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
            AND tc.TABLE_SCHEMA = ku.TABLE_SCHEMA
        WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
    ) pk ON c.TABLE_SCHEMA = pk.TABLE_SCHEMA 
        AND c.TABLE_NAME = pk.TABLE_NAME 
        AND c.COLUMN_NAME = pk.COLUMN_NAME
    LEFT JOIN (
        SELECT 
            ku.TABLE_SCHEMA,
            ku.TABLE_NAME,
            ku.COLUMN_NAME,
            ku2.TABLE_SCHEMA as REFERENCED_TABLE_SCHEMA,
            ku2.TABLE_NAME as REFERENCED_TABLE_NAME,
            ku2.COLUMN_NAME as REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
            ON rc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku2
            ON rc.UNIQUE_CONSTRAINT_NAME = ku2.CONSTRAINT_NAME
    ) fk ON c.TABLE_SCHEMA = fk.TABLE_SCHEMA 
        AND c.TABLE_NAME = fk.TABLE_NAME 
        AND c.COLUMN_NAME = fk.COLUMN_NAME
    WHERE c.TABLE_SCHEMA = ?
    AND c.TABLE_NAME = ?
    ORDER BY c.ORDINAL_POSITION
    """
    cursor = conn.cursor()
    cursor.execute(query, (schema, tabela))
    return cursor.fetchall()

def contar_registros(conn, schema, tabela):
    """Conta registros em uma tabela"""
    try:
        query = f"SELECT COUNT(*) FROM [{schema}].[{tabela}]"
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()[0]
    except:
        return 0

def obter_sample_data(conn, schema, tabela, limit=5):
    """Obtém amostra de dados da tabela"""
    try:
        query = f"SELECT TOP {limit} * FROM [{schema}].[{tabela}]"
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        return {
            'columns': columns,
            'rows': [[str(cell) if cell is not None else None for cell in row] for row in rows]
        }
    except Exception as e:
        return {'error': str(e)}

def analisar_item(conn, item_nome, palavras_chave):
    """Analisa um item específico da Fase 2"""
    print(f"\n{'='*80}")
    print(f"🔍 ANALISANDO: {item_nome}")
    print(f"{'='*80}")
    
    tabelas = buscar_tabelas_relacionadas(conn, palavras_chave)
    
    resultado = {
        'item': item_nome,
        'palavras_chave': palavras_chave,
        'tabelas_encontradas': [],
        'timestamp': datetime.now().isoformat()
    }
    
    if not tabelas:
        print(f"❌ Nenhuma tabela encontrada com as palavras-chave: {palavras_chave}")
        return resultado
    
    print(f"\n✅ Encontradas {len(tabelas)} tabela(s):\n")
    
    for schema, tabela, tipo in tabelas:
        print(f"📋 [{schema}].[{tabela}]")
        
        # Estrutura
        estrutura = obter_estrutura_tabela(conn, schema, tabela)
        
        # Contagem
        count = contar_registros(conn, schema, tabela)
        print(f"   📊 Registros: {count}")
        
        # Sample
        sample = obter_sample_data(conn, schema, tabela, 3)
        
        tabela_info = {
            'schema': schema,
            'nome': tabela,
            'tipo': tipo,
            'total_registros': count,
            'colunas': []
        }
        
        print(f"   📝 Colunas:")
        for col in estrutura:
            col_name, data_type, max_len, nullable, default, is_pk, is_fk, ref_schema, ref_table, ref_col = col
            
            col_info = {
                'nome': col_name,
                'tipo': data_type,
                'tamanho': max_len,
                'nullable': nullable,
                'default': default,
                'primary_key': is_pk == 'YES',
                'foreign_key': is_fk == 'YES'
            }
            
            if is_fk == 'YES':
                col_info['referencia'] = f"[{ref_schema}].[{ref_table}].[{ref_col}]"
            
            tabela_info['colunas'].append(col_info)
            
            # Print formatado
            tipo_display = f"{data_type}"
            if max_len:
                tipo_display += f"({max_len})"
            
            flags = []
            if is_pk == 'YES':
                flags.append('PK')
            if is_fk == 'YES':
                flags.append(f'FK→{ref_table}')
            if nullable == 'NO':
                flags.append('NOT NULL')
            
            flags_str = f" [{', '.join(flags)}]" if flags else ""
            print(f"      • {col_name}: {tipo_display}{flags_str}")
        
        # Adicionar sample ao resultado
        if 'error' not in sample:
            tabela_info['sample_data'] = sample
        
        resultado['tabelas_encontradas'].append(tabela_info)
        print()
    
    return resultado

def main():
    """Função principal"""
    print("="*80)
    print("🔍 ANÁLISE DO BANCO ANTIGO - FASE 2")
    print("="*80)
    print(f"Servidor: {OLD_DB_CONFIG['server']}")
    print(f"Banco: {OLD_DB_CONFIG['database']}")
    print()
    
    try:
        # Conectar
        print("📡 Conectando ao banco antigo...")
        conn = conectar_banco_antigo()
        print("✅ Conectado com sucesso!\n")
        
        # Listar schemas
        print("📂 Schemas disponíveis:")
        schemas = listar_schemas(conn)
        for schema in schemas:
            print(f"   • {schema}")
        print()
        
        resultados = []
        
        # Item 5: Sessões Seguras
        resultado = analisar_item(
            conn,
            "ITEM 5: Sessões Seguras",
            ['session', 'sessao', 'impersonate', 'personificar', 'switch', 'profile']
        )
        resultados.append(resultado)
        
        # Item 6: Dashboard
        resultado = analisar_item(
            conn,
            "ITEM 6: Dashboard",
            ['dashboard', 'stats', 'statistics', 'activity', 'atividade', 'log', 'audit']
        )
        resultados.append(resultado)
        
        # Item 7: Notificações
        resultado = analisar_item(
            conn,
            "ITEM 7: Notificações",
            ['notification', 'notificacao', 'notificacoes', 'alert', 'alerta']
        )
        resultados.append(resultado)
        
        # Item 8: Menus Dinâmicos
        resultado = analisar_item(
            conn,
            "ITEM 8: Menus Dinâmicos",
            ['menu', 'menus', 'navigation', 'navegacao']
        )
        resultados.append(resultado)
        
        # Salvar resultados em JSON
        output_file = 'analise_banco_antigo_fase2_resultado.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*80)
        print(f"✅ ANÁLISE CONCLUÍDA!")
        print(f"📄 Resultado salvo em: {output_file}")
        print("="*80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
