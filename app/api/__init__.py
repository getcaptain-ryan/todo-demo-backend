from fastapi import APIRouter
from app.api import todos, users, columns, tasks

# Create the main API router with /api prefix
api_router = APIRouter(prefix="/api")

# Include all resource routers
api_router.include_router(todos.router)
api_router.include_router(users.router)
api_router.include_router(columns.router)
api_router.include_router(tasks.router)
