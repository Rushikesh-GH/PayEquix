from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.system import router as system_router
from app.api.master_data import router as master_data_router
from app.api.compensation import router as compensation_router
from app.api.exceptions import router as exceptions_router
from app.api.proposals import router as proposals_router
from app.api.audit import router as audit_router
from app.api.comparable_groups import router as groups_router
from app.api.data_admin import router as data_admin_router
from app.api.ai_agents import router as ai_agents_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(system_router)
api_router.include_router(master_data_router)
api_router.include_router(compensation_router)
api_router.include_router(exceptions_router)
api_router.include_router(proposals_router)
api_router.include_router(audit_router)
api_router.include_router(groups_router)
api_router.include_router(data_admin_router)
api_router.include_router(ai_agents_router)
