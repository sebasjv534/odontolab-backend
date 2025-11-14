from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Convertimos la URL de POSTGRESQL para usar asyncpg
def get_database_url():
    url = settings.DATABASE_URL
    if url.startswith("postgresql://"):
        # Cambiar a postgresql+asyncpg:// para usar asyncpg driver
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

DATABASE_URL = get_database_url()

# Configuración optimizada para Render free tier
# - pool_size: Número de conexiones permanentes (2 para free tier)
# - max_overflow: Conexiones adicionales permitidas (0 para free tier)
# - pool_pre_ping: Verifica conexiones antes de usar
# - pool_recycle: Recicla conexiones cada hora para evitar timeouts
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=2,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "timeout": 30,
        "command_timeout": 30,
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session