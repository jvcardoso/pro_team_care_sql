"""
Endpoints CRUD de Companies.

Schema: [core]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
⚠️  Apenas superusuários podem criar/editar/deletar companies
⚠️  Usuários normais podem apenas visualizar
"""
import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.repositories.base import BaseRepository
from app.schemas.company import (
    CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListResponse,
    CompanyCompleteCreate, CompanyCompleteResponse,
    CompanyCompleteUpdate, CompanyUpdateCompleteResponse
)
from app.schemas.lgpd import CompanyContactsResponse
from app.schemas.person import PersonCreate
from app.schemas.pj_profile import PJProfileCreate
from app.models.company import Company
from app.models.person import Person
from app.models.pj_profile import PJProfile
from datetime import datetime, timedelta

# Importar serviços externos
from app.services.cnpj_service import cnpj_service
from app.services.address_enrichment_service import address_enrichment_service
from app.services.geocoding_service import geocoding_service

router = APIRouter(prefix="/companies", tags=["Empresas"])


async def _enrich_company_data(company_data: CompanyCompleteCreate) -> CompanyCompleteCreate:
    """
    Enriquece dados da empresa usando serviços externos

    - CNPJ: consulta ReceitaWS para preencher dados da empresa
    - CEP: consulta ViaCEP para enriquecer endereço
    - Endereço completo: geocodificação para coordenadas

    Args:
        company_data: Dados originais da empresa

    Returns:
        Dados enriquecidos da empresa
    """
    enriched_data = company_data.model_copy(deep=True)

    try:
        # 1. Enriquecer dados do PJ Profile via CNPJ
        if company_data.pj_profile.tax_id:
            cnpj_result = await cnpj_service.consult_cnpj(company_data.pj_profile.tax_id)
            if cnpj_result:
                # Preencher campos que estão vazios
                if not enriched_data.pj_profile.name and cnpj_result.get("nome"):
                    enriched_data.pj_profile.name = cnpj_result["nome"]

                if not enriched_data.pj_profile.trade_name and cnpj_result.get("fantasia"):
                    enriched_data.pj_profile.trade_name = cnpj_result["fantasia"]

                if not enriched_data.pj_profile.incorporation_date and cnpj_result.get("abertura"):
                    enriched_data.pj_profile.incorporation_date = cnpj_result["abertura"]

                if not enriched_data.pj_profile.legal_nature and cnpj_result.get("natureza_juridica"):
                    enriched_data.pj_profile.legal_nature = cnpj_result["natureza_juridica"]

        # 2. Enriquecer endereços via CEP e geocoding
        for i, address in enumerate(enriched_data.addresses):
            # Enriquecer via CEP se disponível
            if address.zip_code:
                cep_result = await address_enrichment_service.consult_viacep(address.zip_code)
                if cep_result:
                    # Preencher campos que estão vazios
                    if not enriched_data.addresses[i].street and cep_result.get("logradouro"):
                        enriched_data.addresses[i].street = cep_result["logradouro"]

                    if not enriched_data.addresses[i].neighborhood and cep_result.get("bairro"):
                        enriched_data.addresses[i].neighborhood = cep_result["bairro"]

                    if not enriched_data.addresses[i].city and cep_result.get("localidade"):
                        enriched_data.addresses[i].city = cep_result["localidade"]

                    if not enriched_data.addresses[i].state and cep_result.get("uf"):
                        enriched_data.addresses[i].state = cep_result["uf"]

            # Geocodificação se endereço estiver completo
            if (address.street and address.city and address.state):
                address_str = f"{address.street}, {address.city}, {address.state}"
                if address.zip_code:
                    address_str += f", CEP: {address.zip_code}"

                # Nota: A geocodificação seria armazenada em campos adicionais do endereço
                # Por enquanto, apenas logamos que seria possível fazer
                # geocoding_result = await geocoding_service.geocode_address(address_str)
                # if geocoding_result:
                #     # Adicionar latitude/longitude aos dados do endereço
                #     pass

    except Exception as e:
        # Log do erro mas não falha a criação - enriquecimento é opcional
        print(f"Erro no enriquecimento automático: {str(e)}")
        # Em produção, usar logging adequado

    return enriched_data


