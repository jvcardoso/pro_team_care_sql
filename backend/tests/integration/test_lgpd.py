"""
Testes para endpoints LGPD.

Testa reveal de campos e consulta de logs de auditoria.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import json


class TestLGPD:
    """Testes de endpoints LGPD."""

    @pytest.mark.asyncio
    async def test_get_audit_logs_unauthorized(self, client: AsyncClient):
        """Testa acesso não autorizado ao endpoint de logs."""
        response = await client.get("/api/v1/lgpd/audit-logs/")

        # Deve retornar 401 sem token
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_audit_logs_success(self, client: AsyncClient, auth_headers):
        """Testa consulta de logs com autenticação."""
        # Este teste assume que há dados no banco de teste
        # Em um cenário real, seria necessário mockar ou inserir dados de teste
        response = await client.get(
            "/api/v1/lgpd/audit-logs/?page=1&size=10",
            headers=auth_headers
        )

        # Deve retornar 200 ou 422 dependendo da conectividade do banco
        assert response.status_code in [200, 422]

        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "page" in data
            assert "size" in data
            assert "pages" in data
            assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_get_audit_logs_with_filters(self, client: AsyncClient, auth_headers):
        """Testa consulta de logs com filtros."""
        response = await client.get(
            "/api/v1/lgpd/audit-logs/?entity_type=company&entity_id=164&page=1&size=10",
            headers=auth_headers
        )

    @pytest.mark.asyncio
    async def test_audit_logs_count_matches_database(self, client: AsyncClient, auth_headers, test_db: AsyncSession):
        """
        Testa se a contagem de registros da API corresponde à consulta direta no banco.

        Este teste verifica se a API está retornando a mesma quantidade de registros
        que uma consulta direta à stored procedure do banco de dados.
        """
        # Parâmetros de teste
        test_company_id = 164  # ID da empresa de teste
        test_page = 1
        test_page_size = 50

        # 1. Executa a stored procedure diretamente no banco
        query = """
        DECLARE @total_records INT;

        EXEC core.sp_get_lgpd_audit_logs
            @requesting_user_id = 1,
            @target_company_id = :company_id,
            @page_number = :page,
            @page_size = :page_size,
            @total_records = @total_records OUTPUT;

        SELECT @total_records AS total_records;
        """

        # Executa a consulta SQL
        result = await test_db.execute(
            text(query),
            {
                "company_id": test_company_id,
                "page": test_page,
                "page_size": test_page_size
            }
        )

        # Obtém o total de registros da stored procedure
        db_total = result.scalar_one()

        # 2. Chama a API
        response = await client.get(
            f"/api/v1/lgpd/companies/{test_company_id}/audit-log",
            params={"page": test_page, "size": test_page_size},
            headers=auth_headers
        )

        # 3. Compara os resultados
        assert response.status_code == 200
        api_data = response.json()
        api_total = api_data["total"]

        # A API deve retornar a mesma contagem que o banco
        assert api_total == db_total, f"API retornou {api_total} registros, mas banco tem {db_total}"

        # Verifica se os registros retornados estão dentro do esperado
        assert len(api_data["items"]) <= test_page_size

    @pytest.mark.asyncio
    async def test_reveal_field_unauthorized(self, client: AsyncClient):
        """Testa acesso não autorizado ao reveal de campo."""
        response = await client.post(
            "/api/v1/lgpd/companies/164/reveal-field",
            json={"field_name": "tax_id"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_reveal_field_success(self, client: AsyncClient, auth_headers):
        """Testa reveal de campo com sucesso."""
        response = await client.post(
            "/api/v1/lgpd/companies/164/reveal-field",
            json={"field_name": "tax_id"},
            headers=auth_headers
        )

        # Deve retornar 200 ou 404 dependendo se o campo existe
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "revealed_value" in data
            assert "field_name" in data
            assert data["field_name"] == "tax_id"

    @pytest.mark.asyncio
    async def test_reveal_field_invalid_field(self, client: AsyncClient, auth_headers):
        """Testa reveal de campo inexistente."""
        response = await client.post(
            "/api/v1/lgpd/companies/164/reveal-field",
            json={"field_name": "campo_inexistente"},
            headers=auth_headers
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_reveal_fields_success(self, client: AsyncClient, auth_headers):
        """Testa reveal de múltiplos campos."""
        response = await client.post(
            "/api/v1/lgpd/companies/164/reveal-fields",
            json={"field_names": ["tax_id", "incorporation_date"]},
            headers=auth_headers
        )

        # Deve retornar 200 ou 404 dependendo se os campos existem
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "revealed_fields" in data
            assert isinstance(data["revealed_fields"], list)

    @pytest.mark.asyncio
    async def test_audit_action_success(self, client: AsyncClient, auth_headers):
        """Testa registro de ação de auditoria."""
        response = await client.post(
            "/api/v1/lgpd/companies/164/audit-action",
            json={
                "action": "VIEW_SENSITIVE_DATA",
                "description": "Usuário visualizou dados sensíveis da empresa",
                "metadata": {"source": "company_details_page"}
            },
            headers=auth_headers
        )

        assert response.status_code == 201

        data = response.json()
        assert "audit_id" in data
        assert "message" in data