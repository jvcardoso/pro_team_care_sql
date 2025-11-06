#!/usr/bin/env python3
"""
Script para verificar movimentos e imagens no banco
"""
import asyncio
import sys
from pathlib import Path

# Adicionar backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import AsyncSessionLocal
from app.repositories.kanban_repository import CardMovementRepository

async def check_movements():
    async with AsyncSessionLocal() as session:
        repo = CardMovementRepository(session)
        movements = await repo.get_by_card(2)  # card_id = 2 baseado nos logs

        print(f'📊 Encontrados {len(movements)} movimentos para o card 2')
        print()

        for m in movements:
            print(f'📝 Movimento {m.MovementID}: {m.Subject}')
            print(f'   Tipo: {m.MovementType}')
            print(f'   Data: {m.LogDate}')
            print(f'   Descrição: {m.Description}')

            if hasattr(m, 'images') and m.images:
                print(f'   🖼️  Imagens: {len(m.images)}')
                for img in m.images:
                    print(f'      ID: {img.MovementImageID}')
                    print(f'      Caminho: {img.ImagePath}')
                    print(f'      Descrição: {img.Description}')
                    print(f'      AIAnalysis: {img.AIAnalysis[:100] + "..." if img.AIAnalysis and len(img.AIAnalysis) > 100 else img.AIAnalysis or "None"}')
            else:
                print('   🖼️  Nenhuma imagem associada')
            print()
            print('-' * 50)

if __name__ == "__main__":
    asyncio.run(check_movements())