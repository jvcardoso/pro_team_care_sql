"""
Schemas Pydantic para Password Reset.
"""
from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    """Request para solicitar reset de senha"""
    email_address: EmailStr = Field(..., description="Email do usuário")


class ValidateResetTokenRequest(BaseModel):
    """Request para validar token de reset"""
    token: str = Field(..., min_length=32, description="Token de reset recebido por email")


class ResetPasswordRequest(BaseModel):
    """Request para redefinir senha"""
    token: str = Field(..., min_length=32, description="Token de reset")
    new_password: str = Field(..., min_length=8, description="Nova senha (mínimo 8 caracteres)")


class PasswordResetResponse(BaseModel):
    """Response genérica para operações de password reset"""
    success: bool
    message: str
