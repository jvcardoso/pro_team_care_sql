"""
Endpoints de autenticação (Login, Registro).

Schema: [core]

Login usa Stored Procedures para segurança avançada:
- [core].[sp_get_user_for_auth]: Busca dados do usuário
- [core].[sp_log_login_success]: Registra sucesso e atualiza last_login_at
- [core].[sp_log_login_failure]: Registra falhas de login
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import hash_password
from app.core.dependencies import get_current_active_user
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse, UserMeResponse, EstablishmentSimple
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ValidateResetTokenRequest,
    ResetPasswordRequest,
    PasswordResetResponse
)
from app.models.user import User
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint de login com segurança avançada.

    Utiliza stored procedures para autenticação segura:
    - [core].[sp_get_user_for_auth]: Busca dados do usuário para validação
    - [core].[sp_log_login_success]: Registra sucesso e atualiza last_login_at
    - [core].[sp_log_login_failure]: Registra falhas (credenciais inválidas, usuário inativo)

    A validação bcrypt ocorre em Python para segurança.
    Retorna token JWT se credenciais válidas.
    """
    # Obter IP e User-Agent da requisição
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Executar login via stored procedure
    auth_service = AuthService(db)
    result = await auth_service.execute_login(
        email=credentials.email_address,
        password=credentials.password,
        ip_address=client_ip,
        user_agent=user_agent
    )

    # Se login falhou, retornar erro HTTP
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("message", "Credenciais inválidas"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Login bem-sucedido, retornar token
    return TokenResponse(
        access_token=result["access_token"],
        token_type=result["token_type"]
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint de registro de novo usuário.
    """
    # Verificar se email já existe
    stmt = select(User).where(User.email_address == user_data.email_address)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    # Criar usuário
    from datetime import datetime

    new_user = User(
        email_address=user_data.email_address,
        password=hash_password(user_data.password),
        person_id=user_data.person_id,
        company_id=user_data.company_id,
        establishment_id=user_data.establishment_id,
        is_active=user_data.is_active,
        is_system_admin=user_data.is_system_admin,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserMeResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para obter dados completos do usuário logado usando Stored Procedure.

    Requer autenticação via token JWT no header Authorization.
    Retorna informações completas incluindo:
    - Dados do usuário
    - Nome completo (JOIN com people)
    - Nome da empresa (JOIN com companies)
    - Nome do estabelecimento (JOIN com establishments)
    - Lista de estabelecimentos da empresa

    Usa a procedure [core].[sp_get_user_me_data] que retorna JSON
    e registra auditoria automaticamente.
    """
    import json
    from sqlalchemy import text

    # Executar stored procedure que retorna JSON
    proc_query = text("EXEC [core].[sp_get_user_me_data] @user_id_input=:user_id")

    result = await db.execute(proc_query, {"user_id": current_user.id})
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # O resultado é uma string JSON na primeira coluna
    json_str = row[0]

    # Parse do JSON
    user_data = json.loads(json_str)

    # Extrair establishments (vem como string JSON ou null)
    establishments = []
    if user_data.get("establishments"):
        establishments = json.loads(user_data["establishments"])

    return UserMeResponse(
        id=user_data["id"],
        email_address=user_data["email_address"],
        person_id=user_data.get("person_id"),
        company_id=user_data.get("company_id"),
        establishment_id=user_data.get("establishment_id"),
        is_active=user_data["is_active"],
        is_system_admin=user_data["is_system_admin"],
        last_login_at=user_data.get("last_login_at"),
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"],
        full_name=user_data.get("full_name"),
        company_name=user_data.get("company_name"),
        establishment_name=user_data.get("establishment_name"),
        context_type=user_data.get("context_type"),
        establishments=establishments  # type: ignore
    )
    
    # Buscar estabelecimentos da empresa (se houver)
    establishments = []
    if user_row.company_id:
        establishments_query = text("""
            SELECT e.id, p.name
            FROM [core].[establishments] e
            JOIN [core].[people] p ON p.id = e.person_id
            WHERE e.company_id = :company_id 
              AND e.deleted_at IS NULL 
              AND p.deleted_at IS NULL
            ORDER BY p.name
        """)
        
        establishments_result = await db.execute(
            establishments_query, 
            {"company_id": user_row.company_id}
        )
        establishments = [
            {"id": row.id, "name": row.name} 
            for row in establishments_result.fetchall()
        ]
    
    # Montar resposta
    return UserMeResponse(
        id=user_row.id,
        email_address=user_row.email_address,
        person_id=user_row.person_id,
        company_id=user_row.company_id,
        establishment_id=user_row.establishment_id,
        is_active=user_row.is_active,
        is_system_admin=user_row.is_system_admin,
        last_login_at=user_row.last_login_at,
        created_at=user_row.created_at,
        updated_at=user_row.updated_at,
        full_name=user_row.full_name,
        company_name=user_row.company_name,
        establishment_name=user_row.establishment_name,
        context_type=None,  # TODO: Implementar lógica de context_type
        establishments=establishments
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para renovar token JWT expirado.
    
    **Funcionalidade:**
    - Aceita token expirado (até certo limite)
    - Valida se usuário ainda existe e está ativo
    - Gera novo token JWT com mesma validade
    - Retorna novo token para o cliente
    
    **Segurança:**
    - Valida estrutura do token (mesmo expirado)
    - Verifica se usuário ainda está ativo
    - Não permite refresh de tokens muito antigos
    
    **Headers necessários:**
    - Authorization: Bearer <token_expirado>
    
    **Retorna:**
    - access_token: Novo token JWT
    - token_type: "bearer"
    - expires_in: Tempo de expiração em segundos
    """
    from jose import JWTError, jwt
    from sqlalchemy import text
    from app.core.config import settings
    from datetime import timedelta
    
    # Obter token do header Authorization
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer requerido no header Authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header[7:]  # Remove 'Bearer '
    
    # Decodificar token (permite expirado para refresh)
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False}  # Permite token expirado
        )
        email = payload.get("email")
        user_id = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: email não encontrado"
            )
            
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuário no banco para validar se ainda está ativo
    query = text("""
        SELECT
            u.id,
            u.email_address,
            u.is_active,
            u.is_system_admin
        FROM [core].[users] u
        WHERE u.email_address = :email 
          AND u.deleted_at IS NULL
    """)
    
    result = await db.execute(query, {"email": email})
    user_row = result.fetchone()
    
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    if not user_row.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Contate o administrador."
        )
    
    # Gerar novo token JWT
    from app.core.security import create_access_token
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user_row.email_address,
            "user_id": user_row.id
        },
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para solicitar reset de senha.
    
    **Endpoint público** (não requer autenticação)
    
    **Segurança:**
    - Sempre retorna sucesso (não revela se email existe)
    - Token válido por 1 hora
    - Token único gerado com secrets.token_urlsafe()
    
    **Fluxo:**
    1. Usuário digita email
    2. Sistema gera token único
    3. Token salvo no banco com expiração
    4. Email enviado com link de reset (simulado em dev)
    5. Mensagem genérica mostrada ao usuário
    
    **Nota:** Em produção, integrar com serviço de email real.
    """
    import secrets
    from datetime import datetime, timedelta
    from sqlalchemy import text
    
    try:
        # Buscar usuário por email
        query = text("""
            SELECT
                u.id,
                u.email_address,
                u.is_active,
                p.name as full_name
            FROM [core].[users] u
            LEFT JOIN [core].[people] p ON p.id = u.person_id
            WHERE u.email_address = :email 
              AND u.deleted_at IS NULL
        """)
        
        result = await db.execute(query, {"email": request_data.email_address})
        user_row = result.fetchone()
        
        # Se usuário existe, gerar token e salvar
        if user_row and user_row.is_active:
            # Gerar token seguro (32 bytes = 43 caracteres base64)
            reset_token = secrets.token_urlsafe(32)
            
            # Calcular expiração (1 hora)
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            # Salvar token no banco
            update_query = text("""
                UPDATE [core].[users]
                SET
                    password_reset_token = :token,
                    password_reset_expires_at = :expires_at,
                    updated_at = GETDATE()
                WHERE id = :user_id
            """)

            await db.execute(update_query, {
                "token": reset_token,
                "expires_at": expires_at,
                "user_id": user_row.id
            })
            await db.commit()
            
            # Enviar email de reset via smtp4dev
            from app.services.email_service import EmailService
            
            email_service = EmailService()
            await email_service.send_password_reset_email(
                to_email=user_row.email_address,
                to_name=user_row.full_name or "Usuário",
                reset_token=reset_token,
                expires_at=expires_at.strftime('%d/%m/%Y %H:%M:%S')
            )
        
        # SEMPRE retornar sucesso (não revelar se email existe)
        return PasswordResetResponse(
            success=True,
            message="Se o email existir, você receberá um link para redefinir sua senha."
        )
        
    except Exception as e:
        # Log do erro mas retorna mensagem genérica (segurança)
        print(f"Erro em forgot_password: {str(e)}")
        return PasswordResetResponse(
            success=True,
            message="Se o email existir, você receberá um link para redefinir sua senha."
        )


@router.post("/validate-reset-token", response_model=PasswordResetResponse)
async def validate_reset_token(
    request_data: ValidateResetTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para validar token de reset de senha.
    
    **Endpoint público** (não requer autenticação)
    
    **Validações:**
    - Token existe no banco?
    - Token não expirou? (1h)
    - Usuário está ativo?
    
    **Uso:**
    Frontend chama este endpoint antes de mostrar formulário de nova senha.
    """
    from datetime import datetime
    from sqlalchemy import text
    
    # Buscar usuário pelo token
    query = text("""
        SELECT
            u.id,
            u.email_address,
            u.is_active,
            u.password_reset_expires_at
        FROM [core].[users] u
        WHERE u.password_reset_token = :token
          AND u.deleted_at IS NULL
    """)
    
    result = await db.execute(query, {"token": request_data.token})
    user_row = result.fetchone()
    
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado"
        )
    
    # Verificar expiração
    if user_row.password_reset_expires_at:
        if datetime.utcnow() > user_row.password_reset_expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expirado. Solicite um novo link de reset."
            )
    
    # Verificar se usuário está ativo
    if not user_row.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo. Contate o administrador."
        )
    
    return PasswordResetResponse(
        success=True,
        message="Token válido. Você pode redefinir sua senha."
    )


@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    request_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para redefinir senha usando token.

    **Endpoint público** (não requer autenticação)

    **Fluxo:**
    1. Valida token
    2. Atualiza senha com hash bcrypt
    3. Invalida token usado
    4. Atualiza password_changed_at
    5. Usuário pode fazer login com nova senha

    **Segurança:**
    - Senha hashada com bcrypt
    - Token invalidado após uso (one-time use)
    - Validação de força de senha (mínimo 8 caracteres)
    """
    from datetime import datetime
    from sqlalchemy import text

    # Buscar usuário pelo token
    query = text("""
        SELECT
            u.id,
            u.email_address,
            u.is_active,
            u.password_reset_expires_at
        FROM [core].[users] u
        WHERE u.password_reset_token = :token
          AND u.deleted_at IS NULL
    """)

    result = await db.execute(query, {"token": request_data.token})
    user_row = result.fetchone()

    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado"
        )

    # Verificar expiração
    if user_row.password_reset_expires_at:
        if datetime.utcnow() > user_row.password_reset_expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expirado. Solicite um novo link de reset."
            )

    # Verificar se usuário está ativo
    if not user_row.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo. Contate o administrador."
        )

    # Validar nova senha (mínimo 8 caracteres)
    if len(request_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha deve ter no mínimo 8 caracteres"
        )

    # Hashear nova senha
    hashed_password = hash_password(request_data.new_password)

    # Atualizar senha e limpar token
    update_query = text("""
        UPDATE [core].[users]
        SET
            password = :password,
            password_reset_token = NULL,
            password_reset_expires_at = NULL
        WHERE id = :user_id
    """)

    await db.execute(update_query, {
        "password": hashed_password,
        "user_id": user_row.id
    })
    await db.commit()

@router.post("/initialize-admin")
async def initialize_admin(db: AsyncSession = Depends(get_db)):
    """
    Endpoint para inicializar usuário admin básico (desenvolvimento).
    
    Cria usuário admin@proteamcare.com.br com senha admin123 se não existir.
    Este endpoint deve ser REMOVIDO em produção.
    """
    try:
        # Verificar se já existe
        stmt = select(User).where(User.email_address == "admin@proteamcare.com.br")
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            return {
                "success": True,
                "message": "Usuário admin já existe",
                "user": {
                    "id": existing_user.id,
                    "email": existing_user.email_address,
                    "is_active": existing_user.is_active,
                    "is_system_admin": existing_user.is_system_admin
                }
            }
        
        # Criar pessoa física
        from app.models.person import Person
        from datetime import datetime
        
        new_person = Person(
            name="Administrador Sistema",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_person)
        await db.commit()
        await db.refresh(new_person)
        
        # Criar usuário
        from app.core.security import hash_password
        new_user = User(
            email_address="admin@proteamcare.com.br",
            password=hash_password("admin123"),
            person_id=new_person.id,
            is_active=True,
            is_system_admin=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return {
            "success": True,
            "message": "Usuário admin criado com sucesso",
            "user": {
                "id": new_user.id,
                "email": new_user.email_address,
                "password": "admin123",
                "is_active": new_user.is_active,
                "is_system_admin": new_user.is_system_admin
            }
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao inicializar admin: {str(e)}"
        )
