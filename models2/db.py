from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select


from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID, uuid4


# models
class EmbeddingX(BaseModel):
    id: int
    data: Dict

# from dataclass import dataclass

# @dataclass
#   class Product:
#     name: str
#     price: float
#     quantity: int = 0

#    def totalCost(self) -> float:
# 	return self.price * self.quantityS


# database setup
DATABASE_URL = "sqlite+aiosqlite:///./data/embeddings-mostly-fastapi.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
)


async def dbInit():
    async with engine.begin() as conn:
        # from models import Base  
        # Ensure models have shared base class
        if False:
            await conn.run_sync(EmbeddingX.metadata.create_all)


async def dbGet():
    async with async_session() as session:
        yield session



