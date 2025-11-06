#!/usr/bin/env python3
"""
Test script to verify that moving cards to completion columns sets CompletedDate
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_db
from app.repositories.kanban_repository import CardRepository, CardColumnRepository
from datetime import datetime

async def test_completed_date_setting():
    """Test that moving a card to a completion column sets CompletedDate"""
    async for db in get_db():
        try:
            card_repo = CardRepository(db)
            column_repo = CardColumnRepository(db)

            # Get all columns for company 1
            columns = await column_repo.get_all(1)
            print(f"Found {len(columns)} columns")

            # Find completion column
            completion_column = None
            for col in columns:
                if "conclu" in col.ColumnName.lower():
                    completion_column = col
                    break

            if not completion_column:
                print("No completion column found")
                return

            print(f"Found completion column: {completion_column.ColumnName} (ID: {completion_column.ColumnID})")

            # Get a card to test with (any card from company 1)
            cards = await card_repo.get_all(1, limit=1)
            if not cards:
                print("No cards found to test with")
                return

            test_card = cards[0]
            print(f"Testing with card: {test_card.Title} (ID: {test_card.CardID})")
            print(f"Current CompletedDate: {test_card.CompletedDate}")

            # Move to completion column
            print(f"Moving to column {completion_column.ColumnID}...")
            moved_card = await card_repo.move_to_column(
                card_id=test_card.CardID,
                company_id=1,
                new_column_id=completion_column.ColumnID,
                user_id=1  # Assuming user 1 exists
            )

            if moved_card:
                print(f"Move successful! New CompletedDate: {moved_card.CompletedDate}")
                if moved_card.CompletedDate:
                    print("✅ SUCCESS: CompletedDate was set!")
                else:
                    print("❌ FAILED: CompletedDate was not set")
            else:
                print("❌ FAILED: Move returned None")

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(test_completed_date_setting())