"""
Service de Autenticação (v2.0 - Refatorado).

Lógica de autenticação usando stored procedures de suporte:
- sp_get_user_for_auth: Busca dados do usuário
- sp_log_login_success: Atualiza last_login_at e registra sucesso
- sp_log_login_failure: Registra falhas de login

A validação de senha bcrypt agora ocorre em Python.
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.security import create_access_token, verify_password
from app.core.config import settings


class AuthService:
    """Service de autenticação (v2.0)"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_login(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executa login com validação bcrypt em Python.

        Fluxo:
        1. Busca usuário via sp_get_user_for_auth
        2. Valida senha com bcrypt em Python
        3. Se sucesso: chama sp_log_login_success e retorna token
        4. Se falha: chama sp_log_login_failure e retorna erro

        Args:
            email: Email do usuário
            password: Senha em texto plano
            ip_address: IP de origem da requisição
            user_agent: User-Agent do cliente

        Returns:
            Dict com:
                - success: bool
                - message: str
                - access_token: str (se success=True)
                - token_type: str (se success=True)
                - user_id: int (se success=True)
                - company_id: int (se success=True)
        """
        ip = ip_address or "unknown"
        ua = user_agent or "unknown"

        # 1. Buscar dados do usuário
        user_data = await self._get_user_for_auth(email)

        # 2. Verificar se usuário existe
        if not user_data:
            # Email não encontrado
            await self._log_login_failure(
                user_id=None,
                company_id=None,
                email=email,
                ip_address=ip,
                user_agent=ua,
                failure_reason="INVALID_CREDENTIALS"
            )
            return {
                "success": False,
                "message": "Email ou senha inválidos"
            }

        # 3. Verificar se usuário está ativo
        if not user_data["is_active"]:
            # Usuário inativo
            await self._log_login_failure(
                user_id=user_data["user_id"],
                company_id=user_data["company_id"],
                email=email,
                ip_address=ip,
                user_agent=ua,
                failure_reason="USER_INACTIVE"
            )
            return {
                "success": False,
                "message": "Este usuário está inativo e não pode fazer login"
            }

        # 4. Validar senha com bcrypt (via passlib)
        password_match = verify_password(password, user_data["password_hash"])

        if not password_match:
            # Senha incorreta
            await self._log_login_failure(
                user_id=user_data["user_id"],
                company_id=user_data["company_id"],
                email=email,
                ip_address=ip,
                user_agent=ua,
                failure_reason="INVALID_CREDENTIALS"
            )
            return {
                "success": False,
                "message": "Email ou senha inválidos"
            }

        # 5. Login bem-sucedido: registrar sucesso e gerar token
        await self._log_login_success(
            user_id=user_data["user_id"],
            ip_address=ip,
            user_agent=ua
        )

        # Gerar token JWT
        access_token = create_access_token(
            data={
                "sub": str(user_data["user_id"]),
                "company_id": user_data["company_id"],
                "email": email
            }
        )

        return {
            "success": True,
            "message": "Login realizado com sucesso",
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_data["user_id"],
            "company_id": user_data["company_id"]
        }

    async def _get_user_for_auth(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Busca dados do usuário para autenticação.
        Chama sp_get_user_for_auth.
        """
        query = text("""
            EXEC [core].[sp_get_user_for_auth]
                @email_attempted = :email
        """)

        result = await self.db.execute(query, {"email": email})
        row = result.fetchone()

        if not row:
            return None

        return {
            "user_id": row.id,
            "company_id": row.company_id,
            "password_hash": row.stored_password_hash,
            "is_active": row.is_active
        }

    async def _log_login_success(
        self,
        user_id: int,
        ip_address: str,
        user_agent: str
    ) -> None:
        """
        Registra sucesso de login.
        Chama sp_log_login_success.
        """
        query = text("""
            EXEC [core].[sp_log_login_success]
                @user_id = :user_id,
                @ip_address = :ip_address,
                @user_agent = :user_agent
        """)

        await self.db.execute(
            query,
            {
                "user_id": user_id,
                "ip_address": ip_address,
                "user_agent": user_agent
            }
        )
        await self.db.commit()

    async def _log_login_failure(
        self,
        user_id: Optional[int],
        company_id: Optional[int],
        email: str,
        ip_address: str,
        user_agent: str,
        failure_reason: str
    ) -> None:
        """
        Registra falha de login.
        Chama sp_log_login_failure.
        """
        query = text("""
            EXEC [core].[sp_log_login_failure]
                @user_id = :user_id,
                @company_id = :company_id,
                @email_attempted = :email,
                @ip_address = :ip_address,
                @user_agent = :user_agent,
                @failure_reason = :failure_reason
        """)

        await self.db.execute(
            query,
            {
                "user_id": user_id,
                "company_id": company_id,
                "email": email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "failure_reason": failure_reason
            }
        )
        await self.db.commit()