@router.get("/complete-list", status_code=status.HTTP_200_OK)
async def list_companies_complete(
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista empresas completas usando a view vw_complete_company_data.
    
    Retorna dados agregados incluindo:
    - Informações da empresa
    - Razão social e nome fantasia
    - CNPJ (mascarado conforme LGPD)
    - Endereço principal
    - Telefones agregados
    - Emails agregados
    
    Requer autenticação JWT.
    """
    # Query na view com paginação
    query = text("""
        SELECT * FROM [core].[vw_complete_company_data]
        ORDER BY CompanyId DESC
        OFFSET :skip ROWS
        FETCH NEXT :limit ROWS ONLY
    """)
    
    result = await db.execute(query, {"skip": skip, "limit": limit})
    rows = result.fetchall()
    
    # Função auxiliar para parsing seguro de JSON
    def safe_json_parse(value):
        """Converte string JSON em objeto Python, retorna lista vazia se falhar"""
        if not value:
            return []
        if isinstance(value, (list, dict)):
            return value  # Já é objeto Python
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []

    # Converter para dicionários
    companies = []
    for row in rows:
        companies.append({
            "company_id": row.CompanyId,
            "access_status": row.CompanyAccessStatus,
            "person_id": row.PersonId,
            "pj_profile_id": row.PjProfileId,
            "razao_social": row.RazaoSocial,
            "nome_fantasia": row.NomeFantasia,
            "cnpj": row.CNPJ,
            "endereco": {
                "street": row.PrincipalStreet,
                "number": row.PrincipalNumber,
                "neighborhood": row.PrincipalNeighborhood,
                "city": row.PrincipalCity,
                "state": row.PrincipalState,
                "zip_code": row.PrincipalZipCode
            } if row.PrincipalStreet else None,
            "telefones": safe_json_parse(row.PhoneNumbers),
            "emails": safe_json_parse(row.EmailAddresses),
            "incorporation_date": row.incorporation_date,
            "created_at": row.CompanyCreatedAt
        })
    
    # Contar total
    count_query = text("SELECT COUNT(*) as total FROM [core].[vw_complete_company_data]")
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return {
        "total": total,
        "companies": companies
    }


@router.get("", response_model=CompanyListResponse, deprecated=True)
async def list_companies(
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todas as companies com paginação (dados básicos).

    ⚠️ **DEPRECATED**: Use GET /complete-list para dados completos com LGPD.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Company, db)

    companies = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()

    return CompanyListResponse(total=total, companies=companies)


@router.get("/{company_id}")
async def get_company(
    company_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca company completa por ID usando vw_complete_company_data.

    Retorna dados agregados incluindo:
    - Informações da empresa
    - Pessoa jurídica (people)
    - Perfil PJ (pj_profile)
    - Telefones agregados
    - Emails agregados
    - Endereço principal

    Requer autenticação JWT.
    """
    # Query na view para dados completos
    query = text("""
        SELECT TOP 1 * FROM [core].[vw_complete_company_data]
        WHERE CompanyId = :company_id
    """)

    result = await db.execute(query, {"company_id": company_id})
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company não encontrada"
        )

    # Função auxiliar para parsing seguro de JSON
    def safe_json_parse(value):
        """Converte string JSON em objeto Python, retorna lista vazia se falhar"""
        if not value:
            return []
        if isinstance(value, (list, dict)):
            return value  # Já é objeto Python
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []

    # Função auxiliar para converter datetime para string
    def format_datetime(dt):
        return dt.isoformat() if dt else None

    # Construir resposta completa
    company_data = {
        "id": row.CompanyId,
        "person_id": row.PersonId,
        "access_status": row.CompanyAccessStatus,
        "settings": None,  # View não inclui settings
        "display_order": 0,  # View não inclui display_order
        "created_at": format_datetime(row.CompanyCreatedAt),
        "updated_at": format_datetime(row.CompanyCreatedAt),  # View não tem updated_at separado
        # Dados relacionados da view
        "people": {
            "id": row.PersonId,
            "name": row.RazaoSocial,
            "trade_name": row.NomeFantasia,
            "tax_id": row.CNPJ,  # CNPJ mascarado da view
            "secondary_tax_id": getattr(row, 'SecondaryTaxId', None),  # IE mascarada
            "municipal_registration": getattr(row, 'MunicipalRegistration', None),  # IM mascarada
            "tax_regime": row.tax_regime,  # Regime tributário
            "legal_nature": row.legal_nature,  # Natureza jurídica
            "website": None,  # View não inclui website
            "description": None,  # View não inclui description
            "status": "active",  # Assumir ativo
            "is_active": True,  # Assumir ativo
            "company_id": row.CompanyId,
            "created_at": format_datetime(row.CompanyCreatedAt),
            "updated_at": format_datetime(row.CompanyCreatedAt)
        } if row.PersonId else None,
        "phones": safe_json_parse(row.PhoneNumbers),
        "emails": safe_json_parse(row.EmailAddresses),
        "addresses": [{
            "id": getattr(row, 'PrincipalAddressId', None),  # ✅ CORREÇÃO: Fallback para None se campo não existir
            "street": row.PrincipalStreet,
            "number": row.PrincipalNumber,
            "neighborhood": row.PrincipalNeighborhood,
            "city": row.PrincipalCity,
            "state": row.PrincipalState,
            "zip_code": row.PrincipalZipCode,
            "type": "business",  # Assumir comercial
            "is_principal": True,  # É o endereço principal da view
            "company_id": row.CompanyId,
            "created_at": format_datetime(row.CompanyCreatedAt),
            "updated_at": format_datetime(row.CompanyCreatedAt)
        }] if row.PrincipalStreet else []
    }

    return company_data


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED, deprecated=True)
async def create_company(
    company_data: CompanyCreate,
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria nova company.

    ⚠️ **DEPRECATED**: Use POST /complete para criação completa com JSON aninhado.

    Se person_id for fornecido, cria company vinculada a essa pessoa.
    Se name/tax_id forem fornecidos sem person_id, cria pessoa PJ e vincula.
    Verifica duplicatas por tax_id.
    Requer autenticação JWT + privilégios de superusuário.
    """
    from datetime import datetime
    from sqlalchemy import select

    person_id = company_data.person_id

    # Se person_id fornecido, apenas criar company
    if person_id:
        repo = BaseRepository(Company, db)
        data = {
            'person_id': person_id,
            'settings': company_data.settings,
            'display_order': company_data.display_order,
            'access_status': company_data.access_status,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        company = await repo.create(data)
        return company

    # Se name e tax_id fornecidos, verificar duplicata ou criar nova
    if company_data.name and company_data.tax_id:
        # Verificar se já existe PJ com esse tax_id
        stmt = select(PJProfile).where(PJProfile.tax_id == company_data.tax_id)
        result = await db.execute(stmt)
        existing_pj = result.scalar_one_or_none()

        if existing_pj:
            # Se já existe, retornar a company existente
            stmt = select(Person).where(Person.id == existing_pj.person_id)
            result = await db.execute(stmt)
            existing_person = result.scalar_one_or_none()

            if existing_person:
                repo = BaseRepository(Company, db)
                existing_company = await repo.get_by_id(existing_person.company_id)
                if existing_company:
                    return existing_company

        # Criar nova company + person + pj_profile
        # 1. Criar company (person_id = None inicialmente)
        company_repo = BaseRepository(Company, db)
        company_data_dict = {
            'person_id': None,
            'settings': company_data.settings,
            'display_order': company_data.display_order,
            'access_status': company_data.access_status,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        company = await company_repo.create(company_data_dict)

        # 2. Criar person
        person_repo = BaseRepository(Person, db)
        person_data = {
            'company_id': company.id,
            'name': company_data.name,
            'website': company_data.website,
            'description': company_data.description,
            'status': 'active',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        person = await person_repo.create(person_data)

        # 3. Criar pj_profile
        pj_repo = BaseRepository(PJProfile, db)
        pj_data = {
            'person_id': person.id,
            'company_id': company.id,
            'tax_id': company_data.tax_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await pj_repo.create(pj_data)

        # 4. Atualizar company.person_id
        await company_repo.update(company.id, {'person_id': person.id})

        return company

    # Se nada fornecido, erro
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Deve fornecer person_id OU name e tax_id para criar company"
    )


@router.post("/complete", response_model=CompanyCompleteResponse, status_code=status.HTTP_201_CREATED)
async def create_company_complete(
    company_data: CompanyCompleteCreate,
    enrich_data: bool = True,  # Novo parâmetro opcional
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria empresa completa usando stored procedure sp_create_company_from_json.

    Cria em uma única transação atômica:
    - Company (conta da empresa)
    - Person (entidade raiz PJ)
    - PJ Profile (dados específicos da PJ)
    - Addresses (múltiplos endereços)
    - Phones (múltiplos telefones)
    - Emails (múltiplos e-mails)

    **Recursos de Enriquecimento Automático:**
    - **CNPJ**: Consulta ReceitaWS para preencher razão social, nome fantasia, data de constituição
    - **CEP**: Consulta ViaCEP para completar endereço (logradouro, bairro, cidade, estado)
    - **Geocoding**: Converte endereço em coordenadas GPS (futuro)

    Args:
        enrich_data: Se True (padrão), tenta enriquecer dados automaticamente usando APIs externas

    Requer autenticação JWT + privilégios de superusuário.
    """
    import json

    try:
        # Enriquecer dados automaticamente se solicitado
        if enrich_data:
            company_data = await _enrich_company_data(company_data)

        # Converter dados Pydantic para dict e depois JSON
        json_data = company_data.model_dump()

        # Executar stored procedure
        result = await db.execute(
            text("EXEC [core].[sp_create_company_from_json] @jsonData = :json_data"),
            {"json_data": json.dumps(json_data, default=str)}
        )

        # Capturar o resultado
        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno: nenhum resultado retornado da stored procedure"
            )

        # Verificar se houve erro na procedure
        if 'NewCompanyId' not in row._mapping or row._mapping['NewCompanyId'] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falha ao criar empresa: verifique os dados enviados"
            )

        # ✅ CORREÇÃO: Validar se a empresa foi realmente criada
        company_id = row._mapping['NewCompanyId']
        
        # Verificar se a empresa existe no banco
        verify_query = text("""
            SELECT TOP 1 c.id 
            FROM [core].[companies] c
            INNER JOIN [core].[people] p ON c.person_id = p.id
            WHERE c.id = :company_id AND c.deleted_at IS NULL
        """)
        
        verify_result = await db.execute(verify_query, {"company_id": company_id})
        verify_row = verify_result.fetchone()
        
        if not verify_row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Stored procedure retornou sucesso mas empresa {company_id} não foi encontrada no banco. Possível rollback silencioso."
            )

        return CompanyCompleteResponse(
            new_company_id=row._mapping['NewCompanyId'],
            new_person_id=row._mapping['NewPersonId'],
            new_pj_profile_id=row._mapping['NewPjProfileId'],
            message="Empresa criada com sucesso"
        )

    except Exception as e:
        # Rollback automático em caso de erro
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar empresa: {str(e)}"
        )


