from datetime import timedelta
from fastapi import APIRouter
from backend.models import *
from backend.db import gen_db
from fastapi.params import Depends
from sqlalchemy.orm.session import Session

access_counter_router = APIRouter()

@access_counter_router.get("/{entry_id}")
async def get_count(entry_id: int, db: Session = Depends(gen_db)):
    all_count =  db.query(DeployAccessCounter).filter(DeployAccessCounter.entry_id == entry_id).order_by(DeployAccessCounter.date.desc()).all()
    if len(all_count) == 0:
        return []
    start_date = all_count[-1].date
    end_date = all_count[0].date
    count_dict = {each.date: each.count for each in all_count}
    delta = end_date - start_date
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        if day not in count_dict:
            count_dict[day] = 0
    return list(sorted(map(lambda each: {
        "date": each,
        "count": count_dict[each]
    }, count_dict.keys()), key=lambda each: each["date"]))