from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Четыре слэша после sqlite+aiosqlite: — это корень / контейнера
DATABASE_URL = "sqlite+aiosqlite:////app/data/booking.db"




engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
