from itertools import chain
import logging
from typing import BinaryIO
from backend.db import get_db
from backend.models import *
from backend.enumerate import *
from datetime import date
import json
from sys import getsizeof
from sqlalchemy.orm.session import Session
from typing import AnyStr, Any
from datasets import load_dataset, Dataset
import os

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
    if kind == 0:
        features =  ["instruction", "input", "output"]
    elif kind == 1:
        features =  ["input", "output"]
    entry = DatasetEntry(
        pool_id=pool_id,
        name=name,
        description=description,
        type=kind,
        created_on=date.today(),
        size=len(content),
        owner=identifier,
        features=features,
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

# 这个type表示是评估还是微调, 0表示的是模型评估，1表示的是模型微调
def fetch_dataset(entry_id: int, op_type: int):
    db = get_db()

    # 查询DatasetEntry，获取数据集的名称和类型
    entry = db.query(DatasetEntry).filter(DatasetEntry.id == entry_id).first()
    dataset_name = entry.name
    dataset_type = entry.type

    # 如果是外部导入的数据需要特殊处理
    if dataset_type >1 or dataset_type == -1:
        dataset_name = dataset_name.strip()
        config = entry.description
        # 设置 Hugging Face 镜像源
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

        # Try multiple mirrors if one fails
        mirrors = [
            'https://hf-mirror.com',
            'https://huggingface.co',
            None  # Default, no mirror
        ]

        dataset_json_obj = []
        success = False

        for mirror in mirrors:
            if mirror:
                os.environ['HF_ENDPOINT'] = mirror
            elif 'HF_ENDPOINT' in os.environ:
                del os.environ['HF_ENDPOINT']

            try:
                print(f"Trying to load dataset from {mirror if mirror else 'default HF endpoint'}")
                if config:
                    dataset = load_dataset(dataset_name, config)
                else:
                    dataset = load_dataset(dataset_name)
                
                if type == 0:
                    splits_order = ['test', 'validation', 'train']
                else:
                    splits_order = ['train', 'validation', 'test']
                train_dataset = None

                for split in splits_order:
                    if split in dataset:
                        train_dataset = dataset[split]
                        break

                if train_dataset is None:
                    print(f"No usable split found in dataset. Available splits: {dataset.keys()}")
                    continue

                # 模型微调保留前2000数据
                # 评估任务最多保留前20条数据, 只做简单评估测试
                if op_type == 0:
                    num_to_select = min(20, len(train_dataset))
                else:
                    num_to_select = min(2000, len(train_dataset))

                # 安全选取
                dataset_json_obj = train_dataset.select(range(num_to_select))

                print(type(dataset_json_obj))
                print(dataset_json_obj)
                
                if dataset_type == 2 and len(dataset_json_obj) > 0:
                    text = dataset_json_obj[0].get('text', '')
                    if isinstance(text, str) and len(text.split('\n')) <= 1:
                        merged_data = []
                        # 每次取两个相邻的条目合并
                        for i in range(0, len(dataset_json_obj) - 1, 2):
                            text1 = dataset_json_obj[i].get("text", "")
                            text2 = dataset_json_obj[i+1].get("text", "")
                            merged_text = f"{text1}\n{text2}"
                            merged_data.append({"text": merged_text})
                        # 更新数据集（舍弃不成对的最后一个条目）
                        dataset_json_obj = Dataset.from_list(merged_data)
                print(type(dataset_json_obj))
                print(dataset_json_obj)
                print("----------------------------------------------------------")
                success = True
                print(f"Successfully loaded dataset from {mirror if mirror else 'default HF endpoint'}")
                break

            except Exception as e:
                # 如果下载失败，尝试下一个镜像
                print(f"Error loading dataset from {mirror if mirror else 'default HF endpoint'}: {e}")
                continue

        if not success:
            print("Failed to load dataset from all mirrors. Returning empty dataset.")
            dataset_json_obj = []
    else:
        # 如果不是huggleface开头，从数据库获取数据集内容
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
