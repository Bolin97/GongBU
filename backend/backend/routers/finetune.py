from backend.db import gen_db
from backend.models import *
from backend.shared_params import FinetuneParams
from fastapi import APIRouter
from typing import List, Literal
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from backend.tuner.worker import Worker
import datetime
import multiprocessing as mp

finetune_router = APIRouter()


@finetune_router.post("/")
async def add_ft_task(
    name: str, description: str, params: FinetuneParams, db: Session = Depends(gen_db)
):
    entry = FinetuneEntry(
        model_id=params.model_id,
        name=name,
        description=description,
        dataset_id=params.dataset_id,
        devices=params.devices
        if params.devices == "auto"
        else LIST_SEPERATER.join(map(str, params.devices)),
        eval_indexes=LIST_SEPERATER.join(params.eval_indexes),
        output_dir=params.output_dir,
        adapter_name=params.adapter_name,
        batch_size=params.batch_size,
        micro_batch_size=params.micro_batch_size,
        num_epochs=params.num_epochs,
        learning_rate=params.learning_rate,
        cutoff_len=params.cutoff_len,
        val_set_size=params.val_set_size,
        use_gradient_checkpointing=params.use_gradient_checkpointing,
        eval_step=params.eval_step,
        save_step=params.save_step,
        logging_step=params.logging_step,
        lora_r=params.lora_r,
        lora_alpha=params.lora_alpha,
        lora_dropout=params.lora_dropout,
        num_virtual_tokens=params.num_virtual_tokens,
        train_on_inputs=params.train_on_inputs,
        group_by_length=params.group_by_length,
        bits_and_bytes=params.bits_and_bytes,
        load_8bit=params.load_8bit,
        load_4bit=params.load_4bit,
        llm_int8_threshold=params.llm_int8_threshold,
        llm_int8_enable_fp32_cpu_offload=params.llm_int8_enable_fp32_cpu_offload,
        llm_int8_has_fp16_weight=params.llm_int8_has_fp16_weight,
        bnb_4bit_compute_dtype=params.bnb_4bit_compute_dtype,
        bnb_4bit_quant_type=params.bnb_4bit_quant_type,
        bnb_4bit_use_double_quant=params.bnb_4bit_use_double_quant,
        state=0,
        start_time=datetime.datetime.now(),
    )
    db.add(entry)
    db.commit()
    w = Worker(entry.id, params)
    w.start()
    return entry.id


@finetune_router.put("/stop/{id}")
async def stop(id: int, db: Session = Depends(gen_db)):
    db.add(Signal(entry_id=id, signal=0))
    db.commit()
    return None