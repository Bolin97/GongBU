from fastapi import APIRouter, Depends, HTTPException, status
from backend.models import *
from backend.db import gen_db
from sqlalchemy.orm.session import Session
from typing import List, Literal
from passlib.hash import bcrypt
from backend.auth import *
import os

user_router = APIRouter()

from fastapi import Form

@user_router.post("")
async def add_user(identifier: str = Form(...), password: str = Form(...), sign_up_token: str = Form(None), db: Session = Depends(gen_db)):
    if os.getenv("NO_SIGNUP_TOKEN") is not None and sign_up_token != get_sign_up_token():
        return {
            "success": False,
            "message": "invalid_sign_up_token"
        }
    
    user = db.query(User).filter(User.identifier == identifier).first()
    if user:
        return {
            "success": False,
            "message": "user_already_exists"
        }
    hashed_password = bcrypt.hash(password)
    db.add(User(identifier=identifier, password=hashed_password))
    db.commit()
    return user

@user_router.get("/signup-token-required")
async def is_signup_token_required():
    return os.getenv("NO_SIGNUP_TOKEN") is None

@user_router.get("/me")
async def get_user_me(current_identifier: str = Depends(get_current_identifier)):
    return current_identifier
