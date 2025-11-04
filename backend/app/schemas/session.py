"""
Schemas Pydantic para Sessões de Usuário.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================================
# SCHEMAS BASE
# ============================================================================

class UserSessionBase(BaseModel):
    """Schema base para sessões de usuário"""
    user_id: int
    jti: str = Field(..., description="JWT ID único do token")
    impersonator_user_id: Optional[int] = Field(None, description="ID do admin personificando")
    expires_at: datetime


class UserSessionCreate(UserSessionBase):
    """Schema para criar sessão"""
    pass


class UserSessionResponse(UserSessionBase):
    """Schema de resposta de sessão"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS DE PERSONIFICAÇÃO
# ============================================================================

class ImpersonateRequest(BaseModel):
    """Schema para solicitar personificação"""
    target_user_id: int = Field(..., description="ID do usuário a ser personificado")


class ImpersonateResponse(BaseModel):
    """Schema de resposta de personificação"""
    access_token: str
    token_type: str = "bearer"
    impersonating: bool = True
    target_user_id: int
    target_user_email: str
    impersonator_id: int
    impersonator_email: str


class EndImpersonationResponse(BaseModel):
    """Schema de resposta ao encerrar personificação"""
    access_token: str
    token_type: str = "bearer"
    impersonating: bool = False
    user_id: int
    user_email: str


# ============================================================================
# SCHEMAS DE SWITCH PROFILE
# ============================================================================

class SwitchProfileRequest(BaseModel):
    """Schema para trocar perfil/contexto"""
    company_id: Optional[int] = Field(None, description="ID da empresa")
    establishment_id: Optional[int] = Field(None, description="ID do estabelecimento")
    role_id: Optional[int] = Field(None, description="ID do role")


class SwitchProfileResponse(BaseModel):
    """Schema de resposta ao trocar perfil"""
    access_token: str
    token_type: str = "bearer"
    active_company_id: Optional[int]
    active_establishment_id: Optional[int]
    active_role_id: Optional[int]
    message: str = "Perfil alterado com sucesso"


# ============================================================================
# SCHEMAS DE LISTAGEM
# ============================================================================

class ActiveSessionResponse(BaseModel):
    """Schema para listar sessões ativas"""
    id: int
    user_id: int
    jti: str
    is_impersonating: bool
    impersonator_user_id: Optional[int]
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

    @property
    def is_expired(self) -> bool:
        """Verifica se a sessão está expirada"""
        return datetime.utcnow() > self.expires_at
