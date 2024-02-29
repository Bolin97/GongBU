from backend.db import gen_db
from fastapi import APIRouter, UploadFile
from backend.dao import submit_finetune_dataset
from fastapi.params import Depends
from sqlalchemy.orm import Session
from backend.models import *
from pydantic import BaseModel
from threading import Thread

dataset_router = APIRouter()


@dataset_router.post("/")
async def upload_finetune(name: str, description: str, pool_id: str, kind: int, file: UploadFile):
    #submit_finetune_dataset(pool_id, name, description, kind, file.file)
    th = Thread(target=submit_finetune_dataset, args=(pool_id, name, description, kind, file.file))
    th.start()


@dataset_router.delete("/{id}")
async def remove(id: int, db: Session = Depends(gen_db)):
    entry = db.query(DatasetEntry).filter(DatasetEntry.id == id).first()
    pool = db.query(Pool).filter(Pool.id == entry.pool_id).first()
    pool.size -= 1
    db.delete(entry)
    db.commit()
    db.close()
