#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append('.')

from sqlalchemy import text
from app.database.connection import get_db_session

async def check_data():
    try:
        async with get_db_session() as session:
            # Verificar se há cards com classificação ITIL
            result = await session.execute(text('SELECT COUNT(*) as total FROM core.Cards WHERE ITILCategory IS NOT NULL'))
            total_itil = result.fetchone()[0]

            # Verificar distribuição por categoria
            result = await session.execute(text('''
                SELECT ITILCategory, COUNT(*) as count
                FROM core.Cards
                WHERE ITILCategory IS NOT NULL AND IsDeleted = 0
                GROUP BY ITILCategory
                ORDER BY count DESC
            '''))
            categories = result.fetchall()

            print(f'📊 Cards com classificação ITIL: {total_itil}')
            if categories:
                print('📈 Distribuição por categoria:')
                for cat, count in categories:
                    print(f'   {cat}: {count} cards')
            else:
                print('⚠️  Nenhum card classificado ainda')

            # Verificar se a view existe
            result = await session.execute(text('''
                SELECT COUNT(*) as total FROM analytics.vw_ITILReport
            '''))
            view_count = result.fetchone()[0]
            print(f'📋 View vw_ITILReport tem {view_count} registros')

    except Exception as e:
        print(f'❌ Erro ao conectar: {e}')

if __name__ == '__main__':
    asyncio.run(check_data())