from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event
from sqlalchemy.exc import DisconnectionError, OperationalError
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:pwd@db:5432/GONGBU"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_size=1256, max_overflow=1128, pool_recycle=300
)
SessionLocal = sessionmaker(bind=engine)


def gen_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db():
    return next(gen_db())
