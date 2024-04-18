from datetime import date
from backend.db import gen_db
from backend.models import *
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from pydantic import BaseModel
from backend.auth import accessible, get_current_identifier, owned, owns

pool_router = APIRouter()


@pool_router.post("")
async def new(
    name: str,
    description: str,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    pool = Pool(
        name=name,
        description=description,
        created_on=date.today(),
        size=0,
        owner=identifier,
        public=False,
    )
    db.add(pool)
    db.commit()
    return pool.id


@pool_router.delete("/{id}")
async def remove(
    id: int,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    if not owns(db.query(Pool).filter(Pool.id == id), identifier):
        raise HTTPException(status_code=401, detail="Unauthorized")
    db.delete(db.query(Pool).filter(Pool.id == id).first())
    db.commit()


@pool_router.get("/")
async def get_all_info(
    db: Session = Depends(gen_db), identifier: str = Depends(get_current_identifier)
):
    return accessible(db.query(Pool), identifier).all()
