"""
Schemas de autenticação (Login, Token).
"""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    email_address: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema para resposta de token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema para payload do token JWT"""
    sub: str  # Subject (email_address do usuário)
    exp: int  # Expiration time
