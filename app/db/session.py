from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import logger

# Tạo engine kết nối đến database
engine = create_async_engine(
    settings.RECO_DB_URI,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=15,
    pool_timeout=30,
    pool_recycle=1800,
)

# Tạo session factory
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@asynccontextmanager
async def get_session():
    """
    Context manager để tạo và quản lý database session.
    """
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        await session.close()


async def init_db():
    """
    Khởi tạo cấu trúc database khi ứng dụng khởi động.
    """
    try:
        # Import để sử dụng Base
        from app.db.models import Base

        async with engine.begin() as conn:
            # Chỉ tạo bảng nếu chúng chưa tồn tại
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise