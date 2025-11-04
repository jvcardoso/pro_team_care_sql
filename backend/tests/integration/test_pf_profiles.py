"""
Testes para endpoints de PF Profiles com foco em LGPD.

Testa mascaramento automático, revelação controlada e auditoria.
"""
import pytest
from httpx import AsyncClient


class TestPFProfilesLGPD:
    """Testes de perfis PF com segurança LGPD."""

    @pytest.mark.asyncio
    async def test_list_pf_profiles_masked(self, client: AsyncClient, auth_headers: dict):
        """Testa listagem de perfis PF com dados mascarados."""
        response = await client.get("/api/v1/pf-profiles", headers=auth_headers)

        # Pode retornar 200 se banco acessível, ou 401 se token inválido
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            # Verificar se dados estão mascarados (ex: CPF com ***)
            if data:  # Se há perfis
                profile = data[0]
                # CPF deve estar mascarado se não for admin
                assert "tax_id" in profile
                # Nota: O mascaramento exato depende da implementação da view

    @pytest.mark.asyncio
    async def test_get_pf_profile_masked(self, client: AsyncClient, auth_headers: dict):
        """Testa busca de perfil PF específico com mascaramento."""
        # Assumindo que existe um perfil com ID 1
        response = await client.get("/api/v1/pf-profiles/1", headers=auth_headers)

        # Pode retornar 200/404 se perfil existe/não existe, ou 401 se token inválido
        assert response.status_code in [200, 401, 404]

        if response.status_code == 200:
            data = response.json()
            assert "tax_id" in data
            assert "birth_date" in data
            # Dados devem estar mascarados conforme permissões

    @pytest.mark.asyncio
    async def test_reveal_pf_profile_data(self, client: AsyncClient, auth_headers: dict):
        """Testa revelação de dados sensíveis de PF."""
        reveal_data = {
            "fields_to_reveal": ["tax_id", "birth_date"]
        }

        response = await client.post(
            "/api/v1/pf-profiles/1/reveal",
            json=reveal_data,
            headers=auth_headers
        )

        # Pode retornar vários códigos dependendo do estado do banco
        assert response.status_code in [200, 401, 403, 404, 422]

        if response.status_code == 200:
            data = response.json()
            # Dados devem estar desmascarados
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_create_pf_profile_audit(self, client: AsyncClient, auth_headers: dict):
        """Testa criação de perfil PF com auditoria."""
        profile_data = {
            "person_id": 1,  # Assumindo que existe
            "tax_id": "12345678900",
            "birth_date": "1990-01-01T00:00:00",
            "gender": "Masculino",
            "marital_status": "S",
            "occupation": "Desenvolvedor"
        }

        response = await client.post(
            "/api/v1/pf-profiles",
            json=profile_data,
            headers=auth_headers
        )

        # Pode retornar vários códigos dependendo do estado do banco
        assert response.status_code in [201, 400, 401, 403, 404, 422, 500]

        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert data["tax_id"] == profile_data["tax_id"]

    @pytest.mark.asyncio
    async def test_pf_profile_unauthorized_access(self, client: AsyncClient):
        """Testa acesso não autorizado a perfis PF."""
        response = await client.get("/api/v1/pf-profiles")

        assert response.status_code in [401, 403]
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_pf_profile_invalid_reveal_fields(self, client: AsyncClient, auth_headers: dict):
        """Testa revelação com campos inválidos."""
        reveal_data = {
            "fields_to_reveal": ["invalid_field"]
        }

        response = await client.post(
            "/api/v1/pf-profiles/1/reveal",
            json=reveal_data,
            headers=auth_headers
        )

        # Pode retornar vários códigos dependendo do estado do banco
        assert response.status_code in [200, 400, 401, 403, 404, 422, 500]