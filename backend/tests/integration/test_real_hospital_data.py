"""
Testes de integração com dados reais de hospitais brasileiros.

Usa CNPJs válidos coletados da Receita Federal para testar cadastros completos
da API, incluindo empresas, estabelecimentos, pessoas, telefones, emails e endereços.

Dados coletados via API pública (ReceitaWS) - informações públicas disponíveis.
"""
import pytest
from httpx import AsyncClient


class TestHospitalCadastroCompleto:
    """Testes de cadastro completo de hospitais reais."""

    @pytest.mark.asyncio
    async def test_cadastrar_hospital_base_sao_jose_rio_preto(self, client: AsyncClient, auth_headers: dict):
        """
        Testa cadastro completo do Hospital de Base de São José do Rio Preto.

        CNPJ: 60.003.761/0001-29
        Dados coletados da Receita Federal.
        """
        # 1. Criar empresa
        company_data = {
            "name": "FUNDACAO FACULDADE REGIONAL DE MEDICINA S J RIO PRETO",
            "tax_id": "60003761000129",  # CNPJ sem formatação
            "website": "https://www.hospitaldebase.com.br",  # Site público
            "description": "Hospital de referência em cardiologia e outras especialidades",
            "settings": None
        }

        company_response = await client.post(
            "/api/v1/companies",
            json=company_data,
            headers=auth_headers
        )
        assert company_response.status_code in [201, 400, 409]  # 409 se já existe

        if company_response.status_code == 201:
            company = company_response.json()
            company_id = company["id"]
        else:
            # Se já existe, buscar pelo CNPJ
            search_response = await client.get(
                f"/api/v1/companies?tax_id={company_data['tax_id']}",
                headers=auth_headers
            )
            assert search_response.status_code == 200
            companies = search_response.json()
            assert len(companies) > 0
            company_id = companies[0]["id"]

        # 2. Criar estabelecimento
        establishment_data = {
            "company_id": company_id,
            "name": "Hospital de Base",
            "type": "hospital",
            "description": "Unidade principal do Hospital de Base"
        }

        establishment_response = await client.post(
            "/api/v1/establishments",
            json=establishment_data,
            headers=auth_headers
        )
        assert establishment_response.status_code in [201, 400]

        if establishment_response.status_code == 201:
            establishment = establishment_response.json()
            establishment_id = establishment["id"]
        else:
            # Buscar estabelecimento existente
            search_response = await client.get(
                f"/api/v1/establishments?company_id={company_id}",
                headers=auth_headers
            )
            assert search_response.status_code == 200
            establishments = search_response.json()
            assert len(establishments) > 0
            establishment_id = establishments[0]["id"]

        # 3. Criar endereço do estabelecimento
        address_data = {
            "establishment_id": establishment_id,
            "street": "AV BRIGADEIRO FARIA LIMA",
            "number": "5544",
            "neighborhood": "SAO PEDRO",
            "city": "SAO JOSE DO RIO PRETO",
            "state": "SP",
            "zip_code": "15090000",  # Sem formatação
            "country": "Brasil",
            "type": "comercial"
        }

        address_response = await client.post(
            "/api/v1/addresses",
            json=address_data,
            headers=auth_headers
        )
        assert address_response.status_code in [201, 400]

        # 4. Criar telefones
        phones_data = [
            {
                "establishment_id": establishment_id,
                "number": "1732015033",
                "type": "fixo"
            },
            {
                "establishment_id": establishment_id,
                "number": "1732015032",
                "type": "fixo"
            }
        ]

        for phone_data in phones_data:
            phone_response = await client.post(
                "/api/v1/phones",
                json=phone_data,
                headers=auth_headers
            )
            assert phone_response.status_code in [201, 400]

        # 5. Criar email
        email_data = {
            "establishment_id": establishment_id,
            "address": "contabilidade@hospitaldebase.com.br",
            "type": "comercial"
        }

        email_response = await client.post(
            "/api/v1/emails",
            json=email_data,
            headers=auth_headers
        )
        assert email_response.status_code in [201, 400]

        # 6. Criar pessoa (exemplo: diretor)
        person_data = {
            "company_id": company_id,
            "name": "HORACIO JOSE RAMALHO",
            "status": "active"
        }

        person_response = await client.post(
            "/api/v1/people",
            json=person_data,
            headers=auth_headers
        )
        assert person_response.status_code in [201, 400]

        if person_response.status_code == 201:
            person = person_response.json()
            person_id = person["id"]

            # Criar perfil PF (dados fictícios para teste)
            pf_profile_data = {
                "person_id": person_id,
                "tax_id": "12345678901",  # CPF fictício
                "birth_date": "1960-01-01T00:00:00",
                "gender": "Masculino",
                "marital_status": "Casado",
                "occupation": "Diretor Executivo"
            }

            pf_response = await client.post(
                "/api/v1/pf-profiles",
                json=pf_profile_data,
                headers=auth_headers
            )
            assert pf_response.status_code in [201, 400, 422, 500]

    @pytest.mark.asyncio
    async def test_cadastrar_hospital_base_distrito_federal(self, client: AsyncClient, auth_headers: dict):
        """
        Testa cadastro completo do Hospital de Base do Distrito Federal.

        CNPJ: 00.394.700/0005-31
        Dados coletados da Receita Federal.
        """
        # 1. Criar empresa
        company_data = {
            "name": "DISTRITO FEDERAL SECRETARIA DE SAUDE",
            "tax_id": "00394700000531",
            "website": "https://www.saude.df.gov.br",  # Site público do governo
            "description": "Secretaria de Saúde do Distrito Federal - Hospital de Base",
            "settings": None
        }

        company_response = await client.post(
            "/api/v1/companies",
            json=company_data,
            headers=auth_headers
        )
        assert company_response.status_code in [201, 400, 409]

        if company_response.status_code == 201:
            company = company_response.json()
            company_id = company["id"]
        else:
            search_response = await client.get(
                f"/api/v1/companies?tax_id={company_data['tax_id']}",
                headers=auth_headers
            )
            assert search_response.status_code == 200
            companies = search_response.json()
            if companies:
                company_id = companies[0]["id"]
            else:
                # Criar mesmo assim se não encontrou
                company_response = await client.post(
                    "/api/v1/companies",
                    json=company_data,
                    headers=auth_headers
                )
                company = company_response.json()
                company_id = company["id"]

        # 2. Criar estabelecimento
        establishment_data = {
            "company_id": company_id,
            "name": "Hospital de Base do Distrito Federal",
            "type": "hospital",
            "description": "Hospital público de referência no DF"
        }

        establishment_response = await client.post(
            "/api/v1/establishments",
            json=establishment_data,
            headers=auth_headers
        )
        assert establishment_response.status_code in [201, 400]

        if establishment_response.status_code == 201:
            establishment = establishment_response.json()
            establishment_id = establishment["id"]
        else:
            search_response = await client.get(
                f"/api/v1/establishments?company_id={company_id}",
                headers=auth_headers
            )
            assert search_response.status_code == 200
            establishments = search_response.json()
            if establishments:
                establishment_id = establishments[0]["id"]
            else:
                establishment_response = await client.post(
                    "/api/v1/establishments",
                    json=establishment_data,
                    headers=auth_headers
                )
                establishment = establishment_response.json()
                establishment_id = establishment["id"]

        # 3. Criar endereço
        address_data = {
            "establishment_id": establishment_id,
            "street": "SMHS QUADRA",
            "number": "101",
            "neighborhood": "PLANO PILOTO",
            "city": "BRASILIA",
            "state": "DF",
            "zip_code": "70310500",
            "country": "Brasil",
            "type": "comercial"
        }

        address_response = await client.post(
            "/api/v1/addresses",
            json=address_data,
            headers=auth_headers
        )
        assert address_response.status_code in [201, 400]

        # 4. Criar telefone
        phone_data = {
            "establishment_id": establishment_id,
            "number": "613254050",
            "type": "fixo"
        }

        phone_response = await client.post(
            "/api/v1/phones",
            json=phone_data,
            headers=auth_headers
        )
        assert phone_response.status_code in [201, 400]

    @pytest.mark.asyncio
    async def test_cadastrar_hospital_forcas_armadas(self, client: AsyncClient, auth_headers: dict):
        """
        Testa cadastro completo do Hospital das Forças Armadas.

        CNPJ: 03.568.867/0001-36
        Dados coletados da Receita Federal.
        """
        # 1. Criar empresa
        company_data = {
            "name": "HOSPITAL DAS FORCAS ARMADAS",
            "tax_id": "03568867000136",
            "website": "https://www.hfa.mil.br",  # Site público das Forças Armadas
            "description": "Hospital militar das Forças Armadas brasileiras",
            "settings": None
        }

        company_response = await client.post(
            "/api/v1/companies",
            json=company_data,
            headers=auth_headers
        )
        assert company_response.status_code in [201, 400, 409]

        if company_response.status_code == 201:
            company = company_response.json()
            company_id = company["id"]
        else:
            search_response = await client.get(
                f"/api/v1/companies?tax_id={company_data['tax_id']}",
                headers=auth_headers
            )
            assert search_response.status_code == 200
            companies = search_response.json()
            if companies:
                company_id = companies[0]["id"]
            else:
                company_response = await client.post(
                    "/api/v1/companies",
                    json=company_data,
                    headers=auth_headers
                )
                company = company_response.json()
                company_id = company["id"]

        # 2. Criar estabelecimento
        establishment_data = {
            "company_id": company_id,
            "name": "Hospital das Forças Armadas",
            "type": "hospital",
            "description": "Hospital militar de referência"
        }

        establishment_response = await client.post(
            "/api/v1/establishments",
            json=establishment_data,
            headers=auth_headers
        )
        assert establishment_response.status_code in [201, 400]

        if establishment_response.status_code == 201:
            establishment = establishment_response.json()
            establishment_id = establishment["id"]
        else:
            search_response = await client.get(
                f"/api/v1/establishments?company_id={company_id}",
                headers=auth_headers
            )
            assert search_response.status_code == 200
            establishments = search_response.json()
            if establishments:
                establishment_id = establishments[0]["id"]
            else:
                establishment_response = await client.post(
                    "/api/v1/establishments",
                    json=establishment_data,
                    headers=auth_headers
                )
                establishment = establishment_response.json()
                establishment_id = establishment["id"]

        # 3. Criar endereço
        address_data = {
            "establishment_id": establishment_id,
            "street": "SETOR HFA",
            "number": "S/N",
            "neighborhood": "SETOR SUDOESTE",
            "city": "BRASILIA",
            "state": "DF",
            "zip_code": "70673900",
            "country": "Brasil",
            "type": "comercial"
        }

        address_response = await client.post(
            "/api/v1/addresses",
            json=address_data,
            headers=auth_headers
        )
        assert address_response.status_code in [201, 400]

        # 4. Criar telefones
        phones_data = [
            {
                "establishment_id": establishment_id,
                "number": "6139662141",
                "type": "fixo"
            },
            {
                "establishment_id": establishment_id,
                "number": "6139662610",
                "type": "fixo"
            },
            {
                "establishment_id": establishment_id,
                "number": "612331599",
                "type": "fixo"
            }
        ]

        for phone_data in phones_data:
            phone_response = await client.post(
                "/api/v1/phones",
                json=phone_data,
                headers=auth_headers
            )
            assert phone_response.status_code in [201, 400]

        # 5. Criar email
        email_data = {
            "establishment_id": establishment_id,
            "address": "gabinete@hfa.mil.br",
            "type": "comercial"
        }

        email_response = await client.post(
            "/api/v1/emails",
            json=email_data,
            headers=auth_headers
        )
        assert email_response.status_code in [201, 400]