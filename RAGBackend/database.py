from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base,Session
from typing import Generator

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:050501@localhost:3306/rag_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
