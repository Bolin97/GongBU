from backend.db import gen_db
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from backend.models import *
from backend.const import EPS

ft_eval_index_router = APIRouter()


@ft_eval_index_router.get("")
async def eval_index_get(id: int, ind: str, db: Session = Depends(gen_db)):
    return (
        db.query(FtEvalIndexRecord)
        .filter(FtEvalIndexRecord.entry_id == id)
        .filter(FtEvalIndexRecord.name == ind)
        .all()
    )


@ft_eval_index_router.get("/after")
async def eval_index_get_after(
    id: int, ind: str, after: float, db: Session = Depends(gen_db)
):
    return (
        db.query(FtEvalIndexRecord)
        .filter(FtEvalIndexRecord.entry_id == id)
        .filter(FtEvalIndexRecord.name == ind)
        .filter(FtEvalIndexRecord.epoch - after > EPS)
        .all()
    )
