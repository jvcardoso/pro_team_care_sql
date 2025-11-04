"""
Endpoints para serviços externos
ViaCEP, ReceitaWS, Nominatim

Schema: [external]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_active_user
from app.schemas.external import (
    AddressEnrichmentRequest, AddressEnrichmentResponse,
    CNPJConsultRequest, CNPJConsultResponse,
    GeocodingRequest, GeocodingResponse,
    ReverseGeocodingRequest, ReverseGeocodingResponse,
    CompanyEnrichmentRequest, CompanyEnrichmentResponse
)
from app.services.address_enrichment_service import address_enrichment_service
from app.services.cnpj_service import cnpj_service
from app.services.geocoding_service import geocoding_service

router = APIRouter(prefix="/external", tags=["Serviços Externos"])


@router.post("/address/enrich", response_model=AddressEnrichmentResponse, status_code=status.HTTP_200_OK)
async def enrich_address(
    request: AddressEnrichmentRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Enriquece endereço automaticamente via ViaCEP

    - **cep**: CEP com ou sem formatação (8 dígitos)
    - Retorna dados completos do endereço + metadados
    """
    result = await address_enrichment_service.consult_viacep(request.cep)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CEP não encontrado ou inválido"
        )

    return AddressEnrichmentResponse(**result)


@router.post("/cnpj/consult", response_model=CNPJConsultResponse, status_code=status.HTTP_200_OK)
async def consult_cnpj(
    request: CNPJConsultRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Consulta dados da empresa via ReceitaWS

    - **cnpj**: CNPJ com ou sem formatação (14 dígitos)
    - Retorna dados cadastrais da empresa + metadados
    """
    result = await cnpj_service.consult_cnpj(request.cnpj)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CNPJ não encontrado ou inválido"
        )

    return CNPJConsultResponse(**result)


@router.post("/geocoding/forward", response_model=GeocodingResponse, status_code=status.HTTP_200_OK)
async def geocode_address(
    request: GeocodingRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Converte endereço em coordenadas via Nominatim

    - **address**: Endereço completo
    - **city**: Cidade (opcional, melhora precisão)
    - **state**: Estado (opcional, melhora precisão)
    - Retorna latitude, longitude e dados do local
    """
    result = await geocoding_service.geocode_address(
        request.address,
        request.city,
        request.state
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço não encontrado ou geocoding falhou"
        )

    return GeocodingResponse(**result)


@router.post("/geocoding/reverse", response_model=ReverseGeocodingResponse, status_code=status.HTTP_200_OK)
async def reverse_geocode(
    request: ReverseGeocodingRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Converte coordenadas em endereço via Nominatim

    - **latitude**: Latitude (-90 a 90)
    - **longitude**: Longitude (-180 a 180)
    - Retorna endereço completo do local
    """
    result = await geocoding_service.reverse_geocode(request.latitude, request.longitude)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coordenadas não encontradas ou reverse geocoding falhou"
        )

    return ReverseGeocodingResponse(**result)


@router.post("/company/enrich", response_model=CompanyEnrichmentResponse, status_code=status.HTTP_200_OK)
async def enrich_company_data(
    request: CompanyEnrichmentRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Enriquece dados completos da empresa usando múltiplos serviços externos

    - **cnpj**: CNPJ (opcional)
    - **cep**: CEP (opcional)
    - **endereco_completo**: Endereço completo (opcional)

    Pelo menos um dos campos deve ser fornecido.
    Retorna dados combinados de CNPJ, endereço e geocoding.
    """
    services_status = {
        "cnpj": "not_requested",
        "address": "not_requested",
        "geocoding": "not_requested"
    }

    cnpj_data = None
    address_data = None
    geocoding_data = None

    # Consulta CNPJ se fornecido
    if request.cnpj:
        cnpj_data = await cnpj_service.consult_cnpj(request.cnpj)
        services_status["cnpj"] = "success" if cnpj_data else "error"

    # Consulta endereço se CEP fornecido
    if request.cep:
        address_data = await address_enrichment_service.consult_viacep(request.cep)
        services_status["address"] = "success" if address_data else "error"

    # Geocoding se endereço fornecido
    if request.endereco_completo:
        geocoding_data = await geocoding_service.geocode_address(request.endereco_completo)
        services_status["geocoding"] = "success" if geocoding_data else "error"

    # Se nenhum serviço foi chamado com sucesso, erro
    if not any(status == "success" for status in services_status.values()):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum dos serviços externos retornou dados válidos"
        )

    return CompanyEnrichmentResponse(
        cnpj_data=CNPJConsultResponse(**cnpj_data) if cnpj_data else None,
        address_data=AddressEnrichmentResponse(**address_data) if address_data else None,
        geocoding_data=GeocodingResponse(**geocoding_data) if geocoding_data else None,
        services_status=services_status,
        _metadata={
            "source": "combined_external_services",
            "enriched_at": "2025-10-28T11:30:00Z",
            "version": "1.0"
        }
    )