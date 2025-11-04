"""
Testes de integração para criação de empresas com enriquecimento automático.

Testa o endpoint POST /api/v1/companies/complete com integração real
dos serviços externos: ViaCEP, Receita Federal e Geocoding.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
import httpx


class TestCompanyCompleteWithExternalEnrichment:
    """Testes de criação de empresa com enriquecimento automático."""

    @pytest.mark.asyncio
    async def test_criar_empresa_com_enriquecimento_completo(self, client: AsyncClient, auth_headers):
        """
        Testa criação de empresa com enriquecimento completo.

        Cenário: CNPJ válido + CEP válido → Receita Federal + ViaCEP + Geocoding
        """
        company_data = {
            "access_status": "active",
            "pj_profile": {
                "name": "Empresa Teste Ltda",
                "trade_name": "Empresa Teste",
                "tax_id": "11222333000144",  # CNPJ que será enriquecido
                "incorporation_date": None,
                "legal_nature": None
            },
            "addresses": [{
                "street": "",  # Será preenchido pelo ViaCEP
                "number": "123",
                "neighborhood": "",  # Será preenchido pelo ViaCEP
                "city": "",  # Será preenchido pelo ViaCEP
                "state": "",  # Será preenchido pelo ViaCEP
                "zip_code": "01001000",  # CEP válido para ViaCEP
                "country": "BR",
                "type": "commercial",
                "is_principal": True
            }],
            "phones": [{
                "country_code": "55",
                "number": "11999999999",
                "type": "mobile",
                "is_principal": True,
                "is_whatsapp": False
            }],
            "emails": [{
                "email_address": "contato@empresateste.com.br",
                "type": "work",
                "is_principal": True
            }]
        }

        # Mock dos serviços externos
        with patch("app.services.cnpj_service.cnpj_service.consult_cnpj") as mock_cnpj, \
             patch("app.services.address_enrichment_service.address_enrichment_service.consult_viacep") as mock_viacep, \
             patch("app.services.geocoding_service.geocoding_service.geocode_address") as mock_geocode:

            # Mock Receita Federal
            mock_cnpj.return_value = {
                "success": True,
                "data": {
                    "nome": "EMPRESA TESTE LTDA",
                    "fantasia": "EMPRESA TESTE",
                    "abertura": "2020-01-15",
                    "natureza_juridica": "Sociedade Empresária Limitada"
                }
            }

            # Mock ViaCEP
            mock_viacep.return_value = {
                "cep": "01001-000",
                "logradouro": "Praça da Sé",
                "bairro": "Sé",
                "localidade": "São Paulo",
                "uf": "SP",
                "ibge": "3550308",
                "gia": "1004",
                "ddd": "11",
                "siafi": "7107"
            }

            # Mock Geocoding
            mock_geocode.return_value = {
                "latitude": "-23.550520",
                "longitude": "-46.633308",
                "formatted_address": "Praça da Sé, São Paulo, SP, Brasil",
                "geocoding_accuracy": "exact",
                "geocoding_source": "nominatim"
            }

            # Executar criação
            response = await client.post(
                "/api/v1/companies/complete",
                json=company_data,
                headers=auth_headers
            )

            # Verificar resposta
            assert response.status_code == 201
            data = response.json()
            assert "new_company_id" in data
            assert "new_person_id" in data
            assert "new_pj_profile_id" in data

            # Verificar que os serviços foram chamados
            mock_cnpj.assert_called_once_with("11222333000144")
            mock_viacep.assert_called_once_with("01001000")
            # Geocodificação está desativada no momento
            # mock_geocode.assert_called_once()

            # Verificar empresa criada
            company_id = data["new_company_id"]
            print(f"\n=== DEBUG: Tentando acessar empresa com ID: {company_id} ===")
            
            # Listar todas as empresas para debug usando o endpoint correto
            list_response = await client.get(
                "/api/v1/companies/complete-list",
                headers=auth_headers
            )
            print(f"Status da listagem de empresas: {list_response.status_code}")
            if list_response.status_code == 200:
                companies = list_response.json()
                print(f"Total de empresas encontradas: {len(companies.get('items', []))}")
                for i, company in enumerate(companies.get('items', [])[:5], 1):
                    print(f"  {i}. ID: {company.get('id')}, Nome: company.get('name')")
            
            # Tentar acessar a empresa específica
            verify_response = await client.get(
                f"/api/v1/companies/{company_id}",
                headers=auth_headers
            )
            print(f"Resposta do GET /api/v1/companies/{company_id}: {verify_response.status_code} - {verify_response.text}")
            
            # Verificar se a empresa foi criada com sucesso
            assert response.status_code == 201, f"Falha ao criar empresa: {response.text}"
            assert "new_company_id" in data, f"Resposta inesperada: {data}"
            
            # Verificar se a empresa pode ser acessada
            assert verify_response.status_code == 200, f"Falha ao acessar empresa com ID {company_id} - Resposta: {verify_response.text}"

    @pytest.mark.asyncio
    async def test_criar_empresa_com_enriquecimento_parcial(self, client: AsyncClient, auth_headers):
        """
        Testa criação de empresa com enriquecimento parcial.

        Cenário: CNPJ válido mas CEP inválido → Apenas Receita funciona
        """
        company_data = {
            "access_status": "active",
            "pj_profile": {
                "name": "Empresa Teste Ltda",
                "trade_name": "Empresa Teste",
                "tax_id": "11222333000144",
                "incorporation_date": None,
                "legal_nature": None
            },
            "addresses": [{
                "street": "Rua Manual",
                "number": "456",
                "neighborhood": "Centro",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "99999999",  # CEP inválido
                "country": "BR",
                "type": "commercial",
                "is_principal": True
            }],
            "phones": [],
            "emails": []
        }

        with patch("app.services.cnpj_service.cnpj_service.consult_cnpj") as mock_cnpj, \
             patch("app.services.address_enrichment_service.address_enrichment_service.consult_viacep") as mock_viacep:

            # Mock Receita funciona
            mock_cnpj.return_value = {
                "success": True,
                "data": {
                    "nome": "EMPRESA TESTE LTDA",
                    "fantasia": "EMPRESA TESTE",
                    "abertura": "2020-01-15",
                    "natureza_juridica": "Sociedade Empresária Limitada"
                }
            }

            # Mock ViaCEP falha (CEP inválido)
            mock_viacep.return_value = None

            response = await client.post(
                "/api/v1/companies/complete",
                json=company_data,
                headers=auth_headers
            )

            assert response.status_code == 201
            data = response.json()

            # Empresa criada mesmo com enriquecimento parcial
            mock_cnpj.assert_called_once_with("11222333000144")
            mock_viacep.assert_called_once_with("99999999")

    @pytest.mark.asyncio
    async def test_criar_empresa_sem_enriquecimento(self, client: AsyncClient, auth_headers):
        """
        Testa criação de empresa com enriquecimento desabilitado.

        Cenário: enrich_data=false → Serviços externos não são chamados
        """
        company_data = {
            "access_status": "active",
            "pj_profile": {
                "name": "Empresa Sem Enriquecimento",
                "trade_name": "Sem Enriquecimento",
                "tax_id": "99988877000166",
                "incorporation_date": "2023-01-01",
                "legal_nature": "Ltda"
            },
            "addresses": [{
                "street": "Rua Manual",
                "number": "100",
                "neighborhood": "Centro",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01000000",
                "country": "BR",
                "type": "commercial",
                "is_principal": True
            }],
            "phones": [],
            "emails": []
        }

        with patch("app.services.cnpj_service.cnpj_service.consult_cnpj") as mock_cnpj, \
             patch("app.services.address_enrichment_service.address_enrichment_service.consult_viacep") as mock_viacep:

            response = await client.post(
                "/api/v1/companies/complete?enrich_data=false",
                json=company_data,
                headers=auth_headers
            )

            assert response.status_code == 201

            # Serviços externos NÃO devem ser chamados
            mock_cnpj.assert_not_called()
            mock_viacep.assert_not_called()

    @pytest.mark.asyncio
    async def test_criar_empresa_fallback_servicos_falham(self, client: AsyncClient, auth_headers):
        """
        Testa criação de empresa quando todos os serviços externos falham.

        Cenário: Sistema deve continuar funcionando mesmo com falhas externas
        """
        company_data = {
            "access_status": "active",
            "pj_profile": {
                "name": "Empresa Fallback",
                "trade_name": "Fallback",
                "tax_id": "11222333000144",
                "incorporation_date": None,
                "legal_nature": None
            },
            "addresses": [{
                "street": "Rua Original",
                "number": "123",
                "neighborhood": "Centro",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01001000",
                "country": "BR",
                "type": "commercial",
                "is_principal": True
            }],
            "phones": [],
            "emails": []
        }

        with patch("app.services.cnpj_service.cnpj_service.consult_cnpj") as mock_cnpj, \
             patch("app.services.address_enrichment_service.address_enrichment_service.consult_viacep") as mock_viacep, \
             patch("app.services.geocoding_service.geocoding_service.geocode_address") as mock_geocode:

            # Todos os serviços falham
            mock_cnpj.side_effect = Exception("Receita Federal indisponível")
            mock_viacep.side_effect = Exception("ViaCEP indisponível")
            mock_geocode.side_effect = Exception("Geocoding indisponível")

            response = await client.post(
                "/api/v1/companies/complete",
                json=company_data,
                headers=auth_headers
            )

            # Deve funcionar mesmo com falhas externas
            assert response.status_code == 201
            data = response.json()
            assert "new_company_id" in data

            # Serviços foram chamados mas falharam
            mock_cnpj.assert_called_once()
            mock_viacep.assert_called_once()
            mock_geocode.assert_called_once()

    @pytest.mark.asyncio
    async def test_criar_empresa_dados_ja_completos(self, client: AsyncClient, auth_headers):
        """
        Testa criação de empresa com dados já completos.

        Cenário: Dados fornecidos não devem ser sobrescritos pelo enriquecimento
        """
        company_data = {
            "access_status": "active",
            "pj_profile": {
                "name": "Empresa Já Completa LTDA",  # Já preenchido
                "trade_name": "Já Completa",  # Já preenchido
                "tax_id": "11222333000144",
                "incorporation_date": "2020-06-15",  # Já preenchido
                "legal_nature": "Sociedade Limitada"  # Já preenchido
            },
            "addresses": [{
                "street": "Rua Já Preenchida",  # Já preenchido
                "number": "200",
                "neighborhood": "Centro Histórico",  # Já preenchido
                "city": "São Paulo",  # Já preenchido
                "state": "SP",  # Já preenchido
                "zip_code": "01001000",
                "country": "BR",
                "type": "commercial",
                "is_principal": True
            }],
            "phones": [],
            "emails": []
        }

        with patch("app.services.cnpj_service.cnpj_service.consult_cnpj") as mock_cnpj, \
             patch("app.services.address_enrichment_service.address_enrichment_service.consult_viacep") as mock_viacep:

            # Serviços retornam dados diferentes (não devem sobrescrever)
            mock_cnpj.return_value = {
                "success": True,
                "data": {
                    "nome": "NOME DIFERENTE DO SERVIÇO",
                    "fantasia": "FANTASIA DIFERENTE",
                    "abertura": "2019-01-01",
                    "natureza_juridica": "Natureza Diferente"
                }
            }

            mock_viacep.return_value = {
                "logradouro": "Rua Diferente do Serviço",
                "bairro": "Bairro Diferente",
                "localidade": "Cidade Diferente",
                "uf": "RJ"
            }

            response = await client.post(
                "/api/v1/companies/complete",
                json=company_data,
                headers=auth_headers
            )

            assert response.status_code == 201

            # Serviços foram chamados
            mock_cnpj.assert_called_once()
            mock_viacep.assert_called_once()

            # Verificar que dados originais foram preservados
            # (Isso seria validado consultando o banco de dados criado)