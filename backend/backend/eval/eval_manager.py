from backend.db import get_db
from backend.sync import SafeDict
from backend.models import *
import os

import torch

class EvalManager:
    instance: 'EvalManager'
    
    # active evaluation id to tmux session name
    evaluations: SafeDict[int, str]
    
    def __new__(cls):
        # singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(EvalManager, cls).__new__(cls)
            cls.instance.evaluations = SafeDict()
        return cls.instance

    def start(self, evaluation_id: int):
        if evaluation_id in self.evaluations:
            return
        self.evaluations[evaluation_id] = f"evaluation_task_{evaluation_id}"
        db = get_db()
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if evaluation is None:
            db.close()
            return
        evaluation.state = 1
        db.commit()
        
        if evaluation.devices[0] == "auto":
            devices = [i for i in range(torch.cuda.device_count())]
        else:
            devices = list(map(int, evaluation.devices))
        cuda_visible_devices = ",".join(map(str, devices))

        script_file = os.path.join(
            os.path.dirname(__file__), "eval_script.py"
        )
        command = f"""
CUDA_VISIBLE_DEVICES={cuda_visible_devices} /micromamba/bin/micromamba run -n backend python {script_file} --evaluation_id {evaluation_id}
            """
        # start a new tmux session named evaluation_task_{self.id}
        os.system(f"tmux new-session -d -s evaluation_task_{evaluation_id} '{command}'")
        # write the stdout of the tmux session in real time
        os.system(f"tmux pipe-pane -o -t evaluation_task_{evaluation_id} 'cat > {os.getenv('LOG_PATH')}/evaluation_task_{evaluation_id}.log'")
        print(f"evaluation_task_{evaluation_id} started")
        # print tmux session name
        print(f"tmux session name:\nevaluation_task_{evaluation_id}")
        db.close()
    
    def stop(self, evaluation_id: int):
        if evaluation_id in self.evaluations:
            del self.evaluations[evaluation_id]
        os.system(f"tmux send-keys -t evaluation_task_{evaluation_id} C-c")
        # then delete the tmux session
        os.system(f"tmux kill-session -t evaluation_task_{evaluation_id}")
        db = get_db()
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        evaluation.state = 0
        db.commit()

eval_mgr = EvalManager()