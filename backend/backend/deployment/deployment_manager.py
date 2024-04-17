from backend.db import get_db
from backend.sync import SafeDict
from backend.models import *
import os

import torch

class DeploymentManager:
    instance: 'DeploymentManager'
    
    # active deployment id to tmux session name
    delpoyments: SafeDict[int, str]
    
    def __new__(cls):
        # singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeploymentManager, cls).__new__(cls)
            cls.instance.deployments = SafeDict()
        return cls.instance

    def start(self, deployment_id: int):
        if deployment_id in self.deployments:
            return
        self.deployments[deployment_id] = f"deployment_task_{deployment_id}"
        db = get_db()
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        if deployment is None:
            db.close()
            return
        deployment.state = 1
        db.commit()
        
        if deployment.devices[0] == "auto":
            devices = [i for i in range(torch.cuda.device_count())]
        else:
            devices = list(map(int, deployment.devices))
        cuda_visible_devices = ",".join(map(str, devices))

        script_file = os.path.join(
            os.path.dirname(__file__), "gradio_app.py"
        )
        command = f"""
CUDA_VISIBLE_DEVICES={cuda_visible_devices} /micromamba/bin/micromamba run -n backend python {script_file} --deployment_id {deployment_id}
            """
        # start a new tmux session named finetune_task_{self.id}
        os.system(f"tmux new-session -d -s deployment_task_{deployment_id} '{command}'")
        # write the stdout of the tmux session in real time
        os.system(f"tmux pipe-pane -o -t deployment_task_{deployment_id} 'cat > {os.getenv('LOG_PATH')}/deployment_task_{deployment_id}.log'")
        print(f"deployment_task_{deployment_id} started")
        # print tmux session name
        print(f"tmux session name:\ndeployment_task_{deployment_id}")
        db.close()
    
    def stop(self, deployment_id: int):
        if deployment_id in self.deployments:
            del self.deployments[deployment_id]
        os.system(f"tmux send-keys -t deployment_task_{deployment_id} C-c")
        # then delete the tmux session
        os.system(f"tmux kill-session -t deployment_task_{deployment_id}")
        db = get_db()
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        deployment.state = 0
        db.commit()

depl_mgr = DeploymentManager()