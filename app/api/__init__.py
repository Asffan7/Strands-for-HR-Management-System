from fastapi import APIRouter

from app.api.agent_apis import router as agent_router
from app.api.leave_apis import router as leave_router

api_router = APIRouter()
api_router.include_router(leave_router)
api_router.include_router(agent_router)
