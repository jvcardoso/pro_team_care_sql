"""
Model de LoginLogs (histórico de tentativas de login).

Schema: [core] (banco: pro_team_care_logs)

⚠️ DATABASE FIRST: Este model apenas mapeia a tabela existente.
   A tabela foi criada manualmente no SQL Server no banco dedicado de logs.
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, Index
from app.core.database_logs import LogsBase


class LoginLog(LogsBase):
    """
    Model de log de tentativas de autenticação.

    Armazena histórico completo de todas as tentativas de login
    (bem-sucedidas ou não) para auditoria e segurança.

    Este model aponta para o banco SEPARADO: pro_team_care_logs
    """
    __tablename__ = "login_logs"
    __table_args__ = (
        # Índice para consultas por empresa e data
        Index(
            'idx_login_logs_company_date',
            'company_id', 'created_at'
        ),
        # Índice para consultas por email e status
        Index(
            'idx_login_logs_email_status',
            'email_attempted', 'status'
        ),
        # Índice para análise de IPs suspeitos
        Index(
            'idx_login_logs_ip_date',
            'ip_address', 'created_at'
        ),
        {"schema": "core"}
    )

    # Chave primária
    id = Column(
        BigInteger,
        primary_key=True,
        comment="ID único do log"
    )

    # Relacionamento lógico (sem FK para desacoplamento)
    company_id = Column(
        BigInteger,
        nullable=True,
        comment="ID da empresa (NULL se email não encontrado)"
    )

    user_id = Column(
        BigInteger,
        nullable=True,
        comment="ID do usuário (NULL se email não encontrado)"
    )

    # Dados da tentativa
    email_attempted = Column(
        String(255),
        nullable=False,
        comment="Email usado na tentativa de login"
    )

    ip_address = Column(
        String(45),
        nullable=True,
        comment="Endereço IP de origem (IPv4 ou IPv6)"
    )

    user_agent = Column(
        String(1024),
        nullable=True,
        comment="User-Agent do navegador/cliente"
    )

    # Resultado
    status = Column(
        String(20),
        nullable=False,
        comment="Status: SUCCESS, FAILED, INACTIVE_USER_ATTEMPT"
    )

    failure_reason = Column(
        String(255),
        nullable=True,
        comment="Motivo da falha (INVALID_CREDENTIALS, USER_INACTIVE, etc)"
    )

    session_id = Column(
        String(255),
        nullable=True,
        comment="ID da sessão (se login bem-sucedido)"
    )

    # Timestamp
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Data/hora da tentativa de login"
    )

    def __repr__(self):
        return f"<LoginLog {self.email_attempted} - {self.status} @ {self.created_at}>"
