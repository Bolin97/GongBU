from backend.db import gen_db
from backend.enumerate import DeploymentState
from backend.models import Deployment
from fastapi import APIRouter, HTTPException
from backend.deployment.deployment_manager import depl_mgr
from fastapi.params import Depends
from pydantic import BaseModel
from backend.auth import get_current_identifier, accessible, owns
from sqlalchemy.orm.session import Session

deployment_router = APIRouter()


class DeploymentParams(BaseModel):
    model_or_adpater_id: int
    deploy_base_model: bool
    bits_and_bytes: bool
    load_8bit: bool
    load_4bit: bool
    use_flash_attention: bool
    use_deepspeed: bool
    devices: list[str]
    port: int
    use_vllm: bool


@deployment_router.post("")
async def deploy(
    name: str,
    description: str,
    params: DeploymentParams,
    identifier=Depends(get_current_identifier),
    db: Session = Depends(gen_db),
):
    entry = Deployment(
        name=name,
        description=description,
        owner=identifier,
        state=DeploymentState.stopped.value,
        public=False,
        model_or_adapter_id=params.model_or_adpater_id,
        deploy_base_model=params.deploy_base_model,
        bits_and_bytes=params.bits_and_bytes,
        load_8bit=params.load_8bit,
        load_4bit=params.load_4bit,
        use_flash_attention=params.use_flash_attention,
        use_deepspeed=params.use_deepspeed,
        devices=params.devices,
        port=params.port,
        use_vllm=params.use_vllm,
    )
    db.add(entry)
    db.commit()
    return entry.id


@deployment_router.put("/start/{id}")
async def start(id: int, db: Session=Depends(gen_db), identifier=Depends(get_current_identifier)):
    if not owns(db.query(Deployment).filter(Deployment.id == id), identifier):
        raise HTTPException(status_code=403, detail="Forbidden")
    depl_mgr.start(id)
    return


@deployment_router.put("/stop/{id}")
async def stop(id: int, db: Session=Depends(gen_db), identifier=Depends(get_current_identifier)):
    if not owns(db.query(Deployment).filter(Deployment.id == id), identifier):
        raise HTTPException(status_code=403, detail="Forbidden")
    depl_mgr.stop(id)
    return


@deployment_router.get("")
async def get_all(
    identifier=Depends(get_current_identifier), db: Session = Depends(gen_db)
):
    return accessible(db.query(Deployment), identifier).all()


@deployment_router.get("/{id}")
async def get(
    id: int, identifier=Depends(get_current_identifier), db: Session = Depends(gen_db)
):
    return accessible(
        db.query(Deployment).filter(Deployment.id == id), identifier
    ).first()


@deployment_router.delete("/{id}")
async def delete(
    id: int, identifier=Depends(get_current_identifier), db: Session = Depends(gen_db)
):
    entry = db.query(Deployment).filter(Deployment.id == id)
    if owns(entry, identifier):
        entry.delete()
        db.commit()
    return