@router.put("/{company_id}", response_model=CompanyResponse, deprecated=True)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza company existente.

    ⚠️ **DEPRECATED**: Use PUT /{id}/complete para atualização completa com JSON aninhado.

    Requer autenticação JWT + privilégios de superusuário.
    """
    repo = BaseRepository(Company, db)

    # Preparar dados (remover valores None)
    data = company_data.model_dump(exclude_unset=True)

    company = await repo.update(company_id, data)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company não encontrada"
        )

    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Deleta company (soft delete).

    Requer autenticação JWT + privilégios de superusuário.
    """
    repo = BaseRepository(Company, db)

    success = await repo.delete(company_id, soft=True)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company não encontrada"
        )


@router.get("/cnpj/{cnpj}", response_model=CompanyResponse)
async def get_company_by_cnpj(
    cnpj: str,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca empresa por CNPJ.

    Requer autenticação JWT.
    """
    from app.models.pj_profile import PJProfile

    # Limpar CNPJ (remover formatação)
    clean_cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "").upper()

    # Buscar PJ Profile por tax_id
    stmt = select(PJProfile).where(PJProfile.tax_id == clean_cnpj)
    result = await db.execute(stmt)
    pj_profile = result.scalar_one_or_none()

    if not pj_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada com este CNPJ"
        )

    # Buscar Person
    from app.models.person import Person
    stmt = select(Person).where(Person.id == pj_profile.person_id)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa jurídica não encontrada"
        )

    # Buscar Company
    stmt = select(Company).where(Company.person_id == person.id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    return company


@router.post("/{company_id}/reactivate", response_model=CompanyResponse)
async def reactivate_company(
    company_id: int,
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Reativa empresa inativa.

    Altera status de 'inactive' para 'active'.
    Requer autenticação JWT + privilégios de superusuário.
    """
    repo = BaseRepository(Company, db)

    # Verificar se empresa existe
    company = await repo.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    # Verificar se já está ativa
    if company.access_status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa já está ativa"
        )

    # Reativar
    updated_company = await repo.update(company_id, {"access_status": "active"})

    if not updated_company:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao reativar empresa"
        )

    return updated_company


