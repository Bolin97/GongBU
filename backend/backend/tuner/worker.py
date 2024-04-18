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
from subprocess import Popen, PIPE

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
            if self.params.devices[0] == "auto":
                devices = [i for i in range(torch.cuda.device_count())]
            else:
                devices = list(map(int, self.params.devices))
            cuda_visible_devices = ",".join(map(str, devices))

            script_file = os.path.join(os.path.dirname(__file__), "peft_finetune.py")

            disable_ib_p2p = os.getenv("DISABLE_IB_P2P", None)
            disable_ib_p2p_command = "NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1"

            command = f"""
{"" if disable_ib_p2p is None else disable_ib_p2p_command} CUDA_VISIBLE_DEVICES={cuda_visible_devices} /micromamba/bin/micromamba run -n backend accelerate launch --main_process_port {29500 + self.id} {script_file} --finetune_id {self.id}
            """
            # start a new tmux session named finetune_task_{self.id}
            os.system(
                f"tmux new-session -d -s finetune_task_{self.id} '{command}'; tmux send-keys -t finetune_task_{self.id} exit"
            )
            # write the stdout of the tmux session in real time
            os.system(
                f"tmux pipe-pane -o -t finetune_task_{self.id} 'cat > {os.getenv('LOG_PATH')}/finetune_task_{self.id}.log'"
            )
        except Exception as e:
            self.report_error()
            print(e)
