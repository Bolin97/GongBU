from fastapi import FastAPI, Query, APIRouter
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
async def read_files(dir: Optional[str] = Query(None)):
    try:
        dir = unquote(dir)
        fullPath = os.path.abspath(dir)
        names = os.listdir(fullPath)
        entries = []
        for name in names:
            isDirectory = os.path.isdir(os.path.join(fullPath, name))
            entries.append(FileEntry(name=name, isDirectory=isDirectory))
        entries.sort(key=lambda x: (not x.isDirectory, x.name))
        return [entry for entry in entries if entry.isDirectory]
    except Exception as e:
        return {"failure": True}

@file_router.post("", response_model=FileEntry)
async def create_directory(dir: Optional[str] = Query(None), new: Optional[str] = Query(None)):
    try:
        dir = unquote(dir)
        fullPath = os.path.join(os.path.abspath(dir), new)
        os.mkdir(fullPath)
        return FileEntry(name=new, isDirectory=True)
    except Exception as e:
        return {"success": False}