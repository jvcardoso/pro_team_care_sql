#!/usr/bin/env python3
"""
Test script to verify the cards endpoint with completed date filters
"""
import asyncio
import sys
import os
import requests

# Test the cards endpoint directly
def test_cards_endpoint():
    # Simular uma requisição para o endpoint
    # Como não temos acesso direto ao banco, vamos simular a lógica

    # Período: 2025-10-06 até 2025-11-05
    completed_from = "2025-10-06"
    completed_to = "2025-11-05"
    column_ids = "1,2,3,4,5"

    print("Testando endpoint: /api/v1/kanban/cards")
    print(f"Parâmetros: completed_from={completed_from}, completed_to={completed_to}, column_ids={column_ids}")

    # Simular a query SQL que seria executada
    sql_query = f"""
    SELECT CardID, Title, ColumnID, CompletedDate
    FROM core.Cards
    WHERE CompanyID = 1
      AND IsDeleted = 0
      AND CompletedDate IS NOT NULL
      AND CAST(CompletedDate AS DATE) >= '{completed_from}'
      AND CAST(CompletedDate AS DATE) <= '{completed_to}'
      AND ColumnID IN ({column_ids.replace(',', ',')})
    ORDER BY CompletedDate DESC
    """

    print("Query SQL simulada:")
    print(sql_query)

    # Análise do problema
    print("\n" + "="*50)
    print("ANÁLISE DO PROBLEMA:")
    print("="*50)

    print("1. O período solicitado é muito específico: 2025-10-06 até 2025-11-05")
    print("2. Isso corresponde a aproximadamente 30 dias atrás")
    print("3. Se não há cards concluídos exatamente nesse período, Array(0) é correto")

    print("\n4. Possíveis soluções:")
    print("   - Expandir o período (ex: últimos 90 dias)")
    print("   - Verificar se há cards concluídos recentemente")
    print("   - Verificar se as datas estão no formato correto")

    print("\n5. Verificação necessária:")
    print("   - Executar query no banco para ver se há dados")
    print("   - Verificar se o período do frontend corresponde aos dados")

if __name__ == "__main__":
    test_cards_endpoint()