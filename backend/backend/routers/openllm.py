import os
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from backend.models import OpenLLM
from fastapi.params import Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm.session import Session
from backend.db import gen_db

openllm_router = APIRouter()

@openllm_router.get("/{model_id}")
async def read_openllms(model_id: int, db: Session = Depends(gen_db)):
    llm_entry = db.query(OpenLLM).filter(OpenLLM.model_id == model_id).first()
    if llm_entry is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return llm_entry

@openllm_router.get("/avatar/{model_id}")
async def read_openllms_pic(model_id: int, db: Session = Depends(gen_db)):
    llm_entry = db.query(OpenLLM).filter(OpenLLM.model_id == model_id).first()
    path = os.path.join(os.environ.get("MODEL_PATH"), "model_avatars", llm_entry.view_pic)
    if not os.path.exists(path):
        return FileResponse("./model_avatars/default.jpg")
    return FileResponse(path)


@openllm_router.get("/")
async def read_all_openllms(db: Session = Depends(gen_db)):
    all_llm_entry = db.query(OpenLLM).all()
    if all_llm_entry is None:
        raise HTTPException(status_code=404, detail="No model found")
    return all_llm_entry
