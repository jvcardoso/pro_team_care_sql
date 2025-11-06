#!/usr/bin/env python3
"""
Script para testar as estatísticas do Kanban Board.
Executa queries SQL para verificar se os dados estão corretos.
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

# Configurações do banco
DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 18 for SQL Server')
DB_SERVER = os.getenv('DB_SERVER', '192.168.11.84')
DB_PORT = int(os.getenv('DB_PORT', '1433'))
DB_NAME = os.getenv('DB_NAME', 'pro_team_care')
DB_USER = os.getenv('DB_USER', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'SuaSenhaAqui')

def create_database_url():
    """Cria a URL de conexão do banco"""
    from urllib.parse import quote
    driver = DB_DRIVER.replace(" ", "+")
    encoded_password = quote(DB_PASSWORD, safe='')
    return f"mssql+aioodbc://{DB_USER}:{encoded_password}@{DB_SERVER}:{DB_PORT}/{DB_NAME}?driver={driver}&TrustServerCertificate=yes"

async def test_kanban_stats():
    """Testa as estatísticas do kanban"""

    print("=" * 80)
    print("TESTE DAS ESTATÍSTICAS DO KANBAN BOARD")
    print("=" * 80)

    # Criar engine
    database_url = create_database_url()
    engine = create_async_engine(database_url, echo=False)

    try:
        async with AsyncSession(engine) as session:
            print("\n1. VERIFICANDO SE A STORED PROCEDURE EXISTE...")
            result = await session.execute(text("""
                SELECT COUNT(*) as exists_count
                FROM sys.objects
                WHERE object_id = OBJECT_ID('[core].[sp_get_kanban_statistics]')
                AND type = 'P'
            """))
            exists = result.scalar()
            if exists:
                print("✅ Stored Procedure [core].[sp_get_kanban_statistics] existe.")
            else:
                print("❌ Stored Procedure [core].[sp_get_kanban_statistics] NÃO existe!")
                return

            print("\n2. VERIFICAÇÃO DIRETA DOS DADOS NAS TABELAS...")

            # Total de cards não deletados
            result = await session.execute(text("""
                SELECT COUNT(c.CardID) AS TotalCards_Diretamente
                FROM [core].[Cards] c
                WHERE c.IsDeleted = 0
            """))
            total_direct = result.scalar()
            print(f"Total de cards (direto): {total_direct}")

            # Cards por coluna
            result = await session.execute(text("""
                SELECT
                    cc.ColumnName,
                    COUNT(c.CardID) AS Quantidade,
                    MIN(cc.DisplayOrder) AS DisplayOrder
                FROM
                    [core].[Cards] c
                INNER JOIN
                    [core].[CardColumns] cc ON c.ColumnID = cc.ColumnID AND c.CompanyID = cc.CompanyID
                WHERE
                    c.IsDeleted = 0
                GROUP BY
                    cc.ColumnName
                ORDER BY
                    MIN(cc.DisplayOrder)
            """))
            rows = result.fetchall()
            print("Cards por coluna:")
            for row in rows:
                print(f"  - {row.ColumnName}: {row.Quantidade}")

            print("\n3. EXECUTANDO A STORED PROCEDURE...")

            # Executar stored procedure (usando CompanyID = 1 como exemplo)
            result = await session.execute(text("""
                EXEC [core].[sp_get_kanban_statistics] @CompanyID = 1
            """))
            stats = result.fetchone()

            if stats:
                print("Resultados da Stored Procedure:")
                print(f"  - TotalCards: {stats.TotalCards}")
                print(f"  - InProgressCards: {stats.InProgressCards}")
                print(f"  - CompletedCards: {stats.CompletedCards}")
            else:
                print("❌ Stored Procedure não retornou resultados!")

            print("\n4. VERIFICAÇÃO DETALHADA POR EMPRESA...")

            # Empresas com dados no kanban (sem join com tabela Companies)
            result = await session.execute(text("""
                SELECT
                    CompanyID,
                    COUNT(CardID) AS TotalCards
                FROM
                    [core].[Cards]
                WHERE
                    IsDeleted = 0
                GROUP BY
                    CompanyID
                ORDER BY
                    CompanyID
            """))
            companies = result.fetchall()
            print("Empresas com dados no Kanban:")
            for company in companies:
                print(f"  - Empresa ID {company.CompanyID}: {company.TotalCards} cards")

            print("\n5. COLUNAS DISPONÍVEIS NO SISTEMA...")

            # Colunas disponíveis
            result = await session.execute(text("""
                SELECT
                    ColumnID,
                    ColumnName,
                    DisplayOrder,
                    IsActive,
                    CompanyID
                FROM
                    [core].[CardColumns]
                WHERE
                    IsActive = 1
                ORDER BY
                    CompanyID, DisplayOrder
            """))
            columns = result.fetchall()
            print("Colunas ativas:")
            for col in columns:
                print(f"  - ID {col.ColumnID}: '{col.ColumnName}' (Empresa: {col.CompanyID}, Ordem: {col.DisplayOrder})")

            print("\n6. VERIFICAÇÃO DO PROBLEMA IDENTIFICADO...")

            # Verificar se existem colunas "Em Andamento" e "Concluído"
            result = await session.execute(text("""
                SELECT ColumnName
                FROM [core].[CardColumns]
                WHERE ColumnName IN ('Em Andamento', 'Concluído')
                AND IsActive = 1
            """))
            special_columns = result.fetchall()
            if special_columns:
                print("Colunas especiais encontradas:")
                for col in special_columns:
                    print(f"  - '{col.ColumnName}'")
            else:
                print("❌ PROBLEMA: As colunas 'Em Andamento' e 'Concluído' não existem!")
                print("   A stored procedure está procurando por essas colunas, mas elas não foram encontradas.")
                print("   Colunas existentes:", [col.ColumnName for col in columns])

    except Exception as e:
        print(f"❌ ERRO: {e}")
        print("Verifique se:")
        print("  - O banco está rodando")
        print("  - As credenciais estão corretas no .env")
        print("  - O driver ODBC está instalado")

    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_kanban_stats())