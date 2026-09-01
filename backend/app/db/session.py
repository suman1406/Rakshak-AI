from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from ..core.config import settings

# Engine configuration
connect_args = {}

# Handle NeonDB SSL properly - asyncpg doesn't handle sslmode in URL query string
database_url = settings.DATABASE_URL

if database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
elif "postgresql+" in database_url and "sslmode" in database_url:
    # For NeonDB, parse and handle SSL separately
    from urllib.parse import urlparse, parse_qs
    
    # Extract sslmode from query string
    parsed = urlparse(database_url)
    query_params = parse_qs(parsed.query)
    
    sslmode = query_params.get("sslmode", ["require"])[0]
    
    # Rebuild URL without query string for asyncpg
    # Replace postgresql+asyncpg:// with postgresql+asyncpg:// (keep as-is, just remove query)
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    # Set SSL based on sslmode
    if sslmode == "require":
        connect_args["ssl"] = True
    elif sslmode == "prefer":
        connect_args["ssl"] = "prefer"
    else:
        connect_args["ssl"] = False
    
    database_url = clean_url
    print(f"Using SSL mode: {sslmode} for database connection")

engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
