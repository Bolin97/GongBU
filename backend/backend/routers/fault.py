from backend.auth import check_access, get_current_identifier, accessible, owns
from backend.db import gen_db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm.session import Session
from backend.models import *
from sqlalchemy import or_, and_, any_, all_
from sqlalchemy import text

fault_router = APIRouter()

class FaultSearchParam(BaseModel):
    tags: list[str] = []
    start_time: str = ""
    end_time: str = ""
    limit: int = 99

@fault_router.post("")
async def get_faults(param: FaultSearchParam, db: Session = Depends(gen_db), identifier: str = Depends(get_current_identifier)):
    query = accessible(db.query(Fault), identifier)
    if param.tags:
        query = query.filter(text("source @> :tags")).params(tags=param.tags)
    # if param.start_time and len(param.start_time) > 0:
    #     query = query.filter(Fault.time >= param.start_time)
    # if param.end_time and len(param.end_time) > 0:
    #     query = query.filter(Fault.time <= param.end_time)
    return query.limit(param.limit).all()

@fault_router.get("/log/{fault_id}")
async def get_fault_log(fault_id: int, db: Session = Depends(gen_db), identifier: str = Depends(get_current_identifier)):
    if not check_access(db.query(Fault).filter(Fault.id == fault_id), identifier):
        return None
    return db.query(FaultLog).filter(FaultLog.fault_id == fault_id).first()