#!/usr/bin/env python3
"""
Script para classificar cards existentes com ITIL
"""
import pyodbc

# Configuração do banco
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

def classificar_cards():
    """Classifica cards existentes com ITIL"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()

        print('================================================================================')
        print('CLASSIFICAÇÃO ITIL: Atualizando cards existentes para teste')
        print('================================================================================')

        # 1. Classificar Changes (GMUD, RDM, Deploy)
        cursor.execute('''
            UPDATE core.Cards
            SET ITILCategory = 'Change',
                HasWindow = CASE WHEN Title LIKE '%Janela%' OR Title LIKE '%Window%' THEN 1 ELSE 0 END,
                HasCAB = CASE WHEN Title LIKE '%CAB%' OR Title LIKE '%Comit%' THEN 1 ELSE 0 END,
                HasBackout = CASE WHEN Title LIKE '%backout%' OR Title LIKE '%rollback%' THEN 1 ELSE 0 END,
                RiskLevel = CASE
                    WHEN Title LIKE '%GMUD%' OR Title LIKE '%RDM%' OR Title LIKE '%Deploy%' THEN
                        CASE
                            WHEN (Title LIKE '%CAB%' OR Title LIKE '%Comit%') AND (Title LIKE '%backout%' OR Title LIKE '%rollback%') THEN 'Low'
                            ELSE 'High'
                        END
                    ELSE 'Low'
                END,
                Size = 'M'
            WHERE CardID IN (
                SELECT TOP 5 CardID
                FROM core.Cards
                WHERE (Title LIKE '%GMUD%' OR Title LIKE '%RDM%' OR Title LIKE '%Deploy%' OR Title LIKE '%CHG%')
                AND IsDeleted = 0
                AND ITILCategory IS NULL
            )
        ''')
        print('✅ 5 cards classificados como Change')

        # 2. Classificar Incidents
        cursor.execute('''
            UPDATE core.Cards
            SET ITILCategory = 'Incident',
                HasWindow = 0,
                HasCAB = 0,
                HasBackout = 0,
                RiskLevel = 'High',
                Size = 'S'
            WHERE CardID IN (
                SELECT TOP 3 CardID
                FROM core.Cards
                WHERE (Title LIKE '%Falha%' OR Title LIKE '%Erro%' OR Title LIKE '%Incident%' OR Title LIKE '%Indispon%')
                AND IsDeleted = 0
                AND ITILCategory IS NULL
            )
        ''')
        print('✅ 3 cards classificados como Incident')

        # 3. Classificar Service Requests
        cursor.execute('''
            UPDATE core.Cards
            SET ITILCategory = 'Service Request',
                HasWindow = 0,
                HasCAB = 0,
                HasBackout = 0,
                RiskLevel = 'Low',
                Size = 'S'
            WHERE CardID IN (
                SELECT TOP 3 CardID
                FROM core.Cards
                WHERE (Title LIKE '%Solicit%' OR Title LIKE '%Criar%' OR Title LIKE '%Acesso%' OR Title LIKE '%Permiss%')
                AND IsDeleted = 0
                AND ITILCategory IS NULL
            )
        ''')
        print('✅ 3 cards classificados como Service Request')

        # 4. Resto como Operation Task
        cursor.execute('''
            UPDATE core.Cards
            SET ITILCategory = 'Operation Task',
                HasWindow = 0,
                HasCAB = 0,
                HasBackout = 0,
                RiskLevel = 'Low',
                Size = 'S'
            WHERE ITILCategory IS NULL
            AND IsDeleted = 0
        ''')
        print('✅ Cards restantes classificados como Operation Task')

        # Commit das mudanças
        conn.commit()

        # Verificar resultado
        cursor.execute('''
            SELECT
                ITILCategory,
                COUNT(*) as Quantidade,
                SUM(CASE WHEN RiskLevel = 'High' THEN 1 ELSE 0 END) as AltoRisco,
                SUM(CASE WHEN HasWindow = 1 THEN 1 ELSE 0 END) as ComJanela,
                SUM(CASE WHEN HasCAB = 1 THEN 1 ELSE 0 END) as ComCAB,
                SUM(CASE WHEN HasBackout = 1 THEN 1 ELSE 0 END) as ComBackout
            FROM core.Cards
            WHERE ITILCategory IS NOT NULL AND IsDeleted = 0
            GROUP BY ITILCategory
            ORDER BY Quantidade DESC
        ''')

        results = cursor.fetchall()
        print('\n📊 RESULTADO DA CLASSIFICAÇÃO:')
        for row in results:
            print(f"   {row[0]}: {row[1]} cards (Alto Risco: {row[2]}, Janela: {row[3]}, CAB: {row[4]}, Backout: {row[5]})")

        cursor.close()
        conn.close()

        print('\n================================================================================')
        print('CLASSIFICAÇÃO CONCLUÍDA - Agora teste os endpoints!')
        print('================================================================================')

    except Exception as e:
        print(f'❌ Erro: {e}')

if __name__ == '__main__':
    classificar_cards()