from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict

from app.api.endpoints import auth, songs, interactions, recommendations
from app.core.config import settings
from app.core.openapi import custom_openapi
from app.core.security import FirebaseError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

docs_url = f"{settings.API_V1_STR}/docs" if settings.ENABLE_DOCS else None
redoc_url = f"{settings.API_V1_STR}/redoc" if settings.ENABLE_DOCS else None
openapi_url = f"{settings.API_V1_STR}/openapi.json" if settings.ENABLE_DOCS else None

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=openapi_url,
    docs_url=docs_url,
    redoc_url=redoc_url,
)

logger.info(f"Running in {settings.ENVIRONMENT} environment")
logger.info(f"API documentation is {'enabled' if settings.ENABLE_DOCS else 'disabled'}")

if settings.ENABLE_DOCS:
    app.openapi = lambda: custom_openapi(app)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# API Router
api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(songs.router, prefix="/songs", tags=["songs"])
api_router.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(FirebaseError)
async def firebase_exception_handler(request: Request, exc: FirebaseError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": f"{exc.code}: {exc.message}"},
    )


@app.get("/healthcheck", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["root"])
async def root() -> Dict[str, str]:
    response = {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "environment": settings.ENVIRONMENT,
    }

    if settings.ENABLE_DOCS:
        response["docs"] = f"{settings.API_V1_STR}/docs"

    return response