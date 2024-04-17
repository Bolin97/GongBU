from backend.auth import get_current_identifier
from fastapi import Depends, FastAPI, Query, APIRouter
from typing import Optional
import os
from pydantic import BaseModel
from typing import List
from urllib.parse import unquote

file_router = APIRouter()

class FileEntry(BaseModel):
    name: str
    isDirectory: bool

@file_router.get("")
async def read_files(dir: Optional[str] = Query(None), identifier: str = Depends(get_current_identifier)):
    dir = unquote(dir)
    dir = dir.removeprefix("/")
    base_dir = os.path.join(os.environ.get("FINETUNE_OUTPUT"), identifier)
    full_path = os.path.abspath(
        os.path.join(base_dir, dir)
    )
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    names = os.listdir(full_path)
    entries = []
    for name in names:
        isDirectory = os.path.isdir(os.path.join(full_path, name))
        entries.append(FileEntry(name=name, isDirectory=isDirectory))
    entries.sort(key=lambda x: (not x.isDirectory, x.name))
    return [entry for entry in entries if entry.isDirectory]

@file_router.post("", response_model=FileEntry)
async def create_directory(dir: Optional[str] = Query(None), new: Optional[str] = Query(None), identifier: str = Depends(get_current_identifier)):
    try:
        dir = unquote(dir)
        dir = dir.removeprefix("/")
        base_dir = os.path.join(os.environ.get("FINETUNE_OUTPUT"), identifier)
        full_path = os.path.abspath(
            os.path.join(base_dir, dir, new)
        )
        os.mkdir(full_path)
        return FileEntry(name=new, isDirectory=True)
    except Exception as e:
        return {"success": False}