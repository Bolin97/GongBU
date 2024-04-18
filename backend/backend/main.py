from backend.db import gen_db
from backend.models import User
import bcrypt
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
import multiprocessing as mp
from backend.auth import *
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1024)

generate_sign_up_token()

@app.get("/ping")
async def pong():
    return "pong"

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(gen_db)
):
    identifier, password = form_data.username, form_data.password
    user = db.query(User).filter(User.identifier == identifier).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return {"access_token": generate_jwt_token(identifier), "token_type": "bearer"}


from .routers import *

app.include_router(openllm_router, prefix="/openllm")

app.include_router(adapter_router, prefix="/adapter")

app.include_router(cuda_router, prefix="/cuda")

app.include_router(pool_router, prefix="/pool")

app.include_router(dataset_entry_router, prefix="/dataset_entry")

app.include_router(dataset_router, prefix="/dataset")

app.include_router(finetune_router, prefix="/finetune")

app.include_router(fault_router, prefix="/fault")

app.include_router(finetune_entry_router, prefix="/finetune_entry")

app.include_router(finetune_progress_router, prefix="/finetune_progress")

app.include_router(logging_router, prefix="/logging")

app.include_router(ft_eval_index_router, prefix="/eval_index")

app.include_router(file_router, prefix="/file")

app.include_router(user_router, prefix="/user")

app.include_router(deployment_router, prefix="/deployment")

app.include_router(eval_router, prefix="/eval")

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")