@router.get("/search", response_model=CompanyListResponse)
async def search_companies(
    q: str = Query(..., min_length=1, max_length=100, description="Termo de busca"),
    limit: int = Query(50, ge=1, le=100, description="Limite de resultados"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca empresas por nome, nome fantasia ou CNPJ.

    Requer autenticação JWT.
    """
    # Query na view com busca
    query = text("""
        SELECT TOP (:limit) * FROM [core].[vw_complete_company_data]
        WHERE RazaoSocial LIKE :search_term
           OR NomeFantasia LIKE :search_term
           OR CNPJ LIKE :search_term
        ORDER BY CompanyId DESC
    """)

    search_term = f"%{q}%"
    result = await db.execute(query, {"limit": limit, "search_term": search_term})
    rows = result.fetchall()

    # Converter para CompanyResponse (simplificado)
    companies = []
    for row in rows:
        companies.append(CompanyResponse(
            id=row.CompanyId,
            person_id=row.PersonId,
            access_status=row.CompanyAccessStatus,
            settings=None,
            display_order=0,
            created_at=row.CompanyCreatedAt,
            updated_at=row.CompanyCreatedAt
        ))

    return CompanyListResponse(total=len(companies), companies=companies)


@router.get("/validate/cnpj/{cnpj}")
async def validate_cnpj(
    cnpj: str,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Valida se CNPJ já existe no sistema.

    Retorna se existe e dados básicos se encontrado.
    Requer autenticação JWT.
    """
    from app.models.pj_profile import PJProfile
    from app.models.person import Person

    # Limpar CNPJ
    clean_cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "").upper()

    # Buscar PJ Profile
    stmt = select(PJProfile).where(PJProfile.tax_id == clean_cnpj)
    result = await db.execute(stmt)
    pj_profile = result.scalar_one_or_none()

    if not pj_profile:
        return {"exists": False}

    # Buscar Person e Company para dados básicos
    stmt = select(Person).where(Person.id == pj_profile.person_id)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()

    if person:
        stmt = select(Company).where(Company.person_id == person.id)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()

        if company:
            return {
                "exists": True,
                "company": {
                    "id": company.id,
                    "name": person.name,
                    "trade_name": pj_profile.trade_name,
                    "tax_id": pj_profile.tax_id,
                    "status": company.access_status
                }
            }

    # Se chegou aqui, existe PJ Profile mas sem company completa
    return {"exists": True, "company": None}


@router.get("/{company_id}/stats")
async def get_company_stats(
    company_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca estatísticas agregadas da empresa.

    Inclui contagem de estabelecimentos, clientes, profissionais.
    Requer autenticação JWT.
    """
    from app.models.establishment import Establishment

    # Verificar se empresa existe
    stmt = select(Company).where(Company.id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    # Contar estabelecimentos
    stmt = select(func.count(Establishment.id)).where(
        and_(Establishment.company_id == company_id, Establishment.deleted_at.is_(None))
    )
    establishments_count = (await db.scalar(stmt)) or 0

    # Por enquanto, retornar apenas estabelecimentos
    # TODO: Implementar contagem de clientes e profissionais quando models estiverem disponíveis
    return {
        "company_id": company_id,
        "establishments_count": establishments_count,
        "clients_count": 0,  # TODO
        "professionals_count": 0  # TODO
    }


@router.put("/{company_id}/complete", response_model=CompanyUpdateCompleteResponse, status_code=status.HTTP_200_OK)
async def update_company_complete(
    company_id: int,
    company_data: CompanyCompleteUpdate,
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza empresa completa manualmente (até SP ser criada).

    Atualiza em uma única transação atômica:
    - Company (conta da empresa)
    - Person (entidade raiz PJ)
    - PJ Profile (dados específicos da PJ)
    - Addresses (múltiplos endereços)
    - Phones (múltiplos telefones)
    - Emails (múltiplos e-mails)

    Requer autenticação JWT + privilégios de superusuário.
    """
    from app.models.person import Person
    from app.models.pj_profile import PJProfile
    from app.models.address import Address
    from app.models.phone import Phone
    from app.models.email import Email

    try:
        # Verificar se empresa existe e obter dados relacionados
        stmt = select(Company).where(Company.id == company_id)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada"
            )

        # Obter Person e PJ Profile
        stmt = select(Person).where(Person.id == company.person_id)
        result = await db.execute(stmt)
        person = result.scalar_one_or_none()

        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pessoa jurídica não encontrada"
            )

        stmt = select(PJProfile).where(PJProfile.person_id == person.id)
        result = await db.execute(stmt)
        pj_profile = result.scalar_one_or_none()

        if not pj_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil PJ não encontrado"
            )

        # Atualizar Company se fornecido
        if company_data.access_status is not None:
            await db.execute(
                text("UPDATE [core].[companies] SET access_status = :status, updated_at = GETUTCDATE() WHERE id = :id"),
                {"status": company_data.access_status, "id": company_id}
            )

        # Atualizar Person/PJ Profile se fornecido
        if company_data.pj_profile:
            pj_data = company_data.pj_profile

            # Atualizar Person
            update_person = {}
            if pj_data.name:
                update_person["name"] = pj_data.name
            if pj_data.trade_name:
                update_person["website"] = pj_data.trade_name  # trade_name vai para website? Ajustar conforme model

            if update_person:
                update_person["updated_at"] = datetime.utcnow()
                await db.execute(
                    text("UPDATE [core].[people] SET name = :name, website = :website, updated_at = :updated_at WHERE id = :id"),
                    {"name": pj_data.name, "website": pj_data.trade_name, "updated_at": datetime.utcnow(), "id": person.id}
                )

            # Atualizar PJ Profile
            update_pj = {}
            if pj_data.tax_id:
                update_pj["tax_id"] = pj_data.tax_id
            if pj_data.incorporation_date:
                update_pj["incorporation_date"] = pj_data.incorporation_date
            if pj_data.tax_regime:
                update_pj["tax_regime"] = pj_data.tax_regime
            if pj_data.legal_nature:
                update_pj["legal_nature"] = pj_data.legal_nature
            if pj_data.municipal_registration:
                update_pj["municipal_registration"] = pj_data.municipal_registration

            if update_pj:
                update_pj["updated_at"] = datetime.utcnow()
                await db.execute(
                    text("UPDATE [core].[pj_profiles] SET tax_id = :tax_id, incorporation_date = :incorporation_date, tax_regime = :tax_regime, legal_nature = :legal_nature, municipal_registration = :municipal_registration, updated_at = :updated_at WHERE id = :id"),
                    {**update_pj, "id": pj_profile.id}
                )

        # TODO: Implementar atualização de addresses, phones, emails quando necessário

        # Commit da transação
        await db.commit()

        return CompanyUpdateCompleteResponse(
            updated_company_id=company_id,
            updated_person_id=person.id,
            updated_pj_profile_id=pj_profile.id,
            message="Empresa atualizada com sucesso"
        )

    except Exception as e:
        # Rollback automático em caso de erro
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar empresa: {str(e)}"
        )


