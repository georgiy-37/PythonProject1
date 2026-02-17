from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Для PostgreSQL здесь будет: "postgresql+asyncpg://user:pass@localhost/dbname"
DATABASE_URL = "sqlite+aiosqlite:///./data/booking.db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
