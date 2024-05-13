from itertools import chain
from typing import BinaryIO
from backend.db import get_db
from backend.models import *
from backend.enumerate import *
from datetime import date
import json
from sys import getsizeof
from sqlalchemy.orm.session import Session
from typing import AnyStr, Any

# 1 KB
CHUNKY_BY = 1024


def submit_finetune_dataset(
    pool_id: int,
    name: str,
    description: str,
    kind: int,
    content: Any,
    identifier: str,
):
    db = get_db()
    entry = DatasetEntry(
        pool_id=pool_id,
        name=name,
        description=description,
        type=kind,
        created_on=date.today(),
        size=len(content),
        owner=identifier,
        public=False,
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
            owner=identifier,
            public=False,
        )
        db.add(ds)
        db.commit()
        finished += next_insertation_len

    pool = db.query(Pool).filter(Pool.id == pool_id).first()
    pool.size += 1
    db.commit()
    db.close()

def submit_finetune_dataset_file(
    pool_id: int,
    name: str,
    description: str,
    kind: int,
    file: BinaryIO,
    identifier: str,
):
    db = get_db()
    # try both json and jsonl
    try:
        content = json.load(file)
    except:
        file.seek(0)
        content = [json.loads(line) for line in file]
    submit_finetune_dataset(pool_id, name, description, kind, content, identifier)


def fetch_dataset(entry_id: int) -> tuple[list, int]:
    db = get_db()
    dataset_json_obj = list(
        chain(
            *[
                each.content
                for each in db.query(FinetuneDataset)
                .filter(FinetuneDataset.entry_id == entry_id)
                .all()
            ]
        )
    )
    dataset_type = (
        db.query(DatasetEntry).filter(DatasetEntry.id == entry_id).first().type
    )

    db.close()
    return dataset_json_obj, dataset_type


def submit_evaluation_data(entry_id: int, data: list):
    db = get_db()
    finished = 0
    while finished < len(data):
        next_insertation_len = len(data) - finished
        while getsizeof(data[finished:next_insertation_len]) > CHUNKY_BY:
            next_insertation_len /= 2
            next_insertation_len = int(next_insertation_len)
            if next_insertation_len == 1:
                break
        ds = EvaluationData(
            entry_id=entry_id,
            content=data[finished : finished + next_insertation_len],
        )
        db.add(ds)
        db.commit()
        finished += next_insertation_len
    db.close()


def submit_evaluation_generation(entry_id: int, data: list):
    db = get_db()
    finished = 0
    while finished < len(data):
        next_insertation_len = len(data) - finished
        while getsizeof(data[finished:next_insertation_len]) > CHUNKY_BY:
            next_insertation_len /= 2
            next_insertation_len = int(next_insertation_len)
            if next_insertation_len == 1:
                break
        ds = EvaluationGeneration(
            entry_id=entry_id,
            content=data[finished : finished + next_insertation_len],
        )
        db.add(ds)
        db.commit()
        finished += next_insertation_len
    db.close()
