"""
Main API router — aggregates all v1 sub-routers.
"""

from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.cases.router import router as cases_router
from app.api.v1.persons.router import router as persons_router
from app.api.v1.analytics.router import router as analytics_router
from app.api.v1.graph.router import router as graph_router
from app.api.v1.ai.router import router as ai_router
from app.api.v1.search.router import router as search_router
from app.api.v1.media.router import router as media_router
from app.api.v1.audit.router import router as audit_router
from app.api.v1.tasks.router import router as tasks_router
from app.api.v1.evidence.router import router as evidence_router
from app.api.v1.demo import router as demo_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(cases_router, prefix="/cases", tags=["Cases"])
api_router.include_router(persons_router, prefix="/persons", tags=["Persons"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(graph_router, prefix="/graph", tags=["Graph Intelligence"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI Services"])
api_router.include_router(search_router, prefix="/search", tags=["Global Search"])
api_router.include_router(media_router, prefix="/media", tags=["Media"])
api_router.include_router(audit_router, prefix="/audit", tags=["Audit Trail"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["Investigation Tasks"])
api_router.include_router(evidence_router, prefix="/evidence", tags=["Evidence Chain of Custody"])
api_router.include_router(demo_router, prefix="/demo", tags=["Demo Mode"])
