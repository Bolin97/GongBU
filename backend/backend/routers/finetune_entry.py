from backend.db import gen_db
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from backend.models import *
import shutil
import os
from backend.auth import get_current_identifier, accessible

finetune_entry_router = APIRouter()


@finetune_entry_router.get("")
async def get_all_ft_entry(
    db: Session = Depends(gen_db), identifier: str = Depends(get_current_identifier)
):
    return accessible(db.query(FinetuneEntry), identifier).all()


@finetune_entry_router.get("/reduced/{id}")
async def reduced(
    id: int,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    entry = (
        accessible(db.query(FinetuneEntry), identifier)
        .filter(FinetuneEntry.id == id)
        .first()
    )
    return (
        {
            "id": entry.id,
            "name": entry.name,
            "description": entry.description,
            "start_time": entry.start_time,
            "state": entry.state,
        }
        if entry
        else None
    )


@finetune_entry_router.get("/reduced")
async def reduced(
    db: Session = Depends(gen_db), identifier: str = Depends(get_current_identifier)
):
    return list(
        map(
            lambda entry: {
                "id": entry.id,
                "name": entry.name,
                "description": entry.description,
                "start_time": entry.start_time,
                "state": entry.state,
            },
            accessible(db.query(FinetuneEntry), identifier).all(),
        )
    )


@finetune_entry_router.get("/{id}")
async def get_all_ft_entry(
    id: int,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    return accessible(
        db.query(FinetuneEntry).filter(FinetuneEntry.id == id), identifier
    ).first()


@finetune_entry_router.delete("/{id}")
async def delete_files_and_entry(
    id: int,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    entry = accessible(
        db.query(FinetuneEntry).filter(FinetuneEntry.id == id), identifier
    ).first()
    db.delete(entry)
    related_adapter = db.query(
        Adapter
    ).filter(
        Adapter.ft_entry == id
    ).first()
    if related_adapter:
        db.delete(related_adapter)
    # under entry.output_dir
    # remove all folder follows checkpoint-number
    for folder in os.listdir(entry.output_dir):
        if folder.startswith("checkpoint-"):
            shutil.rmtree(os.path.join(entry.output_dir, folder))

    # remove adapter_model.bin adapter_config.json README.md
    files_to_remove = ["adapter_model.bin", "adapter_config.json", "README.md"]
    for file in files_to_remove:
        file_path = os.path.join(entry.output_dir, file)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    

    db.commit()
