from fastapi import APIRouter, HTTPException

from backend.db import gen_db, get_db

from backend.models import *
from fastapi.params import Depends
from sqlalchemy.orm import Session
from backend.service.sift import kmeans_sift
from backend.service.dataset import submit_finetune_dataset

from backend.auth import accessible, get_current_identifier
from threading import Thread

dataset_sift_router = APIRouter()

@dataset_sift_router.post("/kmeans")
async def kmeans_sift_router(
    pool_id: int,
    name: str,
    description: str,
    source_entry_id: int,
    reduce_to_percentage: float,
    db: Session = Depends(get_db),
    identifier: str = Depends(get_current_identifier),
):
    # if not accessible(
    #     db.query(DatasetEntry).filter(DatasetEntry.id == source_entry_id).first(),
    #     identifier,
    # ):
    #     raise HTTPException(status_code=403, detail="Forbidden")
    def work():
        db = get_db()
        kind = db.query(DatasetEntry).filter(DatasetEntry.id == source_entry_id).first().type
        db.close()
        sifted = kmeans_sift(kind, source_entry_id, reduce_to_percentage)
        submit_finetune_dataset(
            pool_id,
            name,
            description,
            kind,
            sifted,
            identifier,
        )
    th = Thread(target=work)
    th.start()