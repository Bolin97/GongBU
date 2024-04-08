from backend.auth import accessible, get_current_identifier
from fastapi import APIRouter
from datetime import date
from backend.db import gen_db
from backend.models import Pool, DatasetEntry
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session

dataset_entry_router = APIRouter()


@dataset_entry_router.get("/by_pool/{pool_id}")
async def by_pool(pool_id: int, db: Session = Depends(gen_db), identifier: str = Depends(get_current_identifier)):
    try:
        return accessible(db.query(DatasetEntry).filter(DatasetEntry.pool_id == pool_id), identifier).all()
    except:
        return []

@dataset_entry_router.get("/{dataset_entry_id}")
async def by_id(dataset_entry_id: int, db: Session = Depends(gen_db), identifier: str = Depends(get_current_identifier)):
    return accessible(db.query(DatasetEntry), identifier).filter(DatasetEntry.id == dataset_entry_id).first()
