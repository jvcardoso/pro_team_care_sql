"""
Endpoints CRUD de PJ Profiles (Perfis Pessoa Jurídica).

Schema: [core]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
⚠️  Usuários podem gerenciar apenas perfis da própria empresa
⚠️  Validações: CNPJ único, person_id deve existir e não ter PJ profile
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.repositories.base import BaseRepository
from app.schemas.pj_profile import PJProfileCreate, PJProfileUpdate, PJProfileResponse
from app.models.pj_profile import PJProfile
from app.models.person import Person

router = APIRouter(prefix="/pj-profiles", tags=["Perfis PJ"])


@router.get("", response_model=list[PJProfileResponse])
async def list_pj_profiles(
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os perfis PJ da empresa do usuário autenticado.

    Dados sensíveis são mascarados automaticamente pelo banco.
    Requer autenticação JWT.
    """
    from sqlalchemy import text

    # Usar view segura (assumindo que será criada)
    query = text("""
        SELECT id, person_id, company_id, tax_id, trade_name, incorporation_date,
               tax_regime, legal_nature, municipal_registration, created_at, updated_at
        FROM [core].[vw_secure_pj_profiles]
        WHERE person_id IN (
            SELECT id FROM [core].[people] WHERE company_id = :company_id
        )
        ORDER BY id
        OFFSET :skip ROWS
        FETCH NEXT :limit ROWS ONLY
    """)

    result = await db.execute(query, {"company_id": current_user.company_id, "skip": skip, "limit": limit})
    pj_profiles = result.mappings().all()

    return pj_profiles


@router.get("/{profile_id}", response_model=PJProfileResponse)
async def get_pj_profile(
    profile_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca perfil PJ por ID.

    Dados sensíveis são mascarados automaticamente pelo banco.
    Requer autenticação JWT.
    Usuário só pode acessar perfis da própria empresa.
    """
    from sqlalchemy import text

    # Usar view segura
    query = text("""
        SELECT id, person_id, company_id, tax_id, trade_name, incorporation_date,
               tax_regime, legal_nature, municipal_registration, created_at, updated_at
        FROM [core].[vw_secure_pj_profiles]
        WHERE id = :profile_id AND person_id IN (
            SELECT id FROM [core].[people] WHERE company_id = :company_id
        )
    """)

    result = await db.execute(query, {"profile_id": profile_id, "company_id": current_user.company_id})
    pj_profile = result.mappings().first()

    if not pj_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil PJ não encontrado ou acesso negado"
        )

    return pj_profile


@router.post("", response_model=PJProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_pj_profile(
    profile_data: PJProfileCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria novo perfil PJ.

    Requer autenticação JWT.
    Validações:
    - Person deve existir e pertencer à empresa do usuário
    - Person não pode já ter perfil PJ
    - CNPJ deve ser único
    - Company deve existir
    """
    from datetime import datetime

    # Verificar se person existe e pertence à empresa
    person_repo = BaseRepository(Person, db)
    person = await person_repo.get_by_id(profile_data.person_id)

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person não encontrada"
        )

    if person.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Person não pertence à sua empresa"
        )

    # Verificar se person já tem perfil PJ
    if person.has_pj_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person já possui perfil PJ"
        )

    # Verificar se company existe
    company_repo = BaseRepository(Person, db)  # Company is also Person with PJ profile
    company = await company_repo.get_by_id(profile_data.company_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company não encontrada"
        )

    # Verificar unicidade do CNPJ
    from sqlalchemy import select
    query = select(PJProfile).where(PJProfile.tax_id == profile_data.tax_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já cadastrado"
        )

    # Criar perfil
    pj_repo = BaseRepository(PJProfile, db)
    data = profile_data.model_dump()
    data['created_at'] = datetime.utcnow()
    data['updated_at'] = datetime.utcnow()

    pj_profile = await pj_repo.create(data)

    return pj_profile


@router.put("/{profile_id}", response_model=PJProfileResponse)
async def update_pj_profile(
    profile_id: int,
    profile_data: PJProfileUpdate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza perfil PJ existente.

    Requer autenticação JWT.
    Usuário só pode editar perfis da própria empresa.
    """
    pj_repo = BaseRepository(PJProfile, db)
    pj_profile = await pj_repo.get_by_id(profile_id)

    if not pj_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil PJ não encontrado"
        )

    # Verificar se pertence à empresa do usuário
    if pj_profile.person.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: perfil não pertence à sua empresa"
        )

    # Verificar unicidade do CNPJ se estiver sendo alterado
    if profile_data.tax_id and profile_data.tax_id != pj_profile.tax_id:
        from sqlalchemy import select
        query = select(PJProfile).where(PJProfile.tax_id == profile_data.tax_id)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ já cadastrado"
            )

    # Preparar dados (remover valores None)
    data = profile_data.model_dump(exclude_unset=True)

    updated_profile = await pj_repo.update(profile_id, data)

    return updated_profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pj_profile(
    profile_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deleta perfil PJ (soft delete).

    Requer autenticação JWT.
    Usuário só pode deletar perfis da própria empresa.
    """
    pj_repo = BaseRepository(PJProfile, db)
    pj_profile = await pj_repo.get_by_id(profile_id)

    if not pj_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil PJ não encontrado"
        )

    # Verificar se pertence à empresa do usuário
    if pj_profile.person.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: perfil não pertence à sua empresa"
        )

    success = await pj_repo.delete(profile_id, soft=True)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erro ao deletar perfil PJ"
        )


@router.post("/{profile_id}/reveal", response_model=dict)
async def reveal_pj_profile_data(
    profile_id: int,
    fields_to_reveal: list[str],  # Lista de campos a revelar
    request: Request,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revela dados sensíveis de um perfil PJ sob demanda.

    Registra auditoria automaticamente.
    Requer autenticação JWT.
    """
    import json
    from sqlalchemy import text

    # Verificar se perfil existe e pertence à empresa
    query = text("""
        SELECT p.id FROM [core].[pj_profiles] pj
        JOIN [core].[people] p ON pj.person_id = p.id
        WHERE pj.id = :profile_id AND p.company_id = :company_id
    """)
    result = await db.execute(query, {"profile_id": profile_id, "company_id": current_user.company_id})
    if not result.scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil PJ não encontrado ou acesso negado"
        )

    # Chamar procedure de revelação
    reveal_query = text("""
        EXEC [core].[sp_reveal_sensitive_data]
            @entity_type = 'pj_profiles',
            @entity_id = :entity_id,
            @fields_to_reveal = :fields,
            @user_email = :email,
            @ip_address = :ip,
            @endpoint = :endpoint
    """)

    client_ip = request.client.host if request.client else "unknown"
    result = await db.execute(reveal_query, {
        "entity_id": profile_id,
        "fields": json.dumps(fields_to_reveal),
        "email": current_user.email,
        "ip": client_ip,
        "endpoint": str(request.url)
    })

    # Retornar dados revelados
    revealed_data = result.mappings().first()
    return revealed_data or {}