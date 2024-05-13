from itertools import chain
from typing import BinaryIO
from backend.db import get_db
from backend.models import *
from backend.enumerate import *
from datetime import date
import json
from sys import getsizeof
from backend.tuner.generate_prompt import generate_prompt
from sqlalchemy.orm.session import Session
from backend.service.dataset import fetch_dataset
import os

def kmeans_sift(
    kind: int,
    source_entry_id: int,
    reduce_to_percent: float,
):
    original, _ = fetch_dataset(source_entry_id)
    prompts = list(map(lambda x: generate_prompt(x, kind), original))
    from sentence_transformers import SentenceTransformer
    embd = SentenceTransformer(
        os.getenv("EMBEDDING_PATH", "moka-ai/m3e-base")
    )
    from tqdm import tqdm
    import numpy as np
    vecs = []
    for each in tqdm(prompts):
        vecs.append(embd.encode(each))
    vecs = np.array(vecs).squeeze()
    import faiss
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    k = int(reduce_to_percent * vecs.shape[0])
    if reduce_to_percent == 0:
        k = 1
    elif reduce_to_percent == 1:
        return original    
    if k == 0:
        k = 1
    kmeans = faiss.Kmeans(vecs.shape[1], k, niter=50, verbose=True)
    kmeans.train(vecs)
    centriods = kmeans.centroids
    D, I = index.search(centriods, 1)
    return [original[i] for i in I.flatten().tolist()]