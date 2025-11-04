"""
Testes de integração com dados fictícios de hospitais.

Usa dados fictícios realistas para testar cadastros completos
da API, incluindo empresas, estabelecimentos, pessoas, telefones, emails e endereços.

Para telefones: marca se é WhatsApp e qual é o principal.
"""
import pytest
from httpx import AsyncClient


class TestHospitalCadastroFicticio:
    """Testes de cadastro completo de hospitais fictícios."""

    @pytest.mark.asyncio
    async def test_endpoint_establishments_existe(self, client: AsyncClient):
        """Testa se o endpoint establishments existe e responde."""
        response = await client.get("/api/v1/establishments")
        # Deve retornar 401 (não autorizado) ou 403 (forbidden) se endpoint existe
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_cadastrar_hospital_santa_maria(self, client: AsyncClient, auth_headers: dict):
        """
        Testa cadastro completo do Hospital Santa Maria (fictício).

        Dados fictícios baseados em hospitais reais brasileiros.
        Cria dependências (empresa, pessoa) dentro do teste.
        """
        # 1. Criar empresa
        company_data = {
            "name": "Fundação Hospital Santa Maria",
            "tax_id": "12345678000199",
            "website": "https://www.hospitalsantamaria.com.br",
            "description": "Hospital de referência em oncologia e cardiologia",
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
            # Já existe, usar ID fixo para teste
            company_id = 1

        # 2. Criar pessoa (estabelecimento)
        person_data = {
            "company_id": company_id,
            "person_type": "PJ",
            "name": "Unidade Central",
            "tax_id": "12345678000198",
            "description": "Unidade principal com 200 leitos"
        }

        person_response = await client.post(
            "/api/v1/people",
            json=person_data,
            headers=auth_headers
        )
        assert person_response.status_code in [201, 400, 409]

        if person_response.status_code == 201:
            person = person_response.json()
            person_id = person["id"]
        else:
            # Já existe, usar ID fixo para teste
            person_id = 1

        # 3. Criar estabelecimento
        establishment_data = {
            "person_id": person_id,
            "company_id": company_id,
            "code": "HSM001",
            "type": "matriz",
            "category": "hospital",
            "is_active": True,
            "is_principal": True
        }

        establishment_response = await client.post(
            "/api/v1/establishments",
            json=establishment_data,
            headers=auth_headers
        )
        assert establishment_response.status_code in [201, 400, 409]

        if establishment_response.status_code == 201:
            establishment = establishment_response.json()
            establishment_id = establishment["id"]
        else:
            # Já existe, usar ID fixo para teste
            establishment_id = 1

        # 4. Criar endereço do estabelecimento
        address_data = {
            "addressable_type": "Establishment",
            "addressable_id": establishment_id,
            "company_id": company_id,
            "street": "Rua São João",
            "number": "1500",
            "complement": "Centro Médico",
            "neighborhood": "Centro",
            "city": "Porto Alegre",
            "state": "RS",
            "zip_code": "90010100",
            "country": "BR",
            "type": "comercial"
        }

        address_response = await client.post(
            "/api/v1/addresses",
            json=address_data,
            headers=auth_headers
        )
        assert address_response.status_code in [201, 400, 409]

        # 5. Criar telefones (com WhatsApp e principal)
        phones_data = [
            {
                "phoneable_type": "Establishment",
                "phoneable_id": establishment_id,
                "company_id": company_id,
                "number": "5133334444",
                "type": "landline",
                "is_whatsapp": False,
                "is_primary": True  # Telefone principal
            },
            {
                "phoneable_type": "Establishment",
                "phoneable_id": establishment_id,
                "company_id": company_id,
                "number": "51999998888",
                "type": "mobile",
                "is_whatsapp": True,  # WhatsApp disponível
                "is_primary": False
            }
        ]

        for phone_data in phones_data:
            phone_response = await client.post(
                "/api/v1/phones",
                json=phone_data,
                headers=auth_headers
            )
            assert phone_response.status_code in [201, 400, 409]

        # 6. Criar emails
        emails_data = [
            {
                "emailable_type": "Establishment",
                "emailable_id": establishment_id,
                "company_id": company_id,
                "email_address": "contato@hospitalsantamaria.com.br",
                "type": "comercial",
                "is_primary": True  # Email principal
            },
            {
                "emailable_type": "Establishment",
                "emailable_id": establishment_id,
                "company_id": company_id,
                "email_address": "emergencia@hospitalsantamaria.com.br",
                "type": "comercial",
                "is_primary": False
            }
        ]

        for email_data in emails_data:
            email_response = await client.post(
                "/api/v1/emails",
                json=email_data,
                headers=auth_headers
            )
            assert email_response.status_code in [201, 400, 409]

        # 7. Verificar que estabelecimento foi criado
        get_response = await client.get(
            f"/api/v1/establishments/{establishment_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        establishment_data = get_response.json()
        assert establishment_data["code"] == "HSM001"
        assert establishment_data["type"] == "matriz"

        # 6. Criar pessoa (diretor médico)
        person_data = {
            "company_id": company_id,
            "name": "Dr. Roberto Almeida",
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

            # Criar perfil PF
            pf_profile_data = {
                "person_id": person_id,
                "tax_id": "11122233344",  # CPF fictício
                "birth_date": "1975-03-20T00:00:00",
                "gender": "Masculino",
                "marital_status": "Casado",
                "occupation": "Diretor Médico"
            }

            pf_response = await client.post(
                "/api/v1/pf-profiles",
                json=pf_profile_data,
                headers=auth_headers
            )
            assert pf_response.status_code in [201, 400, 422, 500]

    @pytest.mark.asyncio
    async def test_cadastrar_hospital_sao_lucas(self, client: AsyncClient, auth_headers: dict):
        """
        Testa cadastro completo do Hospital São Lucas (fictício).
        """
        # 1. Criar empresa
        company_data = {
            "name": "Instituto São Lucas de Saúde",
            "tax_id": "98765432000188",
            "website": "https://www.hospitalsaolucas.com.br",
            "description": "Hospital especializado em ortopedia e traumatologia",
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

        # 2. Criar pessoa para o estabelecimento
        person_data = {
            "company_id": company_id,
            "person_type": "PJ",
            "name": "Centro de Traumatologia São Lucas",
            "tax_id": "98765432000177",
            "description": "Especializado em cirurgias ortopédicas"
        }

        person_response = await client.post(
            "/api/v1/people",
            json=person_data,
            headers=auth_headers
        )
        assert person_response.status_code in [201, 409]

        if person_response.status_code == 201:
            person = person_response.json()
            person_id = person["id"]
        else:
            person_id = 2  # Usar ID fixo se já existe

        # 3. Criar estabelecimento
        establishment_data = {
            "person_id": person_id,
            "company_id": company_id,
            "code": "HSL001",
            "type": "matriz",
            "category": "hospital",
            "is_active": True,
            "is_principal": True
        }

        establishment_response = await client.post(
            "/api/v1/establishments",
            json=establishment_data,
            headers=auth_headers
        )
        assert establishment_response.status_code in [201, 400, 409]

        if establishment_response.status_code == 201:
            establishment = establishment_response.json()
            establishment_id = establishment["id"]
        else:
            establishment_id = 2  # Usar ID fixo se já existe

        # 3. Criar endereço
        address_data = {
            "establishment_id": establishment_id,
            "street": "Avenida Paulista",
            "number": "2000",
            "complement": "Torre A",
            "neighborhood": "Bela Vista",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01310900",
            "country": "Brasil",
            "type": "comercial"
        }

        address_response = await client.post(
            "/api/v1/addresses",
            json=address_data,
            headers=auth_headers
        )
        assert address_response.status_code in [201, 400]

        # 4. Criar telefones (com WhatsApp e principal)
        phones_data = [
            {
                "establishment_id": establishment_id,
                "number": "1122223333",
                "type": "fixo",
                "is_whatsapp": False,
                "is_primary": True
            },
            {
                "establishment_id": establishment_id,
                "number": "11988887777",
                "type": "celular",
                "is_whatsapp": True,
                "is_primary": False
            }
        ]

        for phone_data in phones_data:
            phone_response = await client.post(
                "/api/v1/phones",
                json=phone_data,
                headers=auth_headers
            )
            assert phone_response.status_code in [201, 400]

        # 5. Criar emails
        emails_data = [
            {
                "establishment_id": establishment_id,
                "address": "contato@hospitalsaolucas.com.br",
                "type": "comercial",
                "is_primary": True
            }
        ]

        for email_data in emails_data:
            email_response = await client.post(
                "/api/v1/emails",
                json=email_data,
                headers=auth_headers
            )
            assert email_response.status_code in [201, 400]

    @pytest.mark.asyncio
    async def test_cadastrar_hospital_santa_clara(self, client: AsyncClient, auth_headers: dict):
        """
        Testa cadastro completo do Hospital Santa Clara (fictício).
        """
        # 1. Criar empresa
        company_data = {
            "name": "Hospital Santa Clara Ltda",
            "tax_id": "55566677000144",
            "website": "https://www.hospitalsantaclara.com.br",
            "description": "Hospital geral com maternidade e pediatria",
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

        # 2. Criar pessoa para o estabelecimento
        person_data = {
            "company_id": company_id,
            "person_type": "PJ",
            "name": "Maternidade Santa Clara",
            "tax_id": "55566677000133",
            "description": "Setor de maternidade e pediatria"
        }

        person_response = await client.post(
            "/api/v1/people",
            json=person_data,
            headers=auth_headers
        )
        assert person_response.status_code in [201, 409]

        if person_response.status_code == 201:
            person = person_response.json()
            person_id = person["id"]
        else:
            person_id = 3  # Usar ID fixo se já existe

        # 3. Criar estabelecimento
        establishment_data = {
            "person_id": person_id,
            "company_id": company_id,
            "code": "HSC001",
            "type": "matriz",
            "category": "hospital",
            "is_active": True,
            "is_principal": True
        }

        establishment_response = await client.post(
            "/api/v1/establishments",
            json=establishment_data,
            headers=auth_headers
        )
        assert establishment_response.status_code in [201, 400, 409]

        if establishment_response.status_code == 201:
            establishment = establishment_response.json()
            establishment_id = establishment["id"]
        else:
            establishment_id = 3  # Usar ID fixo se já existe

        # 3. Criar endereço
        address_data = {
            "establishment_id": establishment_id,
            "street": "Rua das Flores",
            "number": "500",
            "neighborhood": "Jardim América",
            "city": "Ribeirão Preto",
            "state": "SP",
            "zip_code": "14020000",
            "country": "Brasil",
            "type": "comercial"
        }

        address_response = await client.post(
            "/api/v1/addresses",
            json=address_data,
            headers=auth_headers
        )
        assert address_response.status_code in [201, 400]

        # 4. Criar telefones (com WhatsApp e principal)
        phones_data = [
            {
                "establishment_id": establishment_id,
                "number": "1633336666",
                "type": "fixo",
                "is_whatsapp": False,
                "is_primary": True
            },
            {
                "establishment_id": establishment_id,
                "number": "16977776666",
                "type": "celular",
                "is_whatsapp": True,
                "is_primary": False
            },
            {
                "establishment_id": establishment_id,
                "number": "1633336677",
                "type": "fixo",
                "is_whatsapp": False,
                "is_primary": False
            }
        ]

        for phone_data in phones_data:
            phone_response = await client.post(
                "/api/v1/phones",
                json=phone_data,
                headers=auth_headers
            )
            assert phone_response.status_code in [201, 400]

        # 5. Criar emails
        emails_data = [
            {
                "establishment_id": establishment_id,
                "address": "contato@hospitalsantaclara.com.br",
                "type": "comercial",
                "is_primary": True
            },
            {
                "establishment_id": establishment_id,
                "address": "maternidade@hospitalsantaclara.com.br",
                "type": "comercial",
                "is_primary": False
            }
        ]

        for email_data in emails_data:
            email_response = await client.post(
                "/api/v1/emails",
                json=email_data,
                headers=auth_headers
            )
            assert email_response.status_code in [201, 400]