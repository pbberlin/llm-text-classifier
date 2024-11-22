from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func, desc
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.inspection import inspect


from datetime import datetime as datetimeFunc

import  lib.config          as cfg

# database setup

# aiosqlite caused trouble
DATABASE_URL = "sqlite+aiosqlite:..."

DATABASE_URL = "sqlite:///./data/db-fastapi.db"


# Base = declarative_base()
from models.db0_base import Base




engine = create_engine(
    DATABASE_URL,
    # echo=True,
    connect_args={"check_same_thread": False},
)
print(f"\tdb engine created")
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    # class_=AsyncSession,
    # expire_on_commit=False,
)
print(f"\tdb session local created")





if False:
    # moved into init_db()
    Base.metadata.create_all(bind=engine)
    print(f"\tdb create all stop")


# funcs to integrate db management with fastapi
#   @asynccontextmanager
#   async def lifespan(app: FastAPI):
#       ...
async def init_db():
    Base.metadata.create_all(bind=engine)
    print(f"\tdb create all stop")


async def dispose_db():
    engine.dispose()


# get a DB session for endpoints
# 
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



from fastapi import HTTPException, Depends

# create all - if one does not exist
def ifNotExistTable(tableName, db: Session = Depends(get_db)):
    inspector = inspect(engine)
    # if Embedding.__tablename__ not in inspector.get_table_names():
    if tableName not in inspector.get_table_names():
        Base.metadata.create_all(bind=engine)
        return {"message": f"Tables '{inspector.get_table_names()}' created"}
    return {"message": f"table '{tableName}' already exists"}



## -----------------------------------
# end of general db stuff






