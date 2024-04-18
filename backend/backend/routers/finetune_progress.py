from backend.auth import check_access, get_current_identifier
from backend.db import gen_db
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from backend.models import *

finetune_progress_router = APIRouter()


@finetune_progress_router.get("/{id}")
async def prog(
    id: int,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    if not check_access(
        db.query(FinetuneEntry).filter(FinetuneEntry.id == id), identifier
    ):
        return None
    return db.query(FinetuneProgress).filter(FinetuneProgress.id == id).first()
