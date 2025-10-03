import uvicorn
from app.core.database import Base, engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