@router.get("/admin/pending-companies", status_code=status.HTTP_200_OK)
async def list_pending_companies(
    days_old: int = Query(7, ge=1, le=365, description="Empresas criadas há mais de X dias"),
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Termo de busca por nome ou CNPJ"),
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista empresas com cadastro pendente (status = 'pending_contract').

    Retorna apenas empresas criadas há mais de X dias para evitar
    exclusão acidental de cadastros recentes.

    Requer autenticação JWT + privilégios de superusuário.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)

    # Query na view para empresas pendentes criadas há mais de X dias
    base_query = """
        SELECT CompanyId, RazaoSocial, CNPJ, CompanyCreatedAt
        FROM [core].[vw_complete_company_data]
        WHERE CompanyAccessStatus = 'pending_contract'
          AND CompanyCreatedAt < :cutoff_date
    """

    # Adicionar filtro de busca se fornecido
    params = {"cutoff_date": cutoff_date}
    if search:
        search_term = f"%{search}%"
        base_query += """
          AND (RazaoSocial LIKE :search_term OR CNPJ LIKE :search_term)
        """
        params["search_term"] = search_term

    base_query += " ORDER BY CompanyCreatedAt DESC"

    query = text(base_query)

    result = await db.execute(query, params)
    rows = result.fetchall()

    # Converter para formato de resposta
    pending_companies = []
    for row in rows:
        pending_companies.append({
            "company_id": row.CompanyId,
            "razao_social": row.RazaoSocial,
            "cnpj": row.CNPJ,
            "created_at": row.CompanyCreatedAt
        })

    return {
        "total": len(pending_companies),
        "companies": pending_companies,
        "cutoff_date": cutoff_date.isoformat(),
        "days_old_filter": days_old
    }


