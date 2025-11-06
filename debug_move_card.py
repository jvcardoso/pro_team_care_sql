#!/usr/bin/env python3
"""
Script para debugar o movimento de cards no kanban.
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
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Jvc@1702')

def create_database_url():
    """Cria a URL de conexão do banco"""
    from urllib.parse import quote
    driver = DB_DRIVER.replace(" ", "+")
    encoded_password = quote(DB_PASSWORD, safe='')
    return f"mssql+aioodbc://{DB_USER}:{encoded_password}@{DB_SERVER}:{DB_PORT}/{DB_NAME}?driver={driver}&TrustServerCertificate=yes"

async def debug_move_card():
    """Debug do movimento de card"""

    print("=" * 80)
    print("DEBUG: MOVIMENTO DE CARD NO KANBAN")
    print("=" * 80)

    # Criar engine
    database_url = create_database_url()
    engine = create_async_engine(database_url, echo=False)

    try:
        async with AsyncSession(engine) as session:
            print("\n1. VERIFICANDO SE O CARD EXISTE...")

            card_id = 2  # Card que está sendo movido
            result = await session.execute(text("""
                SELECT CardID, Title, ColumnID, DisplayOrder, IsDeleted
                FROM [core].[Cards]
                WHERE CardID = :card_id
            """), {"card_id": card_id})

            card = result.fetchone()
            if card:
                print(f"✅ Card encontrado: ID {card.CardID}, Título: '{card.Title}', Coluna: {card.ColumnID}, Ordem: {card.DisplayOrder}")
            else:
                print(f"❌ Card {card_id} não encontrado!")
                return

            print("\n2. VERIFICANDO COLUNAS DISPONÍVEIS...")

            result = await session.execute(text("""
                SELECT ColumnID, ColumnName, DisplayOrder
                FROM [core].[CardColumns]
                WHERE IsActive = 1
                ORDER BY DisplayOrder
            """))

            columns = result.fetchall()
            print("Colunas ativas:")
            for col in columns:
                print(f"  - ID {col.ColumnID}: '{col.ColumnName}' (Ordem: {col.DisplayOrder})")

            print("\n3. VERIFICANDO CARDS NA COLUNA ATUAL...")

            current_column_id = card.ColumnID
            result = await session.execute(text("""
                SELECT CardID, Title, DisplayOrder
                FROM [core].[Cards]
                WHERE ColumnID = :column_id AND IsDeleted = 0
                ORDER BY DisplayOrder
            """), {"column_id": current_column_id})

            cards_in_column = result.fetchall()
            print(f"Cards na coluna {current_column_id}:")
            for c in cards_in_column:
                print(f"  - ID {c.CardID}: '{c.Title}' (Ordem: {c.DisplayOrder})")

            print("\n4. TESTANDO MOVIMENTO SIMULADO...")

            # Simular movimento para coluna "Em Andamento" (ID 3)
            new_column_id = 3
            print(f"Tentando mover card {card_id} da coluna {current_column_id} para coluna {new_column_id}")

            # Verificar se a nova coluna existe
            result = await session.execute(text("""
                SELECT ColumnID, ColumnName
                FROM [core].[CardColumns]
                WHERE ColumnID = :column_id AND IsActive = 1
            """), {"column_id": new_column_id})

            new_column = result.fetchone()
            if not new_column:
                print(f"❌ Coluna destino {new_column_id} não existe ou não está ativa!")
                return

            print(f"✅ Coluna destino existe: '{new_column.ColumnName}'")

            # Verificar se há cards na coluna destino
            result = await session.execute(text("""
                SELECT COUNT(*) as count
                FROM [core].[Cards]
                WHERE ColumnID = :column_id AND IsDeleted = 0
            """), {"column_id": new_column_id})

            count = result.scalar()
            print(f"Cards na coluna destino: {count}")

            print("\n5. TESTANDO ATUALIZAÇÃO DIRETA...")

            try:
                # Tentar atualizar o card diretamente
                await session.execute(text("""
                    UPDATE [core].[Cards]
                    SET ColumnID = :new_column_id,
                        DisplayOrder = 1
                    WHERE CardID = :card_id
                """), {
                    "new_column_id": new_column_id,
                    "card_id": card_id
                })

                await session.commit()
                print("✅ Atualização direta funcionou!")

                # Verificar se foi atualizado
                result = await session.execute(text("""
                    SELECT CardID, Title, ColumnID, DisplayOrder
                    FROM [core].[Cards]
                    WHERE CardID = :card_id
                """), {"card_id": card_id})

                updated_card = result.fetchone()
                print(f"Card após atualização: Coluna {updated_card.ColumnID}, Ordem {updated_card.DisplayOrder}")

            except Exception as e:
                print(f"❌ Erro na atualização direta: {e}")
                await session.rollback()

    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")

    print("\n" + "=" * 80)
    print("DEBUG CONCLUÍDO")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(debug_move_card())