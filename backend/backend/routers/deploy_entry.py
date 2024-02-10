from backend.db import gen_db
from backend.models import *
from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session
from backend.deployment.deployment_manager import manager

deploy_entry_router = APIRouter()

@deploy_entry_router.get("/reduced")
async def get_all_deploy_entry_reduced(db = Depends(gen_db)):
    return list(map(lambda each: {
        "entry_id": each.entry_id,
        "state": each.state,
    }, list(db.query(DeployEntry).all())))

@deploy_entry_router.get("/state/{entry_id}")
async def get_deploy_entry_state_by_id(entry_id: int, db = Depends(gen_db)):
    entry = db.query(DeployEntry).filter(DeployEntry.entry_id == entry_id).first()
    return entry.state if entry is not None else 1

@deploy_entry_router.delete("/{entry_id}")
async def delete_deploy_entry(entry_id: int, db: Session = Depends(gen_db)):
    manager.stop(entry_id)
    db.delete(db.query(DeployEntry).filter(DeployEntry.entry_id == entry_id).first())
    db.commit()

@deploy_entry_router.get("/{entry_id}")
async def get_all_deploy_entry_by_id(entry_id: int, db = Depends(gen_db)):
    return db.query(DeployEntry).filter(DeployEntry.entry_id == entry_id).first()

@deploy_entry_router.get("/")
async def get_all_deploy_entry(db = Depends(gen_db)):
    return db.query(DeployEntry).all()