#!/usr/bin/env python3
"""
Script para debug do Lead Time negativo no Kanban Analytics
"""

import pyodbc
import os
from datetime import datetime

# Configurações do banco (ajuste conforme necessário)
DB_CONFIG = {
    'server': 'localhost',
    'database': 'pro_team_care',
    'username': 'sa',
    'password': 'YourPassword123!',
    'driver': '{ODBC Driver 18 for SQL Server}'
}

def get_connection():
    """Conecta ao banco de dados"""
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def debug_lead_time():
    """Debug do lead time negativo"""

    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("🔍 DEBUG: Lead Time Negativo")
        print("=" * 80)

        # Query 1: Cards concluídos no período com lead time mais negativo
        query1 = """
        SELECT TOP 10
            c.CardID,
            c.Title,
            c.CreatedAt,
            c.CompletedDate,
            DATEDIFF(SECOND, c.CreatedAt, c.CompletedDate) as LeadTimeSeconds,
            DATEDIFF(MINUTE, c.CreatedAt, c.CompletedDate) as LeadTimeMinutes,
            CASE WHEN c.CompletedDate < c.CreatedAt THEN '❌ PROBLEMA: Conclusão ANTES da criação!' ELSE '✅ OK' END as Status
        FROM core.Cards c
        WHERE c.CompanyID = 1
          AND c.IsDeleted = 0
          AND c.CompletedDate IS NOT NULL
          AND CAST(c.CompletedDate AS DATE) BETWEEN '2025-11-01' AND '2025-11-30'
        ORDER BY DATEDIFF(SECOND, c.CreatedAt, c.CompletedDate) ASC
        """

        print("\n📊 1. Cards concluídos no período (ordenados por lead time mais negativo):")
        cursor.execute(query1)
        rows = cursor.fetchall()

        if not rows:
            print("Nenhum card encontrado no período.")
        else:
            for row in rows:
                print(f"\nCard ID: {row[0]}")
                print(f"Título: {row[1]}")
                print(f"Criado: {row[2]}")
                print(f"Concluído: {row[3]}")
                print(f"Lead Time: {row[4]} segundos ({row[5]} minutos)")
                print(f"Status: {row[6]}")

        # Query 2: Verificar se há cards com CreatedAt no futuro
        query2 = """
        SELECT TOP 5
            CardID,
            Title,
            CreatedAt,
            CompletedDate,
            GETDATE() as Now,
            DATEDIFF(HOUR, CreatedAt, GETDATE()) as HoursInFuture
        FROM core.Cards
        WHERE CompanyID = 1
          AND IsDeleted = 0
          AND CreatedAt > GETDATE()
        ORDER BY CreatedAt DESC
        """

        print("\n\n⏰ 2. Cards com data de criação no futuro:")
        cursor.execute(query2)
        rows = cursor.fetchall()

        if not rows:
            print("Nenhum card com data de criação no futuro.")
        else:
            for row in rows:
                print(f"\nCard ID: {row[0]}")
                print(f"Título: {row[1]}")
                print(f"Criado: {row[2]} (em {row[5]} horas no futuro)")
                print(f"Concluído: {row[3]}")
                print(f"Agora: {row[4]}")

        # Query 3: Verificar histórico de movimentos dos cards problemáticos
        query3 = """
        SELECT TOP 5
            c.CardID,
            c.Title,
            COUNT(cm.MovementID) as TotalMovements,
            MIN(cm.LogDate) as FirstMovement,
            MAX(cm.LogDate) as LastMovement
        FROM core.Cards c
        LEFT JOIN core.CardMovements cm ON c.CardID = cm.CardID
        WHERE c.CompanyID = 1
          AND c.IsDeleted = 0
          AND c.CompletedDate IS NOT NULL
          AND c.CreatedAt > c.CompletedDate
        GROUP BY c.CardID, c.Title
        ORDER BY c.CardID
        """

        print("\n\n📈 3. Histórico de movimentos dos cards problemáticos:")
        cursor.execute(query3)
        rows = cursor.fetchall()

        if not rows:
            print("Nenhum card problemático encontrado.")
        else:
            for row in rows:
                print(f"\nCard ID: {row[0]}")
                print(f"Título: {row[1]}")
                print(f"Total de movimentos: {row[2]}")
                print(f"Primeiro movimento: {row[3]}")
                print(f"Último movimento: {row[4]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erro ao executar debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_lead_time()