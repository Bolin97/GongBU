from fastapi import Depends, FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
import multiprocessing as mp

os.environ["MKL_THREADING_LAYER"] = "GNU"

app = FastAPI()

orgins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=orgins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return "Server is running"

from .routers import *

app.include_router(openllm_router, prefix="/openllm")

app.include_router(cuda_router, prefix="/cuda")

app.include_router(pool_router, prefix="/pool")

app.include_router(dataset_entry_router, prefix="/dataset_entry")

app.include_router(dataset_router, prefix="/dataset")

app.include_router(finetune_router, prefix="/finetune")

app.include_router(finetune_entry_router, prefix="/finetune_entry")

app.include_router(finetune_progress_router, prefix="/finetune_progress")

app.include_router(logging_router, prefix="/logging")

app.include_router(eval_index_router, prefix="/eval_index")

app.include_router(deploy_router, prefix="/deploy")

app.include_router(deploy_entry_router, prefix="/deploy_entry")

app.include_router(access_counter_router, prefix="/access_counter")

app.include_router(application_router, prefix="/application")

app.include_router(file_router, prefix="/file")

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")
