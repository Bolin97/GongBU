from backend.db import get_db
from backend.shared_params import FinetuneParams
from backend.sync import SafeDict
import torch
from backend.enumerate import *
import os
from backend.models import *


def run(task_id: int, params: FinetuneParams):
    devices = None
    if params.devices[0] == "auto":
        devices = [i for i in range(torch.cuda.device_count())]
    else:
        devices = list(map(int, params.devices))
    cuda_visible_devices = ",".join(map(str, devices))

    script_file = os.path.join(os.path.dirname(__file__), "peft_finetune.py")

    disable_ib_p2p = os.getenv("DISABLE_IB_P2P", None)
    disable_ib_p2p_command = "NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1"

    command = f"""
{"" if disable_ib_p2p is None else disable_ib_p2p_command} CUDA_VISIBLE_DEVICES={cuda_visible_devices} /micromamba/bin/micromamba run -n backend accelerate launch --main_process_port {29500 + task_id} {script_file} --finetune_id {task_id}
    """
    session_name = f"{TaskType.finetune.value}_task_{task_id}"
    os.system(
        f"tmux new-session -d -s {session_name} '{command}'; tmux send-keys -t {session_name} exit"
    )
    # write the stdout of the tmux session in real time
    os.system(
        f"tmux pipe-pane -o -t {session_name} 'cat > {os.getenv('LOG_PATH')}/{session_name}.log'"
    )
    
class FinetuneManager:
    instance: "FinetuneManager"

    # active finetune id to tmux session name
    finetunes: SafeDict[int, str]

    def __new__(cls):
        # singleton
        if not hasattr(cls, "instance"):
            cls.instance = super(FinetuneManager, cls).__new__(cls)
            cls.instance.finetunes = SafeDict()
        return cls.instance

    def start(self, finetune_id: int, params: FinetuneParams):
        if finetune_id in self.finetunes:
            return
        self.finetunes[finetune_id] = f"finetune_task_{finetune_id}"
        # db = get_db()
        # finetune = db.query(FinetuneEntry).filter(FinetuneEntry.id == finetune_id).first()
        # if finetune is None:
        #     db.close()
        #     return
        # db.commit()

        run(finetune_id, params)

        # db.close()

    def stop(self, finetune_id: int):
        if finetune_id in self.finetunes:
            del self.finetunes[finetune_id]
        session_name = f"{TaskType.finetune.value}_task_{finetune_id}"
        os.system(f"tmux send-keys -t {session_name} C-c")
        # then delete the tmux session
        os.system(f"tmux kill-session -t {session_name}")
        db = get_db()
        finetune = db.query(FinetuneEntry).filter(FinetuneEntry.id == finetune_id).first()
        finetune.state = 0
        db.commit()


ft_mgr = FinetuneManager()