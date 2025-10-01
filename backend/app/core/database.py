
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.settings import Settings
import asyncio


DATABASE_URL = Settings().DATABASE_URL


Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)

session_factory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
SessionLocal = async_scoped_session(session_factory, scopefunc=asyncio.current_task)


async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
