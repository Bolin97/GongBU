from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event
from sqlalchemy.exc import DisconnectionError, OperationalError
import os

SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_size=128, max_overflow=128, pool_recycle=3600
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
