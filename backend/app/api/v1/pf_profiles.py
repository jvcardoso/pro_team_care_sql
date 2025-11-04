"""
Endpoints CRUD de PF Profiles (Perfis Pessoa Física).

Schema: [core]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
⚠️  Usuários podem gerenciar apenas perfis da própria empresa
⚠️  Validações: CPF único, person_id deve existir e não ter PF profile
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.repositories.base import BaseRepository
from app.schemas.pf_profile import PFProfileCreate, PFProfileUpdate, PFProfileResponse
from app.models.pf_profile import PFProfile
from app.models.person import Person

router = APIRouter(prefix="/pf-profiles", tags=["Perfis PF"])


@router.get("", response_model=list[PFProfileResponse])
async def list_pf_profiles(
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os perfis PF da empresa do usuário autenticado.

    Dados sensíveis são mascarados automaticamente pelo banco.
    Requer autenticação JWT.
    """
    from sqlalchemy import text

    # Usar view segura para mascaramento automático
    query = text("""
        SELECT id, person_id, tax_id, birth_date, created_at, updated_at
        FROM [core].[vw_secure_pf_profiles]
        WHERE person_id IN (
            SELECT id FROM [core].[people] WHERE company_id = :company_id
        )
        ORDER BY id
        OFFSET :skip ROWS
        FETCH NEXT :limit ROWS ONLY
    """)

    result = await db.execute(query, {"company_id": current_user.company_id, "skip": skip, "limit": limit})
    pf_profiles = result.mappings().all()

    return pf_profiles


@router.get("/{profile_id}", response_model=PFProfileResponse)
async def get_pf_profile(
    profile_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca perfil PF por ID.

    Dados sensíveis são mascarados automaticamente pelo banco.
    Requer autenticação JWT.
    Usuário só pode acessar perfis da própria empresa.
    """
    from sqlalchemy import text

    # Usar view segura
    query = text("""
        SELECT id, person_id, tax_id, birth_date, created_at, updated_at
        FROM [core].[vw_secure_pf_profiles]
        WHERE id = :profile_id AND person_id IN (
            SELECT id FROM [core].[people] WHERE company_id = :company_id
        )
    """)

    result = await db.execute(query, {"profile_id": profile_id, "company_id": current_user.company_id})
    pf_profile = result.mappings().first()

    if not pf_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil PF não encontrado ou acesso negado"
        )

    return pf_profile


@router.post("", response_model=PFProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_pf_profile(
    profile_data: PFProfileCreate,
    request: Request,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria novo perfil PF.

    Requer autenticação JWT.
    Validações:
    - Person deve existir e pertencer à empresa do usuário
    - Person não pode já ter perfil PF
    - CPF deve ser único
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

    # Verificar se person já tem perfil PF
    if person.has_pf_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person já possui perfil PF"
        )

    # Verificar unicidade do CPF
    from sqlalchemy import select
    query = select(PFProfile).where(PFProfile.tax_id == profile_data.tax_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )

    # Criar perfil
    pf_repo = BaseRepository(PFProfile, db)
    data = profile_data.model_dump()
    data['created_at'] = datetime.utcnow()
    data['updated_at'] = datetime.utcnow()

    pf_profile = await pf_repo.create(data)

    # Registrar auditoria de criação
    from sqlalchemy import text
    audit_query = text("""
        INSERT INTO [pro_team_care_logs].[core].[lgpd_audit_log]
        (user_id, action_type, entity_type, entity_id, changed_fields, ip_address)
        VALUES (:user_id, 'CREATE', 'pf_profiles', :entity_id, :changed_fields, :ip)
    """)

    client_ip = getattr(request, 'client', None)
    client_ip = client_ip.host if client_ip else "unknown"

    await db.execute(audit_query, {
        "user_id": current_user.id,
        "entity_id": pf_profile.id,
        "changed_fields": f'{{"tax_id": "{profile_data.tax_id}"}}',  # Exemplo simplificado
        "ip": client_ip
    })
    await db.commit()

    return pf_profile


@router.put("/{profile_id}", response_model=PFProfileResponse)
async def update_pf_profile(
    profile_id: int,
    profile_data: PFProfileUpdate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza perfil PF existente.

    Requer autenticação JWT.
    Usuário só pode editar perfis da própria empresa.
    """
    pf_repo = BaseRepository(PFProfile, db)
    pf_profile = await pf_repo.get_by_id(profile_id)

    if not pf_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil PF não encontrado"
        )

    # Verificar se pertence à empresa do usuário
    if pf_profile.person.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: perfil não pertence à sua empresa"
        )

    # Verificar unicidade do CPF se estiver sendo alterado
    if profile_data.tax_id and profile_data.tax_id != pf_profile.tax_id:
        from sqlalchemy import select
        query = select(PFProfile).where(PFProfile.tax_id == profile_data.tax_id)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )

    # Preparar dados (remover valores None)
    data = profile_data.model_dump(exclude_unset=True)

    updated_profile = await pf_repo.update(profile_id, data)

    return updated_profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pf_profile(
    profile_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deleta perfil PF (soft delete).

    Requer autenticação JWT.
    Usuário só pode deletar perfis da própria empresa.
    """
    pf_repo = BaseRepository(PFProfile, db)
    pf_profile = await pf_repo.get_by_id(profile_id)

    if not pf_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil PF não encontrado"
        )

    # Verificar se pertence à empresa do usuário
    if pf_profile.person.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: perfil não pertence à sua empresa"
        )

    success = await pf_repo.delete(profile_id, soft=True)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erro ao deletar perfil PF"
        )


@router.post("/{profile_id}/reveal", response_model=dict)
async def reveal_pf_profile_data(
    profile_id: int,
    fields_to_reveal: list[str],  # Lista de campos a revelar
    request: Request,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revela dados sensíveis de um perfil PF sob demanda.

    Registra auditoria automaticamente.
    Requer autenticação JWT.
    """
    import json
    from sqlalchemy import text

    # Verificar se perfil existe e pertence à empresa
    query = text("""
        SELECT p.id FROM [core].[pf_profiles] pf
        JOIN [core].[people] p ON pf.person_id = p.id
        WHERE pf.id = :profile_id AND p.company_id = :company_id
    """)
    result = await db.execute(query, {"profile_id": profile_id, "company_id": current_user.company_id})
    if not result.scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil PF não encontrado ou acesso negado"
        )

    # Chamar procedure de revelação
    reveal_query = text("""
        EXEC [core].[sp_reveal_sensitive_data]
            @entity_type = 'pf_profiles',
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