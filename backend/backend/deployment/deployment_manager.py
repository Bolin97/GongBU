from backend.sync import ctx, SafeDict
from backend.models import *
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteriaList, StoppingCriteria
import gradio as gr
import torch
from backend.db import get_db
import peft
from datetime import datetime, timedelta
from threading import Thread, Timer
import schedule
import os
import signal
import psutil
from accelerate import infer_auto_device_map, Accelerator

# -1 error
# 0 preparing
# 1 scheduled
# 2 on
# 3 finished

class LLMWrapper:
    
    model_path: str
    adapter_path: str
    devices: str
    port: int
    entry_id: int
    model: any
    tokenizer: any
    device_arr: list[str]
    
    def __init__(self, model_path: str, adapter_path: str, devices: str, port: int, entry_id: int):
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.devices = devices
        self.port = port
        self.entry_id = entry_id
    
    def load_model(self):
        device_arr = self.devices.split(LIST_SEPERATER)
        if device_arr[0] == "auto":
            device_arr = [str(i) for i in range(torch.cuda.device_count())]
        self.device_arr = device_arr
        model_on_cpu = AutoModelForCausalLM.from_pretrained(
            self.model_path, trust_remote_code=True, device_map={"": "cpu"}
        )
        distribution = {
            int(each): torch.cuda.get_device_properties(int(each)).total_memory
            for each in device_arr
        }
        distribution.update({"cpu": psutil.virtual_memory().available})
        device_map = infer_auto_device_map(
            model_on_cpu,
            distribution,
            no_split_module_classes=type(model_on_cpu)._no_split_modules
        )
        del model_on_cpu
        self.model = AutoModelForCausalLM.from_pretrained(self.model_path, trust_remote_code=True, device_map=device_map)
        if self.adapter_path != "":
            self.model = peft.PeftModelForCausalLM.from_pretrained(self.model, self.adapter_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
    
    def text_generate(self, input_str: str, max_length: int, temperature: float):
        stop_token_ids = [self.tokenizer.eos_token_id]
        class StopOnTokens(StoppingCriteria):
            def __call__(
                self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs
            ) -> bool:
                for stop_id in stop_token_ids:
                    if input_ids[0][-1] == stop_id:
                        return True
                return False
        input_ids = self.tokenizer.encode(input_str, return_tensors="pt").to(f"cuda:{self.devices[0]}")
        output = self.model.generate(inputs=input_ids, max_length=max_length, temperature=temperature, stopping_criteria=StoppingCriteriaList([StopOnTokens()]))
        return self.tokenizer.decode(output[0], skip_special_tokens=True).removeprefix(input_str)
    
    def start_gradio_app(self):
        try:
            current_cnt = 0
            last_update = datetime.now()
            def count_access():
                nonlocal current_cnt, last_update
                if last_update.day != datetime.now().day:
                    access_counter = DeployAccessCounter(entry_id=self.entry_id, count=current_cnt, date=last_update.date())
                    current_cnt = 0
                    last_update = datetime.now()
                    db_for_counter = get_db()
                    db_for_counter.add(access_counter)
                    db_for_counter.commit()
                    db_for_counter.close()
                current_cnt += 1
            
            def chat(message: str, history: list[list[str]], temperature: float, max_length: int):
                count_access()
                return self.text_generate(message, max_length, temperature)
                
            db = get_db()
            deploy_entry = db.query(DeployEntry).filter(DeployEntry.entry_id == self.entry_id).first()
            deploy_entry.state = 2
            db.commit()
            db.close()
            gr.ChatInterface(
                fn=chat,
                additional_inputs=[
                    gr.Slider(minimum=0, maximum=3.0, step=0.1, value=1.0, label="Temperature"),
                    gr.Slider(minimum=10, maximum=1024, step=1, value=64, label="Max Length")
                ],
            ).launch(server_port=self.port)
        except Exception as e:
            print(e)
            db = get_db()
            deploy_entry = db.query(DeployEntry).filter(DeployEntry.entry_id == self.entry_id).first()
            deploy_entry.state = -1
            db.commit()
            db.close()
    
def terminate_proc(pid: int):
    os.kill(pid, signal.SIGKILL)

class DeploymentManager:

    deploy_id_to_pid: SafeDict[int, int]
    # deploy_id to LLMWrapper
    deployments: SafeDict[int, LLMWrapper]
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeploymentManager, cls).__new__(cls)
        if cls.instance is not None:
            print("DeploymentManager is a singleton class, it will return the same instance every time.")
            return cls.instance
        return cls.instance
    
    def __init__(self):
        self.deploy_id_to_pid = SafeDict()
        self.deployments = SafeDict()
     
    def deploy(self, deploy_id: int):
        #TODO: params not implemented
        if deploy_id in self.deploy_id_to_pid:
            return
        adapter_path = ""
        model_path = ""
        db = get_db()
        deploy_entry = db.query(DeployEntry).filter(DeployEntry.entry_id == deploy_id).first()
        if deploy_entry.deploy_finetuned:
            finetune_entry = db.query(FinetuneEntry).filter(FinetuneEntry.id == deploy_entry.model_or_finetune_id).first()
            model_path = db.query(OpenLLM).filter(OpenLLM.model_id == finetune_entry.model_id).first().local_path
            adapter_path = finetune_entry.output_dir
        else:
            model_path = db.query(OpenLLM).filter(OpenLLM.model_id == deploy_entry.model_or_finetune_id).first().local_path
        deploy_entry.state = 1
        db.commit()
        devcies = deploy_entry.devices
        port = deploy_entry.port
        db.close()
        app = LLMWrapper(model_path, adapter_path, devcies, port, deploy_id)
        self.deployments[deploy_id] = app
        app.load_model()
        proc = ctx.Process(target=app.start_gradio_app)
        if datetime.utcnow() >= deploy_entry.start_time:
            proc.start()
        else:
            delay = (deploy_entry.start_time - datetime.utcnow()).total_seconds()
            start_timer = Timer(delay, proc.start)
            start_timer.start()
        end_timer = Timer((deploy_entry.end_time - datetime.utcnow()).total_seconds(), self.stop, args=(deploy_id,))
        end_timer.start()
        self.deploy_id_to_pid[deploy_id] = proc.pid
  
    def restart(self, entry_id: int):
        if entry_id in self.deploy_id_to_pid:
            self.stop(entry_id)
        self.deploy(entry_id)

    def stop(self, entry_id: int):
        if entry_id not in self.deploy_id_to_pid:
            # which means it was manually stopped
            return
        terminate_proc(self.deploy_id_to_pid[entry_id])
        del self.deploy_id_to_pid[entry_id]
        db = get_db()
        deploy_entry = db.query(DeployEntry).filter(DeployEntry.entry_id == entry_id).first()
        deploy_entry.state = 3
        db.commit()
        db.close()
    
manager = DeploymentManager()