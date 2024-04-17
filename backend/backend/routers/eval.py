import datetime
from backend.auth import get_current_identifier, accessible
from backend.db import gen_db
from backend.models import *
from fastapi import APIRouter
from backend.eval.eval_manager import eval_mgr
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

eval_router = APIRouter()

class EvalParams(BaseModel):
    model_or_adapter_id : int
    deploy_base_model : bool
    bits_and_bytes : bool
    load_8bit : bool
    load_4bit : bool
    use_flash_attention : bool
    use_deepspeed : bool
    devices : list[str]
    indexes : list[str]
    dataset_id : int
    val_set_size : float

@eval_router.post("")
async def create(name: str, description: str, params: EvalParams, identifier = Depends(get_current_identifier), db: Session = Depends(gen_db)):
    entry = Evaluation(
        name = name,
        description = description,
        state = 0,
        start_time = datetime.datetime.utcnow(),
        model_or_adapter_id = params.model_or_adapter_id,
        deploy_base_model = params.deploy_base_model,
        bits_and_bytes = params.bits_and_bytes,
        load_8bit = params.load_8bit,
        load_4bit = params.load_4bit,
        use_flash_attention = params.use_flash_attention,
        use_deepspeed = params.use_deepspeed,
        devices = params.devices,
        indexes = params.indexes,
        dataset_id = params.dataset_id,
        val_set_size = params.val_set_size,
        owner = identifier,
        public = False
    )
    db.add(entry)
    db.commit()
    db.add(
        EvaluationProgress(
            entry_id = entry.id,
            total = 1,
            current = 0
        )
    )
    db.commit()
    eval_mgr.start(entry.id)
    return entry.id

@eval_router.get("")
async def get_all(identifier = Depends(get_current_identifier), db: Session = Depends(gen_db)):
    return accessible(db.query(Evaluation), identifier).all()

@eval_router.get("/{id}")
async def get(id: int, identifier = Depends(get_current_identifier), db: Session = Depends(gen_db)):
    return accessible(db.query(Evaluation), identifier).filter(Evaluation.id == id).first()

@eval_router.get("/progress/{id}")
async def get_progress(id: int, db: Session = Depends(gen_db)):
    return db.query(EvaluationProgress).filter(EvaluationProgress.entry_id == id).first()