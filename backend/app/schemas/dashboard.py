"""
Schemas Pydantic para Dashboard.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# SCHEMAS DE ESTATÍSTICAS
# ============================================================================

class EntityStats(BaseModel):
    """Schema para estatísticas de uma entidade"""
    total: int = Field(..., description="Total de registros")
    active: int = Field(..., description="Registros ativos")
    inactive: int = Field(..., description="Registros inativos")


class DashboardStats(BaseModel):
    """Schema de estatísticas gerais do dashboard"""
    users: EntityStats
    companies: EntityStats
    establishments: EntityStats
    roles: Dict[str, int] = Field(..., description="Contagem de roles")
    notifications: Dict[str, int] = Field(..., description="Estatísticas de notificações")
    sessions: Dict[str, int] = Field(..., description="Sessões ativas")


class StatsResponse(BaseModel):
    """Schema de resposta de estatísticas"""
    stats: DashboardStats
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int
    user_context: Optional[str] = None


# ============================================================================
# SCHEMAS DE ATIVIDADE RECENTE
# ============================================================================

class ActivityLog(BaseModel):
    """Schema de log de atividade"""
    id: int
    user_id: int
    user_name: str
    user_email: str
    action: str = Field(..., description="Ação realizada (created, updated, deleted)")
    resource: str = Field(..., description="Recurso afetado (user, company, etc)")
    resource_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecentActivityResponse(BaseModel):
    """Schema de resposta de atividade recente"""
    activities: List[ActivityLog]
    total: int
    page: int = 1
    page_size: int = 10


# ============================================================================
# SCHEMAS DE LOGIN LOGS
# ============================================================================

class LoginLog(BaseModel):
    """Schema de log de login"""
    id: int
    user_id: int
    email_address: str
    login_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    success: bool = True

    class Config:
        from_attributes = True


class RecentLoginsResponse(BaseModel):
    """Schema de resposta de logins recentes"""
    logins: List[LoginLog]
    total: int
    page: int = 1
    page_size: int = 10


# ============================================================================
# SCHEMAS DE GRÁFICOS
# ============================================================================

class ChartDataPoint(BaseModel):
    """Schema de ponto de dados para gráfico"""
    label: str
    value: int
    date: Optional[datetime] = None


class ChartData(BaseModel):
    """Schema de dados de gráfico"""
    title: str
    type: str = Field(..., description="Tipo de gráfico (line, bar, pie, etc)")
    data: List[ChartDataPoint]


class DashboardChartsResponse(BaseModel):
    """Schema de resposta de gráficos do dashboard"""
    charts: List[ChartData]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# SCHEMAS DE RESUMO
# ============================================================================

class QuickStat(BaseModel):
    """Schema de estatística rápida"""
    label: str
    value: int
    icon: Optional[str] = None
    color: Optional[str] = None
    trend: Optional[str] = Field(None, description="up, down, stable")
    change_percentage: Optional[float] = None


class DashboardSummary(BaseModel):
    """Schema de resumo do dashboard"""
    quick_stats: List[QuickStat]
    recent_activities: List[ActivityLog]
    recent_logins: List[LoginLog]
    notifications_unread: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# SCHEMAS DE FILTROS
# ============================================================================

class DashboardFilters(BaseModel):
    """Schema de filtros para dashboard"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    company_id: Optional[int] = None
    establishment_id: Optional[int] = None
    user_id: Optional[int] = None


class FilteredStatsRequest(BaseModel):
    """Schema de requisição de estatísticas filtradas"""
    filters: DashboardFilters
    include_charts: bool = Field(False, description="Incluir dados de gráficos")
    include_activities: bool = Field(True, description="Incluir atividades recentes")
