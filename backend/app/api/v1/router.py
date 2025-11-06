"""
Router principal da API v1.
Agrupa todos os routers de endpoints.
"""
from fastapi import APIRouter
from . import (
    auth, users, companies, phones, emails, addresses,
    pf_profiles, pj_profiles, establishments, people, roles,
    dashboard, notifications, menus, secure_sessions, lgpd, external,
    activities, pendencies, uploads, kanban, uploads_kanban
)

# Import image analysis router
try:
    from .endpoints.image_analysis import router as image_analysis_router
except ImportError as e:
    print(f"Warning: Could not import image analysis router: {e}")
    image_analysis_router = None
# from .endpoints.image_analysis import router as image_analysis_router  # Temporariamente desabilitado

api_router = APIRouter()

# Incluir routers - Fase 1
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(companies.router)
api_router.include_router(phones.router)
api_router.include_router(emails.router)
api_router.include_router(addresses.router)
api_router.include_router(pf_profiles.router)
api_router.include_router(pj_profiles.router)
api_router.include_router(establishments.router)
api_router.include_router(people.router)

# Incluir routers - Fase 2
api_router.include_router(dashboard.router)
api_router.include_router(notifications.router)
api_router.include_router(menus.router)
api_router.include_router(secure_sessions.router)

# Incluir routers - LGPD
api_router.include_router(lgpd.router)

# Incluir routers - Serviços Externos
api_router.include_router(external.router)

# Incluir routers - Módulo de Atividades (IA)
api_router.include_router(activities.router)
api_router.include_router(pendencies.router)

# Incluir routers - Kanban Board (Novo Modelo)
api_router.include_router(kanban.router)
api_router.include_router(uploads_kanban.router)

# Incluir routers - Uploads
api_router.include_router(uploads.router)

# Incluir routers - IA (Image Analysis)
try:
    from app.api.v1.endpoints.image_analysis import router as image_analysis_router
    api_router.include_router(image_analysis_router, prefix="/image-analysis", tags=["image-analysis"])
    print("✅ Image analysis router loaded")
except ImportError as e:
    print(f"⚠️ Image analysis router not loaded: {e}")
    pass
