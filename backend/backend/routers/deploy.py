from fastapi import APIRouter, Depends
from backend.models import *
from backend.db import gen_db
from pydantic import BaseModel
from sqlalchemy.orm.session import Session
from typing import Literal
from backend.deployment.deployment_manager import manager

deploy_router = APIRouter()

class DeployEntryParams(BaseModel):
    model_or_finetune_id: int
    deploy_finetuned: bool
    start_time: str
    end_time: str
    params: dict[str, str | int | float | bool | list[str | int | float]]
    devices: Literal["auto"] | list[int]
    
@deploy_router.put("/{id}")
async def restart(id: int, db: Session = Depends(gen_db)):
    entry = db.query(DeployEntry).filter(DeployEntry.entry_id == id).first()
    if entry is None:
        return
    manager.restart(entry.entry_id)

@deploy_router.post("/")
async def add_deploy_entry(name: str, description: str, port: int, params: DeployEntryParams, db: Session = Depends(gen_db)):
    entry = DeployEntry(
        model_or_finetune_id=params.model_or_finetune_id,
        deploy_finetuned=params.deploy_finetuned,
        start_time=params.start_time,
        end_time=params.end_time,
        name=name,
        description=description,
        port=port,
        params=params.params,
        devices=params.devices if params.devices == "auto" else LIST_SEPERATER.join(map(str, params.devices)),
        state=0
    )
    db.add(entry)
    db.commit()
    manager.deploy(entry.entry_id)

@deploy_router.put("/stop/{id}")
async def manual_halt(id: int, db: Session = Depends(gen_db)):
    entry = db.query(DeployEntry).filter(DeployEntry.entry_id == id).first()
    if entry is None:
        return
    entry.state = 2
    db.commit()
    manager.stop(entry.entry_id)