@router.delete("/admin/companies/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_pending_companies(
    company_ids: list[int],
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
 ):
    """
    Remove empresas pendentes e todos os dados relacionados.

    CORREÇÃO v4: Ordem completa com resolução de dependência circular:
    1. Logs LGPD (lgpd_audit_log) - se existir, dependem de company_id
    2. Logs de login (login_logs) - se existir, dependem de company_id
    3. Usuários (users) - dependem de company_id
    4. TODOS os contatos (phones, emails, addresses) - dependem de company_id
    5. Estabelecimentos (establishments) - dependem de company_id
    6. Perfis PJ (pj_profiles) - DELETADO DIRETAMENTE (não SET NULL!)
    7. Perfis PF (pf_profiles) - dependem de person_id
    8. QUEBRAR DEPENDÊNCIA CIRCULAR: SET companies.person_id = NULL
    9. Pessoas (people) - agora podem ser deletadas
    10. Empresas (companies) - por último, sem dependências

    DEPENDÊNCIA CIRCULAR RESOLVIDA:
    - companies.person_id → people.id (FK_companies_person)
    - people.company_id → companies.id (FK_people_company)

    NOTA: Tabelas de log são opcionais e podem não existir no banco.

    Requer autenticação JWT + privilégios de superusuário.
    """
    if not company_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lista de IDs de empresas não pode estar vazia"
        )

    results = []
    success_count = 0
    error_count = 0

    for company_id in company_ids:
        try:
            # Verificar se a empresa existe e está pendente
            company_result = await db.execute(
                text("SELECT person_id, access_status FROM [core].[companies] WHERE id = :company_id"),
                {"company_id": company_id}
            )
            company_data = company_result.fetchone()

            if not company_data:
                results.append({
                    "company_id": company_id,
                    "status": "error",
                    "message": f"Empresa {company_id} não encontrada"
                })
                error_count += 1
                continue

            person_id, access_status = company_data

            if access_status != 'pending_contract':
                results.append({
                    "company_id": company_id,
                    "status": "error",
                    "message": f"Empresa {company_id} não está com status 'pending_contract'"
                })
                error_count += 1
                continue

            # Executar exclusão em ordem segura respeitando todas as dependências
            # ORDEM CRÍTICA: Filhos antes dos pais, respeitando constraints NOT NULL

            # Função auxiliar para executar delete apenas se tabela existir
            async def safe_delete(table_name: str, where_clause: str, params: dict):
                try:
                    sql = f"DELETE FROM [core].[{table_name}] WHERE {where_clause}"
                    await db.execute(text(sql), params)
                    return True
                except Exception as e:
                    # Verificar se é erro de tabela não existente
                    if "Invalid object name" in str(e) or "42S02" in str(e):
                        return False  # Tabela não existe, pular
                    else:
                        raise  # Re-raise outros erros

            # Executar exclusão em ordem segura respeitando TODAS as dependências
            # ORDEM CRÍTICA: Deve deletar TUDO relacionado à empresa antes dela

            # 1. Deletar logs de auditoria LGPD relacionados à empresa (tabela opcional)
            await safe_delete("lgpd_audit_log", "company_id = :company_id", {"company_id": company_id})

            # 2. Deletar logs de login relacionados à empresa (tabela opcional)
            await safe_delete("login_logs", "company_id = :company_id", {"company_id": company_id})

            # 3. Deletar usuários relacionados à empresa
            await db.execute(
                text("DELETE FROM [core].[users] WHERE company_id = :company_id"),
                {"company_id": company_id}
            )

            # 4. Deletar TODOS os contatos (phones, emails, addresses) da empresa
            # IMPORTANTE: deletar ANTES dos estabelecimentos e perfis
            await db.execute(
                text("DELETE FROM [core].[phones] WHERE company_id = :company_id"),
                {"company_id": company_id}
            )

            await db.execute(
                text("DELETE FROM [core].[emails] WHERE company_id = :company_id"),
                {"company_id": company_id}
            )

            await db.execute(
                text("DELETE FROM [core].[addresses] WHERE company_id = :company_id"),
                {"company_id": company_id}
            )

            # 5. Deletar estabelecimentos
            await db.execute(
                text("DELETE FROM [core].[establishments] WHERE company_id = :company_id"),
                {"company_id": company_id}
            )

            # 6. Deletar perfis PJ de TODAS as pessoas da empresa
            # CORREÇÃO: Deletar todos os pj_profiles, não apenas da pessoa principal
            await db.execute(
                text("""
                    DELETE FROM [core].[pj_profiles]
                    WHERE person_id IN (
                        SELECT id FROM [core].[people] WHERE company_id = :company_id
                    )
                """),
                {"company_id": company_id}
            )

            # 7. Deletar perfis PF de TODAS as pessoas da empresa
            # CORREÇÃO: Deletar todos os pf_profiles, não apenas da pessoa principal
            await db.execute(
                text("""
                    DELETE FROM [core].[pf_profiles]
                    WHERE person_id IN (
                        SELECT id FROM [core].[people] WHERE company_id = :company_id
                    )
                """),
                {"company_id": company_id}
            )

            # 8. REMOVER DEPENDÊNCIA CIRCULAR: Setar person_id = NULL na empresa
            # Isso quebra a FK companies.person_id -> people.id
            await db.execute(
                text("UPDATE [core].[companies] SET person_id = NULL WHERE id = :company_id"),
                {"company_id": company_id}
            )

            # 9. Agora pode deletar TODAS as pessoas relacionadas à empresa (incluindo o dono)
            await db.execute(
                text("DELETE FROM [core].[people] WHERE company_id = :company_id"),
                {"company_id": company_id}
            )

            # 10. Deletar empresa (por último - NÃO é mais referenciada por nada)
            await db.execute(
                text("DELETE FROM [core].[companies] WHERE id = :company_id"),
                {"company_id": company_id}
            )

            await db.commit()  # Commit da transação

            results.append({
                "company_id": company_id,
                "status": "success",
                "message": f"Empresa {company_id} removida com sucesso"
            })
            success_count += 1

        except Exception as e:
            await db.rollback()  # Rollback em caso de erro
            error_message = str(e)
            print(f"ERRO na limpeza da empresa {company_id}: {error_message}")  # Log para debug

            results.append({
                "company_id": company_id,
                "status": "error",
                "message": f"Falha ao remover empresa {company_id}: {error_message}"
            })
            error_count += 1

    return {
        "total_processed": len(company_ids),
        "success_count": success_count,
        "error_count": error_count,
        "results": results,
        "message": f"Processamento concluído: {success_count} empresas removidas, {error_count} falhas"
    }


