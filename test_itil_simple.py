#!/usr/bin/env python3
"""
Script simples para testar dados ITIL no banco
"""
import pyodbc

# Configuração do banco (do .env)
DB_CONFIG = {
    'server': '192.168.11.84',
    'database': 'pro_team_care',
    'username': 'sa',
    'password': 'Jvc@1702',
    'driver': '{ODBC Driver 18 for SQL Server}',
    'TrustServerCertificate': 'yes',
    'timeout': 10
}

def conectar_banco():
    """Conecta ao banco"""
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"TrustServerCertificate={DB_CONFIG['TrustServerCertificate']};"
        f"Connection Timeout={DB_CONFIG['timeout']};"
    )
    return pyodbc.connect(conn_str)

def testar_itil():
    """Testa os dados ITIL implementados"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()

        print('================================================================================')
        print('TESTE: Classificação ITIL - Status Atual')
        print('================================================================================')

        # 1. Verificar se as colunas ITIL existem
        print('\n1. Verificando colunas ITIL na tabela core.Cards:')
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'core'
                AND TABLE_NAME = 'Cards'
                AND COLUMN_NAME IN ('ITILCategory', 'HasWindow', 'HasCAB', 'HasBackout', 'Size', 'RiskLevel')
            ORDER BY COLUMN_NAME
        """)
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                print(f"   ✅ {col[0]} ({col[1]}) - Nullable: {col[2]}")
        else:
            print("   ❌ Nenhuma coluna ITIL encontrada!")

        # 2. Verificar se a view existe
        print('\n2. Verificando se a view analytics.vw_ITILReport existe:')
        cursor.execute("""
            SELECT COUNT(*)
            FROM sys.views v
            JOIN sys.schemas s ON v.schema_id = s.schema_id
            WHERE s.name = 'analytics' AND v.name = 'vw_ITILReport'
        """)
        if cursor.fetchone()[0] > 0:
            print('   ✅ View analytics.vw_ITILReport existe')
        else:
            print('   ❌ View analytics.vw_ITILReport NÃO existe')

        # 3. Contar cards com classificação ITIL
        print('\n3. Cards com classificação ITIL:')
        cursor.execute("""
            SELECT COUNT(*) as TotalCardsClassificados
            FROM core.Cards
            WHERE ITILCategory IS NOT NULL AND IsDeleted = 0
        """)
        total = cursor.fetchone()[0]
        print(f"   📊 Total: {total} cards classificados")

        # 4. Distribuição por categoria ITIL
        print('\n4. Distribuição por categoria ITIL:')
        cursor.execute("""
            SELECT
                ITILCategory,
                COUNT(*) as Quantidade,
                CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as Percentual
            FROM core.Cards
            WHERE ITILCategory IS NOT NULL AND IsDeleted = 0
            GROUP BY ITILCategory
            ORDER BY Quantidade DESC
        """)
        categories = cursor.fetchall()
        if categories:
            for cat, qty, pct in categories:
                print(f"   {cat}: {qty} cards ({pct}%)")
        else:
            print("   ⚠️  Nenhuma categoria encontrada")

        # 5. Verificar metadados ITIL
        print('\n5. Metadados ITIL (Window/CAB/Backout):')
        cursor.execute("""
            SELECT
                SUM(CASE WHEN HasWindow = 1 THEN 1 ELSE 0 END) as ComJanela,
                SUM(CASE WHEN HasCAB = 1 THEN 1 ELSE 0 END) as ComCAB,
                SUM(CASE WHEN HasBackout = 1 THEN 1 ELSE 0 END) as ComBackout,
                SUM(CASE WHEN RiskLevel = 'High' THEN 1 ELSE 0 END) as AltoRisco
            FROM core.Cards
            WHERE ITILCategory IS NOT NULL AND IsDeleted = 0
        """)
        meta = cursor.fetchone()
        if meta:
            print(f"   🪟 Com Janela: {meta[0] or 0}")
            print(f"   👥 Com CAB: {meta[1] or 0}")
            print(f"   🔄 Com Backout: {meta[2] or 0}")
            print(f"   ⚠️  Alto Risco: {meta[3] or 0}")

        # 6. Testar a view vw_ITILReport
        print('\n6. Testando view analytics.vw_ITILReport:')
        cursor.execute("""
            SELECT TOP 3
                CardID,
                ExternalCardID,
                LEFT(Title, 50) as Title,
                ITILCategory,
                RiskLevel,
                HasWindow,
                HasCAB,
                HasBackout,
                CompletedDate
            FROM analytics.vw_ITILReport
            WHERE CompletedDate >= '2025-01-01'
            ORDER BY CompletedDate DESC
        """)
        cards = cursor.fetchall()
        if cards:
            for card in cards:
                print(f"   📋 {card[1]}: {card[2]}... [{card[3]}] Risco:{card[4]}")
        else:
            print("   ⚠️  Nenhum card encontrado na view")

        print('\n================================================================================')
        print('TESTE CONCLUÍDO')
        print('================================================================================')

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erro ao conectar/testar: {e}")

if __name__ == '__main__':
    testar_itil()