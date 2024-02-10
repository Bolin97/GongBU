from typing import BinaryIO
from backend.db import get_db
from backend.models import *
from backend.interfaces import *
from datetime import date
import json
from sys import getsizeof
from sqlalchemy.orm.session import Session

# 1 KB
CHUNKY_BY = 1024


def submit_finetune_dataset(pool_id: int, name: str, description: str, file: BinaryIO):
    db = get_db()
    # try both json and jsonl
    try:
        content = json.load(file)
    except:
        file.seek(0)
        content = [json.loads(line) for line in file]
    entry = DatasetEntry(
        pool_id=pool_id,
        name=name,
        description=description,
        type=DatasetType.finetune_instruction_input_output.value,
        creation_date=date.today(),
        size=len(content),
    )
    db.add(entry)
    db.commit()
    finished = 0
    while finished < len(content):
        next_insertation_len = len(content) - finished
        while getsizeof(content[finished:next_insertation_len]) > CHUNKY_BY:
            next_insertation_len /= 2
            next_insertation_len = int(next_insertation_len)
            if next_insertation_len == 1:
                break
        ds = FinetuneDataset(
            entry_id=entry.id,
            content=content[finished : finished + next_insertation_len],
        )
        db.add(ds)
        db.commit()
        finished += next_insertation_len

    pool = db.query(Pool).filter(Pool.id == pool_id).first()
    pool.size += 1
    db.commit()
    db.close()
