# backend/tests/conftest_fixed.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
import os
from unittest.mock import patch

# ✅ CORREÇÃO 1: Configuração do banco remoto
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "mssql+pyodbc://sa:SuaSenha@IP_DO_SERVIDOR/pro_team_care_test?driver=ODBC+Driver+17+for+SQL+Server&timeout=30"
)

# ✅ CORREÇÃO 2: Configuração do loop de eventos
@pytest.fixture(scope="session")
def event_loop():
    """Cria um loop de eventos para toda a sessão de teste"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def db_engine():
    """Engine do banco de dados com configurações otimizadas"""
    engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "timeout": 30,
            "autocommit": True
        }
    )
    return engine

@pytest.fixture(scope="function")
async def db_session(db_engine):
    """Sessão do banco com rollback automático"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="session")
async def async_client():
    """Cliente assíncrono para testes"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# ✅ CORREÇÃO 3: Autenticação com credenciais reais
@pytest.fixture(scope="session")
async def auth_token(async_client):
    """Token de autenticação válido para toda a sessão"""
    login_data = {
        "username": os.getenv("TEST_ADMIN_EMAIL", "admin@proteancare.com"),
        "password": os.getenv("TEST_ADMIN_PASSWORD", "admin123")
    }
    
    response = await async_client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200, f"Falha no login: {response.text}"
    
    token_data = response.json()
    return f"Bearer {token_data['access_token']}"

@pytest.fixture
def auth_headers(auth_token):
    """Headers de autenticação"""
    return {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }

# ✅ CORREÇÃO 4: CNPJs válidos para teste
VALID_TEST_CNPJS = {
    "14337098000185": {  # Hospital Unimed - AL
        "razao_social": "HOSPITAL UNIMED LTDA",
        "nome_fantasia": "HOSPITAL UNIMED",
        "uf": "AL",
        "cidade": "MACEIÓ"
    },
    "11679181739988": {  # Hospital São Camilo - AP  
        "razao_social": "HOSPITAL SAO CAMILO E SAO LUIS LTDA",
        "nome_fantasia": "HOSPITAL SAO CAMILO E SAO LUIS",
        "uf": "AP", 
        "cidade": "MACAPÁ"
    },
    "25979675000120": {  # Hospital Calixto - BA
        "razao_social": "HOSPITAL CALIXTO MIDLEJ FILHO LTDA",
        "nome_fantasia": "HOSPITAL CALIXTO MIDLEJ FILHO",
        "uf": "BA",
        "cidade": "ITABUNA"
    }
}

# ✅ CORREÇÃO 5: Mocks otimizados
@pytest.fixture(autouse=True)
def mock_external_apis():
    """Mocks para APIs externas com dados realistas"""
    with patch('app.services.cnpj_service.CNPJService.consult_cnpj') as mock_cnpj, \
         patch('app.services.address_enrichment_service.AddressEnrichmentService.consult_viacep') as mock_viacep, \
         patch('app.services.geocoding_service.GeocodingService.geocode_address') as mock_geocode:
        
        def cnpj_side_effect(cnpj):
            return VALID_TEST_CNPJS.get(cnpj, {})
        
        mock_cnpj.side_effect = cnpj_side_effect
        
        mock_viacep.return_value = {
            "logradouro": "RUA EXEMPLO",
            "bairro": "CENTRO", 
            "localidade": "SÃO PAULO",
            "uf": "SP",
            "cep": "01001000"
        }
        
        mock_geocode.return_value = {
            "latitude": -23.5505,
            "longitude": -46.6333
        }
        
        yield {
            "mock_cnpj": mock_cnpj,
            "mock_viacep": mock_viacep,
            "mock_geocode": mock_geocode
        }
