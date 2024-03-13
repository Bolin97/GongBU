import multiprocessing as mp
from enum import Enum
from threading import Thread
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
from itertools import chain


class Signal(Enum):
    Terminate = 0


class Worker(Thread):
    id: int
    params: FinetuneParams

    def report_error(self):
        db = get_db()
        entry = db.query(FinetuneEntry).filter(FinetuneEntry.id == self.id).first()
        entry.state = -1
        entry.end_time = datetime.datetime.now()
        db.commit()
        db.close()

    def __init__(self, worker_id: int, params: FinetuneParams):
        super().__init__()
        self.id = worker_id
        self.stop_signal = False
        self.params = params

    def run(self):
        try:
            devices = None
            if self.params.devices == "auto":
                devices = [i for i in range(torch.cuda.device_count())]
            else:
                devices = list(map(int, self.params.devices.split(LIST_SPLITTER)))
            cuda_visible_devices = ",".join(map(str, devices))

            conda_activation = f"conda activate backend"

            script_file = os.path.join(
                os.path.dirname(__file__), "peft_finetune.py"
            )

            command = f"""
{conda_activation} && \
CUDA_VISIBLE_DEVICES={cuda_visible_devices} accelerate launch {script_file} --finetune_id {self.id}
            """
            # start a new tmux session named finetune_task_{self.id}
            os.system(f"tmux new-session -d -s finetune_task_{self.id} '{command}'")
            print(f"finetune_task_{self.id} started")
            # print tmux session name
            print(f"tmux session name:\nfinetune_task_{self.id}")
        except Exception as e:
            self.report_error()
            print(e)