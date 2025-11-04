"""
Endpoints CRUD de People.

Schema: [core]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
⚠️  Apenas usuários da mesma empresa podem acessar/modificar
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.repositories.base import BaseRepository
from app.schemas.person import PersonCreate, PersonUpdate, PersonResponse, PersonListResponse
from app.models.person import Person

router = APIRouter(prefix="/people", tags=["Pessoas"])


@router.get("", response_model=PersonListResponse)
async def list_people(
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todas as people com paginação.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Person, db)

    people = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()

    return PersonListResponse(total=total, people=people)


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca person por ID.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Person, db)
    person = await repo.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada"
        )

    return person


@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(
    person_data: PersonCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria nova person com perfil PF ou PJ.

    O campo person_type determina se cria perfil PF ou PJ.
    Requer autenticação JWT.
    """
    from datetime import datetime
    from app.models.pf_profile import PFProfile
    from app.models.pj_profile import PJProfile
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy import select

    # Extrair person_type antes de criar person
    person_type = person_data.person_type
    
    # Verificar se já existe perfil com esse tax_id na mesma empresa
    if person_type == "PJ":
        stmt = select(PJProfile).where(
            PJProfile.tax_id == person_data.tax_id,
            PJProfile.company_id == person_data.company_id
        )
        result = await db.execute(stmt)
        existing_pj = result.scalar_one_or_none()
        if existing_pj:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe uma pessoa jurídica com o CNPJ {person_data.tax_id} nesta empresa"
            )
    elif person_type == "PF":
        stmt = select(PFProfile).where(PFProfile.tax_id == person_data.tax_id)
        result = await db.execute(stmt)
        existing_pf = result.scalar_one_or_none()
        if existing_pf:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe uma pessoa física com o CPF {person_data.tax_id}"
            )
    
    try:
        # Preparar dados da person (remover campos que não existem no model Person)
        person_dict = person_data.model_dump(exclude={
            'person_type', 'secondary_tax_id', 'birth_date', 'incorporation_date',
            'gender', 'marital_status', 'occupation', 'tax_regime', 
            'legal_nature', 'municipal_registration', 'trade_name', 'tax_id'
        })
        person_dict['created_at'] = datetime.utcnow()
        person_dict['updated_at'] = datetime.utcnow()

        # Criar person
        person_repo = BaseRepository(Person, db)
        person = await person_repo.create(person_dict)

        # Criar perfil PF ou PJ conforme person_type
        if person_type == "PF":
            pf_data = {
                'person_id': person.id,
                'tax_id': person_data.tax_id,
                'birth_date': person_data.birth_date,
                'gender': person_data.gender,
                'marital_status': person_data.marital_status,
                'occupation': person_data.occupation,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            pf_repo = BaseRepository(PFProfile, db)
            await pf_repo.create(pf_data)
        
        elif person_type == "PJ":
            pj_data = {
                'person_id': person.id,
                'company_id': person_data.company_id,
                'tax_id': person_data.tax_id,
                'trade_name': person_data.trade_name,
                'incorporation_date': person_data.incorporation_date,
                'tax_regime': person_data.tax_regime,
                'legal_nature': person_data.legal_nature,
                'municipal_registration': person_data.municipal_registration,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            pj_repo = BaseRepository(PJProfile, db)
            await pj_repo.create(pj_data)

        return person
    
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro de integridade: registro duplicado ou violação de constraint"
        )


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: int,
    person_data: PersonUpdate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza person existente.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Person, db)

    # Preparar dados (remover valores None)
    data = person_data.model_dump(exclude_unset=True)

    person = await repo.update(person_id, data)

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada"
        )

    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deleta person (soft delete).

    Requer autenticação JWT.
    """
    repo = BaseRepository(Person, db)

    success = await repo.delete(person_id, soft=True)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada"
        )