@router.get("/{company_id}/contacts", response_model=CompanyContactsResponse)
async def get_company_contacts(
    company_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca contatos de uma empresa (telefones e emails).

    Retorna dados agregados incluindo:
    - Informações básicas da empresa
    - Telefones com tipo e flag principal
    - Emails com tipo e flag principal

    Requer autenticação JWT.
    """
    try:
        # Query para buscar empresa e seus contatos
        query = text("""
            SELECT
                c.id as company_id,
                p.name,
                p.trade_name,
                -- Telefones (JSON array)
                (
                    SELECT
                        REPLACE(REPLACE(REPLACE(ph.number, '(', ''), ')', ''), ' ', '') as number,
                        ph.type,
                        ph.is_principal
                    FROM core.phones ph
                    WHERE ph.company_id = c.id
                    FOR JSON PATH
                ) as phones,
                -- Emails (JSON array)
                (
                    SELECT
                        em.email_address as email,
                        em.type,
                        em.is_principal
                    FROM core.emails em
                    WHERE em.company_id = c.id
                    FOR JSON PATH
                ) as emails
            FROM core.companies c
            LEFT JOIN core.people p ON c.person_id = p.id
            WHERE c.id = :company_id
        """)

        result = await db.execute(query, {"company_id": company_id})
        row = result.first()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada"
            )

        # Parse JSON arrays
        phones = json.loads(row.phones) if row.phones else []
        emails = json.loads(row.emails) if row.emails else []

        return CompanyContactsResponse(
            company_id=row.company_id,
            name=row.name,
            trade_name=row.trade_name,
            phones=phones,
            emails=emails
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.put("/{company_id}/complete", response_model=CompanyUpdateCompleteResponse, status_code=status.HTTP_200_OK)
async def update_company_complete(
    company_id: int,
    company_data: CompanyCompleteUpdate,
    enrich_data: bool = True,  # Novo parâmetro opcional
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza empresa completa usando stored procedure sp_update_company_from_json.

    Atualiza em uma única transação atômica:
    - Company (conta da empresa)
    - Person (entidade raiz PJ)
    - PJ Profile (dados específicos da PJ)
    - Addresses (múltiplos endereços)
    - Phones (múltiplos telefones)
    - Emails (múltiplos e-mails)

    **Recursos de Enriquecimento Automático:**
    - **CNPJ**: Consulta ReceitaWS para preencher dados da empresa
    - **CEP**: Consulta ViaCEP para completar endereço (logradouro, bairro, cidade, estado)
    - **Geocoding**: Converte endereço em coordenadas GPS (futuro)

    Args:
        company_id: ID da empresa a ser atualizada
        company_data: Dados atualizados da empresa
        enrich_data: Se True (padrão), tenta enriquecer dados automaticamente usando APIs externas

    Requer autenticação JWT + privilégios de superusuário.
    """
    import json

    try:
        # Verificar se empresa existe
        stmt = select(Company).where(Company.id == company_id)
        result = await db.execute(stmt)
        existing_company = result.scalar_one_or_none()

        if not existing_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada"
            )

        # Enriquecimento automático se solicitado
        enriched_data = company_data
        if enrich_data:
            # Criar dados completos para enriquecimento
            full_data = CompanyCompleteCreate(
                access_status=company_data.access_status or existing_company.access_status,
                pj_profile=company_data.pj_profile,
                addresses=company_data.addresses or [],
                phones=company_data.phones or [],
                emails=company_data.emails or []
            )
            enriched_data = await _enrich_company_data(full_data)

        # Converter dados Pydantic para dict e depois JSON
        json_data = enriched_data.model_dump()

        # Adicionar company_id aos dados
        json_data["company_id"] = company_id

        # Executar stored procedure de atualização
        result = await db.execute(
            text("EXEC [core].[sp_update_company_from_json] @jsonData = :json_data"),
            {"json_data": json.dumps(json_data, default=str)}
        )

        # Capturar o resultado
        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno: nenhum resultado retornado da stored procedure"
            )

        # Verificar se houve erro na procedure
        if 'UpdatedCompanyId' not in row._mapping or row._mapping['UpdatedCompanyId'] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falha ao atualizar empresa: verifique os dados enviados"
            )

        return CompanyUpdateCompleteResponse(
            updated_company_id=row._mapping['UpdatedCompanyId'],
            updated_person_id=row._mapping.get('UpdatedPersonId'),
            updated_pj_profile_id=row._mapping.get('UpdatedPjProfileId'),
            message="Empresa atualizada com sucesso"
        )

    except HTTPException:
        raise
    except Exception as e:
        # Rollback automático em caso de erro
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar empresa: {str(e)}"
        )
