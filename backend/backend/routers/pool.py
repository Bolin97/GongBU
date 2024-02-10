from datetime import date
from backend.db import gen_db
from backend.models import *
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from pydantic import BaseModel

pool_router = APIRouter()


@pool_router.post("/")
async def new(name: str, description: str, db: Session = Depends(gen_db)):
    pool = Pool(
        name=name,
        description=description,
        creation_date=date.today(),
        size=0,
    )
    db.add(pool)
    db.commit()
    return pool.id


@pool_router.delete("/{id}")
async def remove(id: int, db: Session = Depends(gen_db)):
    db.delete(db.query(Pool).filter(Pool.id == id).first())
    db.commit()


@pool_router.get("/")
async def get_all_info(db: Session = Depends(gen_db)):
    return db.query(Pool).all()
