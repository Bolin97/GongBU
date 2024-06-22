from backend.auth import check_access, get_current_identifier, accessible, owns
from backend.db import gen_db
from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm.session import Session
from backend.models import *
from sqlalchemy import desc, or_, and_, any_, all_
from sqlalchemy import text
from wordcloud import WordCloud  
from io import BytesIO  
import matplotlib.pyplot as plt  
from PIL import Image

fault_router = APIRouter()


class FaultSearchParam(BaseModel):
    tags: list[str] = []
    start_time: str = ""
    end_time: str = ""
    limit: int = 99


@fault_router.post("")
async def get_faults(
    param: FaultSearchParam,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    query = accessible(db.query(Fault), identifier)
    if param.tags:
        query = query.filter(text("source @> :tags")).params(tags=param.tags)
    # if param.start_time and len(param.start_time) > 0:
    #     query = query.filter(Fault.time >= param.start_time)
    # if param.end_time and len(param.end_time) > 0:
    #     query = query.filter(Fault.time <= param.end_time)
    return query.order_by(
            desc(Fault.id)  # Change this line
        ).limit(param.limit).all()


@fault_router.get("/log/{fault_id}")
async def get_fault_log(
    fault_id: int,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    if not check_access(db.query(Fault).filter(Fault.id == fault_id), identifier):
        return None
    return db.query(FaultLog).filter(FaultLog.fault_id == fault_id).first()

@fault_router.delete("/{fault_id}")
async def delete_fault(
    fault_id: int,
    db: Session = Depends(gen_db),
    identifier: str = Depends(get_current_identifier),
):
    if not owns(db.query(Fault).filter(Fault.id == fault_id), identifier):
        return None
    db.query(Fault).filter(Fault.id == fault_id).delete()
    db.commit()
    return

@fault_router.get("/wordcloud")
async def get_fault_wordcloud(
    db: Session = Depends(gen_db),
    # identifier: str = Depends(get_current_identifier),
):
    # faults = accessible(db.query(Fault), identifier)
    faults = db.query(Fault)

    cloudword = ""
    for fault in faults:
        cloudword += fault.message
    wordcloud = WordCloud(background_color="white", width=800, height=600, max_words=200).generate(cloudword)
    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={"xticks": [], "yticks": []})
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
  
    buf = BytesIO()  
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    headers = {
        "Content-Type": "image/png",
    }
    return StreamingResponse(buf, headers=headers) 
  
