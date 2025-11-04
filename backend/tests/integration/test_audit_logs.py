"""
Testes para os endpoints de logs de auditoria LGPD.

Testa a integração entre a API e o banco de dados, garantindo que a contagem
de registros retornados pela API corresponda à consulta direta no banco.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

class TestAuditLogs:
    """Testes para os endpoints de logs de auditoria."""

    @pytest.mark.asyncio
    async def test_audit_logs_count_matches_database(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_db: AsyncSession
    ):
        """
        Testa se a contagem de registros da API corresponde à consulta direta no banco.
        
        Este teste verifica se a API está retornando a mesma quantidade de registros
        que uma consulta direta à stored procedure do banco de dados.
        """
        # Parâmetros de teste
        test_company_id = 164  # ID da empresa de teste
        test_page = 1
        test_page_size = 50
        
        # 1. Primeiro, chama a API para obter os dados
        print(f"\n🔍 Chamando API para company_id={test_company_id}, page={test_page}, size={test_page_size}")
        response = await client.get(
            f"/api/v1/lgpd/companies/{test_company_id}/audit-log",
            params={"page": test_page, "size": test_page_size},
            headers=auth_headers
        )
        
        # Verifica se a requisição foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK, f"Erro na requisição: {response.text}"
        
        # Obtém a resposta da API
        api_data = response.json()
        print(f"✅ Resposta da API: {api_data.get('total')} registros totais")
        
        # 2. Verifica a estrutura da resposta
        assert "items" in api_data, "Resposta da API não contém campo 'items'"
        assert "total" in api_data, "Resposta da API não contém campo 'total'"
        assert "page" in api_data, "Resposta da API não contém campo 'page'"
        assert "size" in api_data, "Resposta da API não contém campo 'size'"
        assert "pages" in api_data, "Resposta da API não contém campo 'pages'"
        
        # 3. Verifica se o número de itens retornados é o esperado
        expected_items = min(test_page_size, api_data["total"] - (test_page - 1) * test_page_size)
        assert len(api_data["items"]) == expected_items, \
            f"Número incorreto de itens retornados. Esperado: {expected_items}, Obtido: {len(api_data['items'])}"
        
        # 4. Se houver itens, verifica a estrutura de cada um
        if api_data["items"]:
            first_item = api_data["items"][0]
            required_fields = [
                "id", "created_at", "action_type", "entity_type", 
                "entity_id", "user_id", "user_email"
            ]
            
            for field in required_fields:
                assert field in first_item, f"Campo obrigatório não encontrado: {field}"
            
            print(f"✅ Estrutura do primeiro item válida: {first_item}")
        
        # 5. Executa a stored procedure diretamente para comparar
        print(f"\n🔍 Executando stored procedure diretamente...")
        try:
            # A stored procedure não retorna o total diretamente, então contamos os registros
            sp_query = text("""
                EXEC pro_team_care_logs.core.sp_get_lgpd_audit_logs
                    @requesting_user_id = :user_id,
                    @target_company_id = :company_id,
                    @page_number = :page,
                    @page_size = :page_size
            """)
            
            params = {
                "user_id": 1,  # ID do usuário admin
                "company_id": test_company_id,
                "page": test_page,
                "page_size": test_page_size
            }
            
            result = await db.execute(sp_query, params)
            db_items = result.fetchall()
            
            print(f"✅ Stored procedure retornou {len(db_items)} registros")
            
            # 6. Verifica se a contagem de itens é a mesma
            assert len(api_data["items"]) == len(db_items), \
                f"Contagem de itens não corresponde. API: {len(api_data['items'])}, SP: {len(db_items)}"
            
            # 7. Se houver itens, verifica se os IDs correspondem
            if api_data["items"] and db_items:
                api_ids = {item["id"] for item in api_data["items"]}
                db_ids = {item[0] for item in db_items}  # Assumindo que o ID está na primeira coluna
                
                # Verifica se todos os IDs da API estão no banco
                missing_in_db = api_ids - db_ids
                assert not missing_in_db, f"IDs encontrados na API mas não no banco: {missing_in_db}"
                
                print(f"✅ Todos os {len(api_ids)} IDs da API estão presentes no banco")
                
        except Exception as e:
            pytest.fail(f"Erro ao executar stored procedure: {str(e)}")
        
        print("\n✅ Teste concluído com sucesso!")
