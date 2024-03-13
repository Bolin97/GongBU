from backend.db import gen_db
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from backend.models import *

finetune_progress_router = APIRouter()


@finetune_progress_router.get("/{id}")
async def prog(id: int, db: Session = Depends(gen_db)):
    return db.query(FinetuneProgress).filter(FinetuneProgress.id == id).first()
