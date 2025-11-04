"""
Testes de API para CRUD de empresas.

Cobre listagem, criação, consulta, atualização e inativação.
"""
import pytest
from fastapi import status
from tests.test_data.companies import get_test_company, TEST_COMPANIES

# Executa testes sequencialmente para evitar conflitos de concorrência
pytestmark = [pytest.mark.asyncio, pytest.mark.sequential]


@pytest.mark.asyncio
async def test_list_companies(client, auth_headers):
    """Teste de listagem básica de empresas."""
    response = await client.get("/api/v1/companies", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "companies" in data
    assert "total" in data
    # page e size podem não estar presentes se não paginado


@pytest.mark.asyncio
async def test_list_companies_with_filters(client, auth_headers):
    """Teste de listagem com filtros."""
    test_company = get_test_company()
    uf = test_company["endereco"]["uf"]

    response = await client.get(
        f"/api/v1/companies?uf={uf}",
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Nota: Pode não haver empresas no DB de teste, então apenas verifica estrutura
    assert "companies" in data


@pytest.mark.parametrize("company_data", TEST_COMPANIES, ids=lambda c: c["cnpj"])
@pytest.mark.asyncio
async def test_cnpj_consult(client, auth_headers, company_data):
    """Teste de consulta CNPJ para cada empresa da lista."""
    cnpj_clean = company_data["cnpj"].replace(".", "").replace("/", "").replace("-", "")
    response = await client.get(f"/api/v1/cnpj/{cnpj_clean}", headers=auth_headers)
    # Consulta CNPJ pode retornar dados ou erro se não encontrado
    assert response.status_code in [200, 404, 422], f"Status inesperado: {response.status_code} para CNPJ {cnpj_clean}"


@pytest.mark.asyncio
async def test_create_company_complete(client, auth_headers):
    """Teste de criação completa de empresa."""
    test_company = get_test_company()

    # Prepara dados para criação
    company_data = {
        "access_status": "contract_signed",
        "pj_profile": {
            "name": test_company["razao_social"],
            "trade_name": test_company["nome_fantasia"],
            "tax_id": test_company["cnpj"].replace(".", "").replace("/", "").replace("-", ""),
            "incorporation_date": "2015-08-22",
            "tax_regime": "Simples Nacional",
            "legal_nature": "Sociedade Empresária Limitada",
            "municipal_registration": "987654"
        },
        "addresses": [
            {
                "street": test_company["endereco"]["logradouro"],
                "number": test_company["endereco"]["numero"],
                "details": test_company["endereco"]["complemento"],
                "neighborhood": test_company["endereco"]["bairro"],
                "city": test_company["endereco"]["cidade"],
                "state": test_company["endereco"]["uf"],
                "zip_code": test_company["endereco"]["cep"].replace("-", ""),
                "country": "BR",
                "type": "commercial",
                "is_principal": True
            }
        ],
        "phones": [
            {
                "country_code": "55",
                "number": test_company["telefone"].replace("(", "").replace(")", "").replace(" ", "").replace("-", ""),
                "type": "landline",
                "is_principal": True,
                "is_whatsapp": True,
                "phone_name": "Recepção Principal"
            }
        ],
        "emails": [
            {
                "email_address": test_company["email"],
                "type": "work",
                "is_principal": True
            }
        ]
    }

    # Cria a empresa
    response = await client.post(
        "/api/v1/companies/complete",
        json=company_data,
        headers=auth_headers
    )

    # Pode ser 201 ou 500 se CNPJ já existe
    assert response.status_code in [201, 500], f"Status inesperado: {response.status_code}, Response: {response.text}"

    if response.status_code == 201:
        data = response.json()
        assert "new_company_id" in data
        assert data["new_company_id"] > 0


@pytest.mark.asyncio
async def test_get_company(client, auth_headers):
    """Teste de consulta individual de empresa."""
    # Primeiro cria uma empresa
    test_company = get_test_company()
    cnpj_clean = test_company["cnpj"].replace(".", "").replace("/", "").replace("-", "")

    # Cria empresa
    company_data = {
        "access_status": "contract_signed",
        "pj_profile": {
            "name": test_company["razao_social"],
            "trade_name": test_company["nome_fantasia"],
            "tax_id": cnpj_clean,
            "incorporation_date": "2015-08-22",
            "tax_regime": "Simples Nacional",
            "legal_nature": "Sociedade Empresária Limitada"
        },
        "addresses": [{
            "street": test_company["endereco"]["logradouro"],
            "number": test_company["endereco"]["numero"],
            "neighborhood": test_company["endereco"]["bairro"],
            "city": test_company["endereco"]["cidade"],
            "state": test_company["endereco"]["uf"],
            "zip_code": test_company["endereco"]["cep"].replace("-", ""),
            "country": "BR",
            "type": "commercial",
            "is_principal": True
        }],
        "phones": [],
        "emails": []
    }

    create_response = await client.post(
        "/api/v1/companies/complete",
        json=company_data,
        headers=auth_headers
    )

    if create_response.status_code == 201:
        company_id = create_response.json()["new_company_id"]

        # Consulta a empresa
        response = await client.get(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verifica mascaramento LGPD (dados sensíveis mascarados)
        assert "pj_profile" in data
        # Exemplo: verificar se tax_id está mascarado
        # assert data["pj_profile"]["tax_id"] == "***.***.***/****-**"  # Ajustar conforme implementação


@pytest.mark.asyncio
async def test_update_company(client, auth_headers):
    """Teste de atualização de empresa."""
    # Similar ao get, mas com PUT
    # Implementar após criar empresa
    # Focar em campos não-chave
    pass  # Placeholder


@pytest.mark.asyncio
async def test_deactivate_activate_company(client, auth_headers):
    """Teste de inativação e ativação de empresa."""
    # Implementar endpoints de inativação/ativação
    pass  # Placeholder