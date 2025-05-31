from fastapi import APIRouter
from .query import router as query_router
from .auth import router as auth_router

router = APIRouter()

# Include all API routes
router.include_router(query_router, prefix="/query", tags=["Query"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
