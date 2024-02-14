import os
import subprocess
from threading import Thread
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from backend.models import OpenLLM
from fastapi.params import Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm.session import Session
from backend.db import gen_db, get_db
from typing import Optional
from pydantic import BaseModel
import requests as rq
import shutil
import datetime
from PIL import Image
from io import BytesIO

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
        return FileResponse("./logo.jpg")
    return FileResponse(path)


@openllm_router.get("/")
async def read_all_openllms(db: Session = Depends(gen_db)):
    all_llm_entry = db.query(OpenLLM).all()
    if all_llm_entry is None:
        raise HTTPException(status_code=404, detail="No model found")
    return all_llm_entry

class ModelListItem(BaseModel):
    model_name: str
    model_display_name: str
    source: str
    model_description: str
    lora_support: int
    lora_multi_device: int
    prefix_tuning_support: int
    prefix_tuning_multi_device: int
    ptuning_support: int
    ptuning_multi_device: int
    prompt_tuning_support: int
    prompt_tuning_multi_device: int
    IA3_support: int
    IA3_multi_device: int
    finetune: int
    deployment: int
    download_url: str
    avatar_url: Optional[str] = None

def download_model(info: ModelListItem, entry_id: int):
    db = get_db()
    if info.source == "git":
        entry = db.query(OpenLLM).filter(OpenLLM.model_id == entry_id).first()
        entry.storage_state = "Downloading"
        local_path = os.path.join(os.environ.get("MODEL_PATH"), info.model_name)
        db.commit()
        command = f"""cd {os.environ.get("MODEL_PATH")} && git init && git lfs install && git clone {info.download_url} {info.model_name}"""
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # Stream output to stdout
        for line in iter(process.stdout.readline, b''):
            print(line.decode().strip())
        entry.local_path = local_path
        entry.local_store = 1
        entry.storage_state = "Ready"
        db.commit()
    db.close()

def write_info(info: ModelListItem):
    # create model_avatars folder if not exists
    if not os.path.exists(os.path.join(os.environ.get("MODEL_PATH"), "model_avatars")):
        os.makedirs(os.path.join(os.environ.get("MODEL_PATH"), "model_avatars"))
    
    db = get_db()
    # avatar
    view_pic = f"{info.model_name}.png"
    try:
        response = rq.get(info.avatar_url, timeout=5)
        img = Image.open(BytesIO(response.content))
        img.thumbnail((100, 100))
        byte_io = BytesIO()
        img.save(byte_io, format='PNG', compress_level=9)
        byte_io.seek(0)
        # Save the image to a file with a .png extension
        filename = os.path.join(os.environ.get("MODEL_PATH"), "model_avatars", f"{info.model_name}.png")
        with open(filename, 'wb') as f:
            f.write(byte_io.getbuffer())
    except:
        view_pic = "ERR"
    
    local_path = os.path.join(os.environ.get("MODEL_PATH"), info.model_name)
    entry = OpenLLM(
        model_name = info.model_display_name,
        model_description = info.model_description,
        view_pic = view_pic,
        remote_path = info.download_url,
        local_path = local_path,
        local_store = 0,
        lora_support = info.lora_support,
        lora_multi_device = info.lora_multi_device,
        prefix_tuning_support = info.prefix_tuning_support,
        prefix_tuning_multi_device = info.prefix_tuning_multi_device,
        ptuning_support = info.ptuning_support,
        ptuning_multi_device = info.ptuning_multi_device,
        prompt_tuning_support = info.prompt_tuning_support,
        prompt_tuning_multi_device = info.prompt_tuning_multi_device,
        IA3_support = info.IA3_support,
        IA3_multi_device = info.IA3_multi_device,
        storage_state = "InfoOnly",
        storage_date = datetime.datetime.utcnow(),
        finetune = info.finetune,
        deployment = info.deployment
    )
    db.add(entry)
    db.commit()
    entry_id = entry.model_id
    db.close()
    return entry_id

@openllm_router.post("/download")
async def create_openllm_download(info: ModelListItem):
    entry_id = write_info(info)
    # Download Model in a new thread
    th = Thread(target=download_model, args=(info, entry_id))
    th.start()
    return {"status": "success"}

@openllm_router.post("/no_download")
async def create_openllm(info: ModelListItem):
    write_info(info)
    return {"status": "success"}

@openllm_router.delete("/{model_id}")
async def delete_openllm(model_id: int, db: Session = Depends(gen_db)):
    entry = db.query(OpenLLM).filter(OpenLLM.model_id == model_id).first()
    # delete the avatar
    path = os.path.join(os.environ.get("MODEL_PATH"), "model_avatars", entry.view_pic)
    if os.path.exists(path):
        os.remove(path)
    if entry is None:
        raise HTTPException(status_code=404, detail="Model not found")
    if entry.local_store == 1:
        shutil.rmtree(entry.local_path)
    db.delete(entry)
    db.commit()
    return {"status": "success"}

@openllm_router.delete("/entry/{model_id}")
async def delete_openllm_entry(model_id: int, db: Session = Depends(gen_db)):
    entry = db.query(OpenLLM).filter(OpenLLM.model_id == model_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Model not found")
    db.delete(entry)
    db.commit()
    return {"status": "success"}