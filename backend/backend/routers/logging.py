from backend.auth import check_access, get_current_identifier
from backend.db import get_db
from backend.reduce_size import reduce_size
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from backend.models import *
from backend.const import EPS

logging_router = APIRouter()


@logging_router.get("/after/{id}")
async def get_logging_after(
    id: int,
    after: float,
    db: Session = Depends(get_db),
    identifier: str = Depends(get_current_identifier),
):
    if not check_access(
        db.query(FinetuneEntry).filter(FinetuneEntry.id == id), identifier
    ):
        return None
    return (
        db.query(FtLoggingRecord)
        .filter(FtLoggingRecord.entry_id == id)
        .filter(FtLoggingRecord.step > after)
        .order_by(FtLoggingRecord.step)
        .all()
    )


@logging_router.get("/{id}")
async def get_logging(
    id: int,
    db: Session = Depends(get_db),
    identifier: str = Depends(get_current_identifier),
):
    if not check_access(
        db.query(FinetuneEntry).filter(FinetuneEntry.id == id), identifier
    ):
        return None
    return reduce_size(
        db.query(FtLoggingRecord).filter(FtLoggingRecord.entry_id == id).all()
    )


@logging_router.get("/eval/{id}")
async def get_eval(
    id: int,
    db: Session = Depends(get_db),
    identifier: str = Depends(get_current_identifier),
):
    if not check_access(
        db.query(FinetuneEntry).filter(FinetuneEntry.id == id), identifier
    ):
        return None
    return reduce_size(
        db.query(FtEvalLossRecord).filter(FtEvalLossRecord.entry_id == id).all()
    )


@logging_router.get("/eval/after/{id}")
async def get_eval_after(
    id: int,
    after: float,
    db: Session = Depends(get_db),
    identifier: str = Depends(get_current_identifier),
):
    if not check_access(
        db.query(FinetuneEntry).filter(FinetuneEntry.id == id), identifier
    ):
        return None
    return (
        db.query(FtEvalLossRecord)
        .filter(FtEvalLossRecord.entry_id == id)
        .filter(FtEvalLossRecord.epoch - after > EPS)
        .all()
    )
