from backend.db import get_db
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from backend.models import *
from backend.const import EPS

logging_router = APIRouter()


@logging_router.get("/after/{id}")
async def get_logging_after(id: int, after: float, db: Session = Depends(get_db)):
    return (
        db.query(LoggingRecord)
        .filter(LoggingRecord.entry_id == id)
        .filter(LoggingRecord.step > after)
        .order_by(LoggingRecord.step)
        .all()
    )


@logging_router.get("/{id}")
async def get_logging(id: int, db: Session = Depends(get_db)):
    return db.query(LoggingRecord).filter(LoggingRecord.entry_id == id).all()


@logging_router.get("/eval/{id}")
async def get_eval(id: int, db: Session = Depends(get_db)):
    return db.query(EvalRecord).filter(EvalRecord.entry_id == id).all()


@logging_router.get("/eval/after/{id}")
async def get_eval_after(id: int, after: float, db: Session = Depends(get_db)):
    return (
        db.query(EvalRecord)
        .filter(EvalRecord.entry_id == id)
        .filter(EvalRecord.epoch - after > EPS)
        .all()
    )
