from backend.db import gen_db
from fastapi import APIRouter, UploadFile
from backend.dao import submit_finetune_dataset
from fastapi.params import Depends
from sqlalchemy.orm import Session
from backend.models import *
from pydantic import BaseModel

dataset_router = APIRouter()


@dataset_router.post("/")
async def upload_finetune(name: str, description: str, pool_id: str, file: UploadFile):
    submit_finetune_dataset(pool_id, name, description, file.file)


@dataset_router.delete("/{id}")
async def remove(id: int, db: Session = Depends(gen_db)):
    db.delete(db.query(DatasetEntry).filter(DatasetEntry.id == id).first())
    db.commit()
    db.close()
