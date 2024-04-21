from fastapi import APIRouter
from backend.auth import get_current_identifier, owns
from backend.models import *
from backend.db import gen_db
from sqlalchemy.orm.session import Session

visibility_router = APIRouter()

from fastapi import Depends

# Four types of data can toggle visibility
# Dataset, LLM, Adapter, Pool
@visibility_router.get("/dataset/owns/{dataset_id}")
async def owns_dataset(dataset_id: int, db: Session = Depends(gen_db), current_identifier: str = Depends(get_current_identifier)):
    return owns(db.query(DatasetEntry).filter(DatasetEntry.id == dataset_id), current_identifier)

@visibility_router.get("/openllm/owns/{openllm_id}")
async def owns_openllm(openllm_id: int, db: Session = Depends(gen_db), current_identifier: str = Depends(get_current_identifier)):
    return owns(db.query(OpenLLM).filter(OpenLLM.id == openllm_id), current_identifier)

@visibility_router.get("/adapter/owns/{adapter_id}")
async def owns_adapter(adapter_id: int, db: Session = Depends(gen_db), current_identifier: str = Depends(get_current_identifier)):
    return owns(db.query(Adapter).filter(Adapter.id == adapter_id), current_identifier)

@visibility_router.get("/pool/owns/{pool_id}")
async def owns_pool(pool_id: int, db: Session = Depends(gen_db), current_identifier: str = Depends(get_current_identifier)):
    return owns(db.query(Pool).filter(Pool.id == pool_id), current_identifier)

@visibility_router.get("/dataset/public/{dataset_id}")
async def get_dataset_visibility(dataset_id: int, db: Session = Depends(gen_db)):
    return db.query(DatasetEntry).filter(DatasetEntry.id == dataset_id).first().public

@visibility_router.get("/openllm/public/{openllm_id}")
async def get_openllm_visibility(openllm_id: int, db: Session = Depends(gen_db)):
    return db.query(OpenLLM).filter(OpenLLM.id == openllm_id).first().public

@visibility_router.get("/adapter/public/{adapter_id}")
async def get_adapter_visibility(adapter_id: int, db: Session = Depends(gen_db)):
    return db.query(Adapter).filter(Adapter.id == adapter_id).first().public

@visibility_router.get("/pool/public/{pool_id}")
async def get_pool_visibility(pool_id: int, db: Session = Depends(gen_db)):
    return db.query(Pool).filter(Pool.id == pool_id).first().public

@visibility_router.put("/dataset/public/{dataset_id}")
async def set_dataset_visibility(
    dataset_id: int, public: bool, db: Session = Depends(gen_db), current_identifier: str = Depends(get_current_identifier)
):
    dataset = db.query(DatasetEntry).filter(DatasetEntry.id == dataset_id).first()
    if dataset is None:
        return {"success": False, "message": "dataset_not_found"}
    if dataset.owner != current_identifier:
        return {"success": False, "message": "not_owner"}
    dataset.public = public
    db.commit()
    return {"success": True}

@visibility_router.put("/openllm/public/{openllm_id}")
async def set_openllm_visibility(
    openllm_id: int, public: bool, db: Session = Depends(gen_db), current_identifier: str = Depends(get_current_identifier)
):
    openllm = db.query(OpenLLM).filter(OpenLLM.id == openllm_id).first()
    if openllm is None:
        return {"success": False, "message": "openllm_not_found"}
    if openllm.owner != current_identifier:
        return {"success": False, "message": "not_owner"}
    openllm.public = public
    db.commit()
    return {"success": True}

@visibility_router.put("/adapter/public/{adapter_id}")
async def set_adapter_visibility(
    adapter_id: int, public: bool, db: Session = Depends(gen_db), current_identifier: str = Depends(get_current_identifier)
):
    adapter = db.query(Adapter).filter(Adapter.id == adapter_id).first()
    if adapter is None:
        return {"success": False, "message": "adapter_not_found"}
    if adapter.owner != current_identifier:
        return {"success": False, "message": "not_owner"}
    adapter.public = public
    db.commit()
    return {"success": True}

@visibility_router.put("/pool/public/{pool_id}")
async def set_pool_visibility(
    pool_id: int, public: bool, db: Session = Depends(gen_db), current_identifier: str = Depends(get_current_identifier)
):
    pool = db.query(Pool).filter(Pool.id == pool_id).first()
    if pool is None:
        return {"success": False, "message": "pool_not_found"}
    if pool.owner != current_identifier:
        return {"success": False, "message": "not_owner"}
    pool.public = public
    db.commit()
    return {"success": True}

