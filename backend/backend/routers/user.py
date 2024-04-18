from fastapi import APIRouter, Depends, HTTPException, status
from backend.models import *
from backend.db import gen_db
from sqlalchemy.orm.session import Session
from typing import List, Literal
from passlib.hash import bcrypt
from backend.auth import *

user_router = APIRouter()


@user_router.post("")
async def add_user(identifier: str, password: str, db: Session = Depends(gen_db)):
    user = db.query(User).filter(User.identifier == identifier).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_password = bcrypt.hash(password)
    db.add(User(identifier=identifier, password=hashed_password))
    db.commit()
    return user


@user_router.get("/me")
async def get_user_me(current_identifier: str = Depends(get_current_identifier)):
    return current_identifier
