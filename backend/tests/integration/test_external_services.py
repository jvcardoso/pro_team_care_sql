"""
Testes para endpoints de serviços externos.

Testa ViaCEP, ReceitaWS e Nominatim com mocks.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


class TestExternalServices:
    """Testes de serviços externos."""

    @pytest.mark.asyncio
    async def test_enrich_address_success(self, client: AsyncClient, auth_headers):
        """Testa enriquecimento de endereço com sucesso."""
        mock_result = {
            "cep": "01001000",
            "logradouro": "Praça da Sé",
            "complemento": "",
            "bairro": "Sé",
            "localidade": "São Paulo",
            "uf": "SP",
            "ibge": "3550308",
            "gia": "",
            "ddd": "11",
            "siafi": "7107",
            "ibge_state_code": 35,
            "endereco_completo": "Praça da Sé, Sé, São Paulo - SP, CEP: 01001-000",
            "_metadata": {
                "source": "viacep",
                "enriched_at": "2025-10-28T11:30:00Z",
                "version": "1.0"
            }
        }

        with patch("app.services.address_enrichment_service.address_enrichment_service.consult_viacep",
                   new_callable=AsyncMock) as mock_consult:
            mock_consult.return_value = mock_result

            request_data = {"cep": "01001000"}
            response = await client.post(
                "/api/v1/external/address/enrich",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["cep"] == "01001000"
            assert data["logradouro"] == "Praça da Sé"
            assert data["localidade"] == "São Paulo"
            assert data["ibge_state_code"] == 35

    @pytest.mark.asyncio
    async def test_enrich_address_not_found(self, client: AsyncClient, auth_headers):
        """Testa enriquecimento de endereço com CEP não encontrado."""
        with patch("app.services.address_enrichment_service.address_enrichment_service.consult_viacep",
                   new_callable=AsyncMock) as mock_consult:
            mock_consult.return_value = None

            request_data = {"cep": "99999999"}
            response = await client.post(
                "/api/v1/external/address/enrich",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 404
            data = response.json()
            assert "CEP não encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_enrich_address_invalid_format(self, client: AsyncClient, auth_headers):
        """Testa enriquecimento de endereço com CEP inválido."""
        request_data = {"cep": "123"}
        response = await client.post(
            "/api/v1/external/address/enrich",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_consult_cnpj_success(self, client: AsyncClient, auth_headers):
        """Testa consulta CNPJ com sucesso."""
        mock_result = {
            "cnpj": "06990590000123",
            "nome": "GOOGLE BRASIL INTERNET LTDA.",
            "fantasia": "",
            "status": "ATIVA",
            "ultima_atualizacao": "2023-01-01",
            "tipo": "MATRIZ",
            "abertura": "1998-08-19",
            "situacao": "ATIVA",
            "logradouro": "AV BRIG FARIA LIMA",
            "numero": "3477",
            "complemento": "",
            "bairro": "ITAIM BIBI",
            "municipio": "SAO PAULO",
            "uf": "SP",
            "cep": "04.538-133",
            "telefone": "",
            "email": "",
            "atividade_principal": [{"code": "62.01-1/00", "text": "Desenvolvimento de programas de computador sob encomenda"}],
            "atividades_secundarias": [],
            "natureza_juridica": "205-4 - Sociedade Anônima Fechada",
            "capital_social": "1000000.00",
            "porte": "DEMAIS",
            "data_situacao": "2005-11-03",
            "motivo_situacao": "",
            "situacao_especial": "",
            "data_situacao_especial": "",
            "atividade_principal_descricao": "Informação e comunicação",
            "endereco_completo": "AV BRIG FARIA LIMA, 3477 - ITAIM BIBI, SAO PAULO - SP, CEP: 04.538-133",
            "_metadata": {
                "source": "receitaws",
                "enriched_at": "2025-10-28T11:30:00Z",
                "version": "1.0"
            }
        }

        with patch("app.services.cnpj_service.cnpj_service.consult_cnpj",
                   new_callable=AsyncMock) as mock_consult:
            mock_consult.return_value = mock_result

            request_data = {"cnpj": "06990590000123"}
            response = await client.post(
                "/api/v1/external/cnpj/consult",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["cnpj"] == "06990590000123"
            assert data["nome"] == "GOOGLE BRASIL INTERNET LTDA."
            assert data["status"] == "ATIVA"

    @pytest.mark.asyncio
    async def test_consult_cnpj_not_found(self, client: AsyncClient, auth_headers):
        """Testa consulta CNPJ não encontrado."""
        with patch("app.services.cnpj_service.cnpj_service.consult_cnpj",
                   new_callable=AsyncMock) as mock_consult:
            mock_consult.return_value = None

            request_data = {"cnpj": "99999999999999"}
            response = await client.post(
                "/api/v1/external/cnpj/consult",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 404
            data = response.json()
            assert "CNPJ não encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_geocode_address_success(self, client: AsyncClient, auth_headers):
        """Testa geocoding com sucesso."""
        mock_result = {
            "latitude": -23.5503898,
            "longitude": -46.633081,
            "display_name": "Praça da Sé, São Paulo",
            "type": "park",
            "importance": 0.46,
            "address": {"city": "São Paulo", "state": "SP"},
            "boundingbox": ["-23.551", "-23.549", "-46.634", "-46.632"],
            "original_query": "Praça da Sé, São Paulo, SP",
            "_metadata": {
                "source": "nominatim",
                "enriched_at": "2025-10-28T11:30:00Z",
                "version": "1.0"
            }
        }

        with patch("app.services.geocoding_service.geocoding_service.geocode_address",
                   new_callable=AsyncMock) as mock_geocode:
            mock_geocode.return_value = mock_result

            request_data = {
                "address": "Praça da Sé, São Paulo, SP"
            }
            response = await client.post(
                "/api/v1/external/geocoding/forward",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert abs(data["latitude"] - (-23.55)) < 0.01
            assert abs(data["longitude"] - (-46.63)) < 0.01
            assert "Praça da Sé" in data["display_name"]

    @pytest.mark.asyncio
    async def test_geocode_address_not_found(self, client: AsyncClient, auth_headers):
        """Testa geocoding com endereço não encontrado."""
        with patch("app.services.geocoding_service.geocoding_service.geocode_address",
                   new_callable=AsyncMock) as mock_geocode:
            mock_geocode.return_value = None

            request_data = {"address": "Endereço inexistente"}
            response = await client.post(
                "/api/v1/external/geocoding/forward",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 404
            data = response.json()
            assert "Endereço não encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_reverse_geocode_success(self, client: AsyncClient, auth_headers):
        """Testa reverse geocoding com sucesso."""
        mock_result = {
            "latitude": -23.5503898,
            "longitude": -46.633081,
            "display_name": "Praça da Sé, São Paulo, SP",
            "type": "park",
            "importance": 0.46,
            "address": {"city": "São Paulo", "state": "SP"},
            "boundingbox": ["-23.551", "-23.549", "-46.634", "-46.632"],
            "_metadata": {
                "source": "nominatim_reverse",
                "enriched_at": "2025-10-28T11:30:00Z",
                "version": "1.0"
            }
        }

        with patch("app.services.geocoding_service.geocoding_service.reverse_geocode",
                   new_callable=AsyncMock) as mock_reverse:
            mock_reverse.return_value = mock_result

            request_data = {
                "latitude": -23.5503898,
                "longitude": -46.633081
            }
            response = await client.post(
                "/api/v1/external/geocoding/reverse",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert "Praça da Sé" in data["display_name"]
            assert "_metadata" in data

    @pytest.mark.asyncio
    async def test_enrich_company_combined(self, client: AsyncClient, auth_headers):
        """Testa enriquecimento combinado de empresa."""
        mock_cnpj = {
            "cnpj": "06990590000123",
            "nome": "GOOGLE BRASIL INTERNET LTDA.",
            "status": "ATIVA",
            "_metadata": {"source": "receitaws"}
        }
        mock_address = {
            "cep": "01001000",
            "logradouro": "Praça da Sé",
            "localidade": "São Paulo",
            "_metadata": {"source": "viacep"}
        }
        mock_geocoding = {
            "latitude": -23.55,
            "longitude": -46.63,
            "display_name": "Praça da Sé, São Paulo",
            "_metadata": {"source": "nominatim"}
        }

        with patch("app.services.cnpj_service.cnpj_service.consult_cnpj",
                   new_callable=AsyncMock) as mock_cnpj_consult, \
             patch("app.services.address_enrichment_service.address_enrichment_service.consult_viacep",
                   new_callable=AsyncMock) as mock_address_consult, \
             patch("app.services.geocoding_service.geocoding_service.geocode_address",
                   new_callable=AsyncMock) as mock_geocode:

            mock_cnpj_consult.return_value = mock_cnpj
            mock_address_consult.return_value = mock_address
            mock_geocode.return_value = mock_geocoding

            request_data = {
                "cnpj": "06990590000123",
                "cep": "01001000",
                "endereco_completo": "Praça da Sé, São Paulo"
            }
            response = await client.post(
                "/api/v1/external/company/enrich",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["cnpj_data"]["nome"] == "GOOGLE BRASIL INTERNET LTDA."
            assert data["address_data"]["logradouro"] == "Praça da Sé"
            assert data["geocoding_data"]["display_name"] == "Praça da Sé, São Paulo"
            assert all(status == "success" for status in data["services_status"].values())
            assert "_metadata" in data

    @pytest.mark.asyncio
    async def test_enrich_company_partial_failure(self, client: AsyncClient, auth_headers):
        """Testa enriquecimento combinado com falha parcial."""
        mock_cnpj = {
            "cnpj": "06990590000123",
            "nome": "GOOGLE BRASIL INTERNET LTDA.",
            "_metadata": {"source": "receitaws"}
        }

        with patch("app.services.cnpj_service.cnpj_service.consult_cnpj",
                   new_callable=AsyncMock) as mock_cnpj_consult, \
             patch("app.services.address_enrichment_service.address_enrichment_service.consult_viacep",
                   new_callable=AsyncMock) as mock_address_consult, \
             patch("app.services.geocoding_service.geocoding_service.geocode_address",
                   new_callable=AsyncMock) as mock_geocode:

            mock_cnpj_consult.return_value = mock_cnpj
            mock_address_consult.return_value = None  # Falha
            mock_geocode.return_value = None  # Falha

            request_data = {"cnpj": "06990590000123"}
            response = await client.post(
                "/api/v1/external/company/enrich",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["cnpj_data"]["nome"] == "GOOGLE BRASIL INTERNET LTDA."
            assert data["address_data"] is None
            assert data["geocoding_data"] is None
            assert data["services_status"]["cnpj"] == "success"
            assert data["services_status"]["address"] == "not_requested"
            assert data["services_status"]["geocoding"] == "not_requested"

    @pytest.mark.asyncio
    async def test_enrich_company_all_fail(self, client: AsyncClient, auth_headers):
        """Testa enriquecimento combinado com todas falhas."""
        with patch("app.services.cnpj_service.cnpj_service.consult_cnpj",
                   new_callable=AsyncMock) as mock_cnpj_consult, \
             patch("app.services.address_enrichment_service.address_enrichment_service.consult_viacep",
                   new_callable=AsyncMock) as mock_address_consult, \
             patch("app.services.geocoding_service.geocoding_service.geocode_address",
                   new_callable=AsyncMock) as mock_geocode:

            mock_cnpj_consult.return_value = None
            mock_address_consult.return_value = None
            mock_geocode.return_value = None

            request_data = {
                "cnpj": "99999999999999",
                "cep": "99999999",
                "endereco_completo": "Endereço inexistente"
            }
            response = await client.post(
                "/api/v1/external/company/enrich",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 404
            data = response.json()
            assert "Nenhum dos serviços externos" in data["detail"]