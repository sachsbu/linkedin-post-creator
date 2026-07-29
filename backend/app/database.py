from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings
from app.models.db_models import Base

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("ALTER TABLE posts ADD COLUMN platform VARCHAR DEFAULT 'linkedin'"))
        except Exception:
            pass  # Column already exists

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

