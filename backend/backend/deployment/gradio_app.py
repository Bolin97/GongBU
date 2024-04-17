from fire import Fire
from backend.db import get_db
from backend.models import *
from backend.llmw import LLMW
import gradio as gr

def run(
    deployment_id: int
):
    db = get_db()
    
    entry = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    
    deploy_base_model = entry.deploy_base_model
    model_or_adapter_id = entry.model_or_adapter_id
    bits_and_bytes = entry.bits_and_bytes
    load_8bit = entry.load_8bit
    load_4bit = entry.load_4bit
    use_flash_attention = entry.use_flash_attention
    use_deepspeed = entry.use_deepspeed
    devices = entry.devices
    port = entry.port
    
    llmw = None
    if deploy_base_model:
        model = db.query(OpenLLM).filter(OpenLLM.id == model_or_adapter_id).first()
        llmw = LLMW(model.local_path, None)
    else:
        adapter = db.query(Adapter).filter(Adapter.id == model_or_adapter_id).first()
        base_model = db.query(OpenLLM).filter(OpenLLM.model_name == adapter.base_model_name).first()
        llmw = LLMW(base_model.local_path, adapter.local_path)
    llmw.load()

    entry.state = 2
    db.commit()
    db.close()
    
    
    def generate(prompt: str, max_length: int) -> str:
        return llmw.simple_text_generation(prompt, max_length)

    iface = gr.Interface(fn=generate, inputs=["text", "number"], outputs="text")
    iface.launch(share=False, server_port=port, server_name="0.0.0.0", root_path=f"/net/{port}/")
    
if __name__ == "__main__":
    Fire(run)