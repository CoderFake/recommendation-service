from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.api.endpoints import recommendations, health
from app.core.config import settings
from app.db.session import init_db
from app.services.data_sync_service import start_sync_scheduler
from app.api.openapi_description import API_DESCRIPTION, API_TAGS_METADATA

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=API_DESCRIPTION,
    version="1.0.0",
    docs_url=None,  # Tắt docs mặc định để sử dụng custom docs
    redoc_url=None,
    openapi_tags=API_TAGS_METADATA
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router
app.include_router(recommendations.router, prefix="/api")
app.include_router(health.router, prefix="/api")


# Tạo endpoint custom cho API docs
@app.get("/api/docs", include_in_schema=False)
async def get_documentation():
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title="API Documentation")


@app.get("/api/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description=API_DESCRIPTION,
        routes=app.routes,
        tags=API_TAGS_METADATA
    )


@app.on_event("startup")
async def startup_event():
    # Khởi tạo kết nối database
    await init_db()

    # Khởi chạy scheduler đồng bộ dữ liệu
    start_sync_scheduler()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)