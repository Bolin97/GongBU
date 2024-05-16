from fastapi import APIRouter
from backend.db import *
from backend.models import *
from backend.auth import *
from sqlalchemy.orm import Session

adapter_router = APIRouter()


@adapter_router.get("/by_base_model/{base_model_id}")
async def by_base_model(
    base_model_id: int,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    base_model = accessible(
        db.query(OpenLLM).filter(OpenLLM.id == base_model_id), identifier
    ).first()
    return accessible(
        db.query(Adapter).filter(Adapter.base_model_name == base_model.model_name),
        identifier,
    ).all()


@adapter_router.get("/{id}")
async def get(
    id: int,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    return accessible(db.query(Adapter).filter(Adapter.id == id), identifier).first()

@adapter_router.delete("/{id}")
async def delete(
    id: int,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    adapter = accessible(db.query(Adapter).filter(Adapter.id == id), identifier).first()
    if adapter.owner != identifier:
        raise HTTPException(status_code=403, detail="Permission denied")
    db.delete(adapter)
    db.commit()
    return adapter
