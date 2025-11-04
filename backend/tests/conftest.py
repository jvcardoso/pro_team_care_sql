"""
Configuração de testes com pytest + httpx.

Fixtures para testes de API FastAPI com isolamento de transações.
"""
import os
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from tests.mocks.cnpj_mock_data import get_mock_cnpj_data, get_all_valid_cnpjs


# ========================================
# FIXTURES DE CONFIGURAÇÃO
# ========================================
@pytest.fixture(scope="session", autouse=True)
def override_test_settings():
    """Override configurações para usar bancos de teste."""
    import os
    os.environ["DB_NAME"] = "pro_team_care_test"
    os.environ["DB_LOGS_NAME"] = "pro_team_care_logs_test"


@pytest_asyncio.fixture
async def client():
    """Cliente HTTP para testes de API."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_token(client: AsyncClient):
    """
    Fixture que faz login real e retorna um token JWT válido.

    Faz login com usuário admin para obter token válido.
    """
    login_data = {
        "email_address": "admin@proteamcare.com.br",
        "password": "admin123"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200, f"Login falhou: {response.text}"
    token_data = response.json()
    return token_data["access_token"]


@pytest_asyncio.fixture
async def auth_headers(auth_token: str):
    """Headers com autenticação JWT."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def event_loop():
    """Cria um loop de eventos para cada teste (evita conflitos em testes parametrizados)"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def test_db():
    """Fixture que fornece uma sessão de banco de dados para testes."""
    # Configuração do banco de dados de teste
    test_db_url = os.getenv("TEST_DATABASE_URL", "mssql+aioodbc:///?odbc_connect=DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.11.84;DATABASE=pro_team_care_test;UID=sa;PWD=Jvc@1702;Encrypt=no")
    
    # Cria engine de teste
    engine = create_async_engine(
        test_db_url,
        echo=True,
        future=True,
        poolclass=StaticPool,
    )
    
    # Cria uma nova sessão de teste
    TestingSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
    )
    
    # Cria as tabelas do banco de dados de teste
    async with engine.begin() as conn:
        # Em um cenário real, você pode querer recriar as tabelas aqui
        # await conn.run_sync(Base.metadata.drop_all)
        # await conn.run_sync(Base.metadata.create_all)
        pass
    
    # Cria uma sessão de banco de dados que será usada nos testes
    db = TestingSessionLocal()
    
    # Sobrescreve a dependência get_db para usar a sessão de teste
    async def override_get_db():
        try:
            yield db
        finally:
            await db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        yield db
    finally:
        await db.close()
        await engine.dispose()


# ========================================
# FIXTURES DE DADOS DE TESTE
# ========================================
@pytest.fixture
def test_company():
    """Fixture que retorna dados mockados de empresa de teste."""
    return {
        "id": 1,
        "name": "Hospital Teste Ltda",
        "tax_id": "12345678000199"
    }


@pytest.fixture
def test_person():
    """Fixture que retorna dados mockados de pessoa de teste."""
    return {
        "id": 1,
        "name": "Unidade Central Teste",
        "tax_id": "12345678000198"
    }


# ========================================
# FIXTURES PARA SERVIÇOS EXTERNOS (ENRICHMENT)
# ========================================
@pytest.fixture
def mock_cnpj_response():
    """Fixture com resposta mockada do serviço CNPJ (ReceitaWS)."""
    return {
        "cnpj": "06990590000123",
        "nome": "GOOGLE BRASIL INTERNET LTDA",
        "fantasia": "GOOGLE",
        "abertura": "2005-04-29",
        "natureza_juridica": "Sociedade Empresária Limitada",
        "situacao": "ATIVA",
        "cnae_principal": "63.11-9-00",
        "cnae_principal_descricao": "Tratamento de dados, provedores de serviços de aplicação e serviços de hospedagem na internet",
        "logradouro": "Av. Brg. Faria Lima",
        "numero": "3477",
        "complemento": "19º andar",
        "bairro": "Itaim Bibi",
        "municipio": "São Paulo",
        "uf": "SP",
        "cep": "04538-133",
        "email": "",
        "telefone": "(11) 2395-8500",
        "data_situacao": "2005-04-29",
        "capital_social": "1000000.00"
    }


@pytest.fixture
def mock_viacep_response():
    """Fixture com resposta mockada do serviço ViaCEP."""
    return {
        "cep": "01001-000",
        "logradouro": "Praça da Sé",
        "complemento": "lado ímpar",
        "bairro": "Sé",
        "localidade": "São Paulo",
        "uf": "SP",
        "ibge": "3550308",
        "gia": "1004",
        "ddd": "11",
        "siafi": "7107"
    }


@pytest.fixture
def mock_geocoding_response():
    """Fixture com resposta mockada do serviço de geocoding (Nominatim)."""
    return {
        "lat": "-23.550520",
        "lon": "-46.633308",
        "display_name": "Praça da Sé, Sé, São Paulo, SP, Brasil",
        "address": {
            "road": "Praça da Sé",
            "suburb": "Sé",
            "city": "São Paulo",
            "state": "São Paulo",
            "country": "Brasil",
            "country_code": "br"
        }
    }


@pytest.fixture
def mock_enriched_company_data(mock_cnpj_response, mock_viacep_response):
    """Fixture com dados de empresa que serão enriquecidos."""
    return {
        "access_status": "active",
        "pj_profile": {
            "name": "",  # Será preenchido pelo CNPJ
            "trade_name": "",  # Será preenchido pelo CNPJ
            "tax_id": "11222333000144",  # CNPJ que será consultado
            "incorporation_date": None,  # Será preenchido pelo CNPJ
            "legal_nature": None  # Será preenchido pelo CNPJ
        },
        "addresses": [
            {
                "street": "",  # Será preenchido pelo CEP
                "number": "123",
                "neighborhood": "",  # Será preenchido pelo CEP
                "city": "",  # Será preenchido pelo CEP
                "state": "",  # Será preenchido pelo CEP
                "zip_code": "01001000",  # CEP que será consultado
                "country": "BR",
                "type": "commercial",
                "is_principal": True
            }
        ],
        "phones": [],
        "emails": []
    }


# ========================================
# MOCKS ROBUSTOS PARA APIS EXTERNAS
# ========================================
@pytest.fixture(autouse=True)
def mock_external_apis_robust():
    """Mocks robustos para APIs externas - elimina rate limits e falhas"""
    from unittest.mock import patch
    
    with patch('app.services.cnpj_service.CNPJService.consult_cnpj') as mock_cnpj, \
         patch('app.services.address_enrichment_service.AddressEnrichmentService.consult_viacep') as mock_viacep, \
         patch('app.services.geocoding_service.GeocodingService.geocode_address') as mock_geocode:
        
        # Mock CNPJ com dados completos dos 12 hospitais
        def cnpj_side_effect(cnpj):
            mock_data = get_mock_cnpj_data(cnpj)
            if mock_data:
                return mock_data
            else:
                # CNPJ não encontrado - simular erro da API
                raise Exception(f"CNPJ {cnpj} não encontrado na Receita Federal")
        
        mock_cnpj.side_effect = cnpj_side_effect
        
        # Mock ViaCEP sempre retorna dados válidos
        mock_viacep.return_value = {
            "logradouro": "RUA EXEMPLO TESTE",
            "bairro": "CENTRO",
            "localidade": "SÃO PAULO",
            "uf": "SP",
            "cep": "01001000",
            "ibge": "3550308"
        }
        
        # Mock Geocoding sempre retorna coordenadas válidas
        mock_geocode.return_value = {
            "latitude": -23.5505,
            "longitude": -46.6333,
            "accuracy": "high"
        }
        
        yield {
            "mock_cnpj": mock_cnpj,
            "mock_viacep": mock_viacep,
            "mock_geocode": mock_geocode
        }