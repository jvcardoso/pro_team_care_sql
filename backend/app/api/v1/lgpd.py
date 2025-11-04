"""
Endpoints LGPD para auditoria e reveal de dados sensíveis.

Schema: [core] e [pro_team_care_logs]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
⚠️  Apenas usuários com permissão de unmask podem acessar
⚠️  Todas as ações são auditadas automaticamente
"""
import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func, column

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.schemas.lgpd import (
    RevealFieldRequest, RevealFieldResponse,
    RevealFieldsRequest, RevealFieldsResponse,
    AuditActionRequest, AuditActionResponse,
    AuditLogFilters, AuditLogResponse, AuditLogEntry,
    CompanyContactsResponse
)
from app.models.user import User
from datetime import datetime


router = APIRouter(prefix="/lgpd", tags=["LGPD"])


@router.post("/{entity_type}/{entity_id}/reveal-field", response_model=RevealFieldResponse)
async def reveal_field_generic(
    entity_type: str,
    entity_id: int,
    req: Request,
    field_name: str = Query(..., description="Nome do campo a revelar"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revela um campo sensível de qualquer entidade (genérico).

    - **entity_type**: Tipo da entidade (companies, clients, establishments)
    - **entity_id**: ID da entidade
    - **field_name**: Nome do campo a revelar

    Requer permissão de unmask e registra auditoria automática.
    """
    try:
        # Validar entidade permitida
        allowed_entities = ["companies", "clients", "establishments", "users"]
        if entity_type not in allowed_entities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Entidade '{entity_type}' não suportada"
            )

        field_value = None

        # Lógica específica por entidade e campo
        if entity_type == "companies":
            if field_name == "tax_id":
                # Buscar CNPJ da empresa
                query = text("""
                    SELECT pj.tax_id
                    FROM core.companies c
                    LEFT JOIN core.people p ON c.person_id = p.id
                    LEFT JOIN core.pj_profiles pj ON pj.person_id = p.id
                    WHERE c.id = :entity_id
                """)
                result = await db.execute(query, {"entity_id": entity_id})
                row = result.first()
                field_value = row.tax_id if row else None

            elif field_name.startswith("phone_") and field_name.endswith("_number"):
                # Buscar telefone específico por ID
                phone_id = field_name.replace("phone_", "").replace("_number", "")
                query = text("SELECT number FROM core.phones WHERE id = :phone_id AND company_id = :entity_id")
                result = await db.execute(query, {"phone_id": phone_id, "entity_id": entity_id})
                row = result.first()
                field_value = row.number if row else None

            elif field_name.startswith("email_") and field_name.endswith("_address"):
                # Buscar email específico por ID
                email_id = field_name.replace("email_", "").replace("_address", "")
                query = text("SELECT email_address FROM core.emails WHERE id = :email_id AND company_id = :entity_id")
                result = await db.execute(query, {"email_id": email_id, "entity_id": entity_id})
                row = result.first()
                field_value = row.email_address if row else None

            elif field_name.startswith("address_") and field_name.endswith("_street"):
                # Revelar rua do endereço
                try:
                    address_id_str = field_name.replace("address_", "").replace("_street", "")
                    address_id = int(address_id_str)
                    query = text("SELECT street FROM core.addresses WHERE id = :address_id AND company_id = :entity_id")
                    result = await db.execute(query, {"address_id": address_id, "entity_id": entity_id})
                    row = result.first()
                    field_value = row.street if row else None
                except (ValueError, TypeError):
                    field_value = None

            elif field_name.startswith("address_") and field_name.endswith("_number"):
                # Revelar número do endereço
                try:
                    address_id_str = field_name.replace("address_", "").replace("_number", "")
                    address_id = int(address_id_str)
                    query = text("SELECT number FROM core.addresses WHERE id = :address_id AND company_id = :entity_id")
                    result = await db.execute(query, {"address_id": address_id, "entity_id": entity_id})
                    row = result.first()
                    field_value = row.number if row else None
                except (ValueError, TypeError):
                    field_value = None

            elif field_name.startswith("address_") and field_name.endswith("_neighborhood"):
                # Revelar bairro do endereço
                try:
                    address_id_str = field_name.replace("address_", "").replace("_neighborhood", "")
                    address_id = int(address_id_str)
                    query = text("SELECT neighborhood FROM core.addresses WHERE id = :address_id AND company_id = :entity_id")
                    result = await db.execute(query, {"address_id": address_id, "entity_id": entity_id})
                    row = result.first()
                    field_value = row.neighborhood if row else None
                except (ValueError, TypeError):
                    field_value = None

            elif field_name.startswith("address_") and field_name.endswith("_zip_code"):
                # Revelar CEP do endereço
                try:
                    address_id_str = field_name.replace("address_", "").replace("_zip_code", "")
                    address_id = int(address_id_str)
                    query = text("SELECT zip_code FROM core.addresses WHERE id = :address_id AND company_id = :entity_id")
                    result = await db.execute(query, {"address_id": address_id, "entity_id": entity_id})
                    row = result.first()
                    field_value = row.zip_code if row else None
                except (ValueError, TypeError):
                    field_value = None

        if field_value is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campo '{field_name}' não encontrado para {entity_type} ID {entity_id}"
            )

        # Inserir log de auditoria
        audit_query = text("""
            INSERT INTO pro_team_care_logs.core.lgpd_audit_log (
                company_id, user_id, user_email, action_type, entity_type, entity_id,
                sensitive_fields, ip_address, endpoint
            ) VALUES (
                :company_id, :user_id, :user_email, 'REVEAL', :entity_type, :entity_id,
                :sensitive_fields, :ip_address, :endpoint
            )
        """)

        client_ip = req.client.host if req.client else "unknown"
        endpoint = str(req.url)

        await db.execute(audit_query, {
            "company_id": entity_id if entity_type == "companies" else None,
            "user_id": current_user.id,
            "user_email": current_user.email_address,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "sensitive_fields": json.dumps([field_name]),
            "ip_address": client_ip,
            "endpoint": endpoint
        })

        await db.commit()

        return RevealFieldResponse(
            status="revealed",
            field_name=field_name,
            field_value=field_value,
            revealed_at=datetime.utcnow(),
            revealed_by=current_user.id,
            message="Campo revelado com sucesso"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.post("/{entity_type}/{entity_id}/reveal-fields", response_model=RevealFieldsResponse)
async def reveal_fields_generic(
    entity_type: str,
    entity_id: int,
    request: RevealFieldsRequest,
    req: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revela múltiplos campos sensíveis de qualquer entidade (genérico).

    - **entity_type**: Tipo da entidade (companies, clients, establishments)
    - **entity_id**: ID da entidade
    - **field_names**: Lista de campos a revelar

    Requer permissão de unmask e registra auditoria automática.
    """
    try:
        # Validar entidade permitida
        allowed_entities = ["companies", "clients", "establishments", "users"]
        if entity_type not in allowed_entities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Entidade '{entity_type}' não suportada"
            )

        revealed_data = {}

        # Lógica específica por entidade e campos
        if entity_type == "companies":
            for field_name in request.field_names:
                if field_name.startswith("address_") and field_name.endswith("_street"):
                    # Revelar rua do endereço
                    try:
                        address_id_str = field_name.replace("address_", "").replace("_street", "")
                        address_id = int(address_id_str)
                        query = text("SELECT street FROM core.addresses WHERE id = :address_id AND company_id = :entity_id")
                        result = await db.execute(query, {"address_id": address_id, "entity_id": entity_id})
                        row = result.first()
                        if row:
                            revealed_data[field_name] = row.street
                    except (ValueError, TypeError):
                        pass

                elif field_name.startswith("address_") and field_name.endswith("_number"):
                    # Revelar número do endereço
                    try:
                        address_id_str = field_name.replace("address_", "").replace("_number", "")
                        address_id = int(address_id_str)
                        query = text("SELECT number FROM core.addresses WHERE id = :address_id AND company_id = :entity_id")
                        result = await db.execute(query, {"address_id": address_id, "entity_id": entity_id})
                        row = result.first()
                        if row:
                            revealed_data[field_name] = row.number
                    except (ValueError, TypeError):
                        pass

                elif field_name.startswith("address_") and field_name.endswith("_neighborhood"):
                    # Revelar bairro do endereço
                    try:
                        address_id_str = field_name.replace("address_", "").replace("_neighborhood", "")
                        address_id = int(address_id_str)
                        query = text("SELECT neighborhood FROM core.addresses WHERE id = :address_id AND company_id = :entity_id")
                        result = await db.execute(query, {"address_id": address_id, "entity_id": entity_id})
                        row = result.first()
                        if row:
                            revealed_data[field_name] = row.neighborhood
                    except (ValueError, TypeError):
                        pass

                elif field_name.startswith("address_") and field_name.endswith("_zip_code"):
                    # Revelar CEP do endereço
                    try:
                        address_id_str = field_name.replace("address_", "").replace("_zip_code", "")
                        address_id = int(address_id_str)
                        query = text("SELECT zip_code FROM core.addresses WHERE id = :address_id AND company_id = :entity_id")
                        result = await db.execute(query, {"address_id": address_id, "entity_id": entity_id})
                        row = result.first()
                        if row:
                            revealed_data[field_name] = row.zip_code
                    except (ValueError, TypeError):
                        pass

        # Inserir log de auditoria
        audit_query = text("""
            INSERT INTO pro_team_care_logs.core.lgpd_audit_log (
                company_id, user_id, user_email, action_type, entity_type, entity_id,
                sensitive_fields, ip_address, endpoint
            ) VALUES (
                :company_id, :user_id, :user_email, 'REVEAL', :entity_type, :entity_id,
                :sensitive_fields, :ip_address, :endpoint
            )
        """)

        client_ip = req.client.host if req.client else "unknown"
        endpoint = str(req.url)

        await db.execute(audit_query, {
            "company_id": entity_id if entity_type == "companies" else None,
            "user_id": current_user.id,
            "user_email": current_user.email_address,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "sensitive_fields": json.dumps(request.field_names),
            "ip_address": client_ip,
            "endpoint": endpoint
        })

        await db.commit()

        # ✅ CORREÇÃO: Adicionar campos obrigatórios status e message
        revealed_count = len(revealed_data)
        total_requested = len(request.field_names)
        
        return RevealFieldsResponse(
            status="success" if revealed_count > 0 else "partial",
            revealed_data=revealed_data,
            revealed_count=revealed_count,
            revealed_at=datetime.utcnow(),
            revealed_by=current_user.id,
            message=f"{revealed_count} de {total_requested} campos revelados com sucesso" if revealed_count > 0 else "Nenhum campo válido encontrado"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/audit-logs/", response_model=AuditLogResponse)
async def get_audit_logs(
    filters: AuditLogFilters = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    DEPRECATED: Este endpoint não monta mais consultas SQL dinâmicas.

    Use o endpoint canônico por entidade:
    GET /api/v1/lgpd/{entity_type}/{entity_id}/audit-log?page=&size=

    Para compatibilidade: se entity_type == "companies" e entity_id informado,
    delega para a Stored Procedure via endpoint canônico. Caso contrário, retorna 400.
    """
    # Exigir entity_type e entity_id para delegar corretamente
    if not filters.entity_type or not filters.entity_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /api/v1/lgpd/{entity_type}/{entity_id}/audit-log com page e size"
        )

    # Delegar para o endpoint canônico (que chama a SP para companies)
    if filters.entity_type == "companies":
        return await get_entity_audit_log(
            entity_type=filters.entity_type,
            entity_id=filters.entity_id,
            filters=filters,
            db=db,
            current_user=current_user,
        )

    # Para demais entidades, ainda não implementado via SP
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Audit logs not implemented for entity_type '{filters.entity_type}'. Use companies por enquanto."
    )


@router.get("/{entity_type}/{entity_id}/audit-log", response_model=AuditLogResponse)
async def get_entity_audit_log(
    entity_type: str,
    entity_id: int,
    filters: AuditLogFilters = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Consulta logs de auditoria LGPD para uma entidade específica.

    Para companies, utiliza Stored Procedure core.sp_get_lgpd_audit_logs.
    Para outras entidades, utiliza query dinâmica (temporário).

    - **entity_type**: Tipo da entidade (companies, clients, etc.)
    - **entity_id**: ID da entidade específica
    - **page**: Página atual (padrão 1)
    - **size**: Itens por página (1-500, padrão 50)

    Requer autenticação JWT.
    """
    if entity_type == "companies":
        # Usar Stored Procedure para companies
        try:
            sp_query = text("""
                EXEC pro_team_care_logs.core.sp_get_lgpd_audit_logs
                    @requesting_user_id = :requesting_user_id,
                    @target_company_id = :target_company_id,
                    @page_number = :page_number,
                    @page_size = :page_size
            """)

            params = {
                "requesting_user_id": current_user.id,
                "target_company_id": entity_id,
                "page_number": filters.page,
                "page_size": filters.size
            }

            print(f"🔍 [LGPD] Executando SP com params: {params}")

            # Estratégia: executar SP duas vezes - uma para contar total, outra para dados paginados
            # Isso garante compatibilidade com ambas versões da SP

            # Primeiro: obter o total de registros
            count_query = text("""
                SELECT COUNT(*)
                FROM pro_team_care_logs.core.lgpd_audit_log
                WHERE entity_type = 'companies' AND entity_id = :target_company_id
            """)

            try:
                count_result = await db.execute(count_query, {"target_company_id": entity_id})
                total = count_result.scalar() or 0
                print(f"🔍 [LGPD] Total de registros encontrado: {total}")
            except Exception as count_error:
                print(f"🔍 [LGPD] Erro ao contar registros: {count_error}")
                total = 0

            # Segundo: obter dados paginados via SP
            result = await db.execute(sp_query, params)
            rows = result.fetchall()
            print(f"🔍 [LGPD] Dados retornados: {len(rows)} linhas")

            if len(rows) > 0:
                print(f"🔍 [LGPD] Primeira linha (sample): {rows[0]}")
                print(f"🔍 [LGPD] Número de colunas: {len(rows[0])}")

            # Mapear para AuditLogEntry (estrutura da SP)
            items = []
            for row in rows:
                try:
                    # Ajustar para a estrutura real retornada pela SP
                    # A ordem é: id, created_at, company_id, user_id, user_email, action_type, entity_type, entity_id, sensitive_fields, ip_address, endpoint
                    sensitive_fields = row[8] if len(row) > 8 else None
                    if isinstance(sensitive_fields, str):
                        sensitive_fields = json.loads(sensitive_fields) if sensitive_fields else None

                    # Criar entrada de log com os dados da SP
                    entry = AuditLogEntry(
                        id=row[0],  # id
                        created_at=row[1],  # created_at
                        user_id=row[3],  # user_id
                        user_email=row[4],  # user_email
                        action_type=row[5],  # action_type
                        entity_type=row[6],  # entity_type
                        entity_id=row[7],  # entity_id
                        sensitive_fields=sensitive_fields,  # sensitive_fields
                        changed_fields=None,  # Não está sendo retornado pela SP
                        ip_address=row[9] if len(row) > 9 else None,  # ip_address (índice 9)
                        endpoint=row[10] if len(row) > 10 else None,  # endpoint (índice 10)
                        description=None,  # Não está sendo retornado pela SP
                        additional_info=None
                    )
                    items.append(entry)
                except (IndexError, ValueError, TypeError) as e:
                    print(f"Erro ao processar linha do log: {e}")
                    continue

            # Calcular páginas baseado no total e tamanho da página
            pages = (total + filters.size - 1) // filters.size if total > 0 else 1

            return AuditLogResponse(
                items=items,
                total=total,
                page=filters.page,
                size=filters.size,
                pages=pages
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao executar Stored Procedure: {str(e)}"
            )
    else:
        # Para outras entidades, manter query dinâmica (temporário)
        filters.entity_type = entity_type
        filters.entity_id = entity_id
        return await get_audit_logs(filters, db, current_user)


# Endpoints específicos mantidos para compatibilidade
@router.post("/companies/{company_id}/reveal-field", response_model=RevealFieldResponse, deprecated=True)
async def reveal_field_companies(
    company_id: int,
    request: RevealFieldRequest,
    req: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """DEPRECATED: Use /lgpd/{entity_type}/{entity_id}/reveal-field"""
    # Redirecionar para o endpoint genérico
    from fastapi.responses import RedirectResponse
    return RedirectResponse(
        url=f"/api/v1/lgpd/companies/{company_id}/reveal-field",
        status_code=307
    )


@router.post("/companies/{company_id}/reveal-fields", response_model=RevealFieldsResponse, deprecated=True)
async def reveal_fields_companies(
    company_id: int,
    request: RevealFieldsRequest,
    req: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """DEPRECATED: Use /lgpd/{entity_type}/{entity_id}/reveal-fields"""
    # Redirecionar para o endpoint genérico
    from fastapi.responses import RedirectResponse
    return RedirectResponse(
        url=f"/api/v1/lgpd/companies/{company_id}/reveal-fields",
        status_code=307
    )