"""
Funções de segurança: hash de senhas e JWT.
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from .config import settings

# ========================================
# HASH DE SENHAS (bcrypt)
# ========================================
# Usando configuração mais simples para evitar problemas de inicialização
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Gera hash bcrypt de uma senha"""
    # Truncar senha se for maior que 72 bytes (limitação do bcrypt)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se senha bate com hash"""
    try:
        # Truncar senha se for maior que 72 bytes (limitação do bcrypt)
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            plain_password = password_bytes[:72].decode('utf-8', errors='ignore')

        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Fallback: usar bcrypt diretamente se passlib falhar
        import bcrypt
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except:
            return False


# ========================================
# JWT TOKENS
# ========================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria JWT token.

    Args:
        data: Dados a codificar no token (ex: {"sub": "user@email.com"})
        expires_delta: Tempo de expiração customizado

    Returns:
        Token JWT assinado
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica e valida JWT token.

    Args:
        token: Token JWT

    Returns:
        Payload do token ou None se inválido
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
