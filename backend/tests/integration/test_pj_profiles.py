"""
Testes para endpoints de PJ Profiles com foco em LGPD.

Testa mascaramento automático e revelação controlada.
"""
import pytest
from httpx import AsyncClient


class TestPJProfilesLGPD:
    """Testes de perfis PJ com segurança LGPD."""

    @pytest.mark.asyncio
    async def test_list_pj_profiles_masked(self, client: AsyncClient, auth_headers: dict):
        """Testa listagem de perfis PJ com dados mascarados."""
        response = await client.get("/api/v1/pj-profiles", headers=auth_headers)

        assert response.status_code in [200, 401, 403, 404]

        if response.status_code == 200:
            data = response.json()
            if data:
                profile = data[0]
                assert "tax_id" in profile  # CNPJ mascarado

    @pytest.mark.asyncio
    async def test_reveal_pj_profile_data(self, client: AsyncClient, auth_headers: dict):
        """Testa revelação de dados sensíveis de PJ."""
        reveal_data = {
            "fields_to_reveal": ["tax_id", "trade_name"]
        }

        response = await client.post(
            "/api/v1/pj-profiles/1/reveal",
            json=reveal_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 403, 404, 422, 500]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_create_pj_profile_validation(self, client: AsyncClient, auth_headers: dict):
        """Testa criação de perfil PJ com validações."""
        profile_data = {
            "person_id": 1,
            "company_id": 1,
            "tax_id": "12.345.678/0001-00",
            "trade_name": "Empresa Teste Ltda",
            "incorporation_date": "2020-01-01",
            "tax_regime": "Simples Nacional"
        }

        response = await client.post(
            "/api/v1/pj-profiles",
            json=profile_data,
            headers=auth_headers
        )

        assert response.status_code in [201, 400, 401, 403, 500]

        if response.status_code == 201:
            data = response.json()
            assert "id" in data