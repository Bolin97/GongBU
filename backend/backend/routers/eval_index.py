from backend.db import gen_db
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from backend.models import *
from backend.const import EPS

eval_index_router = APIRouter()


@eval_index_router.get("")
async def eval_index_get(id: int, ind: str, db: Session = Depends(gen_db)):
    return (
        db.query(EvalIndexRecord)
        .filter(EvalIndexRecord.entry_id == id)
        .filter(EvalIndexRecord.name == ind)
        .all()
    )


@eval_index_router.get("/after")
async def eval_index_get_after(
    id: int, ind: str, after: float, db: Session = Depends(gen_db)
):
    return (
        db.query(EvalIndexRecord)
        .filter(EvalIndexRecord.entry_id == id)
        .filter(EvalIndexRecord.name == ind)
        .filter(EvalIndexRecord.epoch - after > EPS)
        .all()
    )
