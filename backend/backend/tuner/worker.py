import multiprocessing as mp
from enum import Enum
from typing import Callable
from backend.db import get_db
from backend.models import *
from backend.shared_params import FinetuneParams
import os
import multiprocessing as mp
from pathlib import Path
from .peft_finetune import train
from pandas import DataFrame
from transformers import TrainerCallback
from .callback import ReportCallback
import torch
import datetime
from backend.sync import ctx
from itertools import chain


class Signal(Enum):
    Terminate = 0


class Worker(ctx.Process):
    id: int
    params: FinetuneParams

    def report_error(self):
        db = get_db()
        entry = db.query(FinetuneEntry).filter(FinetuneEntry.id == self.id).first()
        entry.state = -1
        entry.end_time = datetime.datetime.now()
        db.commit()

    def __init__(self, worker_id: int, params: FinetuneParams):
        super().__init__()
        self.id = worker_id
        self.stop_signal = False
        self.params = params

    def run(self):
        try:
            db = get_db()
            callback = ReportCallback(self.id, 0 if self.params.devices == "auto" else min(self.params.devices), self.params.eval_indexes)
            model_path = (
                db.query(OpenLLM)
                .filter(OpenLLM.model_id == self.params.model_id)
                .first()
                .local_path
            )
            dataset_json_obj = list(
                chain(
                    *[
                        each.content
                        for each in db.query(FinetuneDataset)
                        .filter(FinetuneDataset.entry_id == self.params.dataset_id)
                        .all()
                    ]
                )
            )
            train(
                base_model=model_path,
                dataset_type=0,
                dataset=dataset_json_obj,
                devices=self.params.devices,
                report_callback=callback,
                output_dir=self.params.output_dir,
                adapter_name=self.params.adapter_name,
                batch_size=self.params.batch_size,
                micro_batch_size=self.params.micro_batch_size,
                num_epochs=self.params.num_epochs,
                learning_rate=self.params.learning_rate,
                cutoff_len=self.params.cutoff_len,
                val_set_size=self.params.val_set_size,
                use_gradient_checkpointing=self.params.use_gradient_checkpointing,
                eval_step=self.params.eval_step,
                save_step=self.params.save_step,
                logging_step=self.params.logging_step,
                lora_r=self.params.lora_r,
                lora_alpha=self.params.lora_alpha,
                lora_dropout=self.params.lora_dropout,
                num_virtual_tokens=self.params.num_virtual_tokens,
                bits_and_bytes=self.params.bits_and_bytes,
                load_8bit=self.params.load_8bit,
                load_4bit=self.params.load_4bit,
                llm_int8_threshold=self.params.llm_int8_threshold,
                llm_int8_enable_fp32_cpu_offload=self.params.llm_int8_enable_fp32_cpu_offload,
                llm_int8_has_fp16_weight=self.params.llm_int8_has_fp16_weight,
                bnb_4bit_compute_dtype=None
                if self.params.bnb_4bit_compute_dtype == "None"
                else self.params.bnb_4bit_compute_dtype,
                bnb_4bit_quant_type=self.params.bnb_4bit_quant_type,
                bnb_4bit_use_double_quant=self.params.bnb_4bit_use_double_quant,
                train_on_inputs=self.params.train_on_inputs,
                group_by_length=self.params.group_by_length,
            )
        except Exception as e:
            self.report_error()
            print(e)
        finally:
            db.close()
