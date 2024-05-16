from backend.enumerate import FaultCode
from fire import Fire
from backend.db import get_db
from backend.models import *
from backend.llmw import LLMW
import gradio as gr
from backend.enumerate import DeploymentState
from backend.service.fault import *
from backend.enumerate import *
from vllm import SamplingParams


def run(deployment_id: int):
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
    use_vllm = entry.use_vllm
    port = entry.port

    llmw = None
    if deploy_base_model:
        model = db.query(OpenLLM).filter(OpenLLM.id == model_or_adapter_id).first()
        llmw = LLMW(model.local_path, None, use_vllm=use_vllm, use_deepspeed=use_deepspeed)
    else:
        adapter = db.query(Adapter).filter(Adapter.id == model_or_adapter_id).first()
        base_model = (
            db.query(OpenLLM)
            .filter(OpenLLM.model_name == adapter.base_model_name)
            .first()
        )
        if use_vllm and db.query(FinetuneEntry).filter(
            FinetuneEntry.id == adapter.ft_entry
        ).first().adapter_name != "lora":
            raise Exception("VLLM can only be used with LORA adapters")
        llmw = LLMW(base_model.local_path, adapter.local_path, use_vllm=use_vllm, use_deepspeed=use_deepspeed)
    llmw.load()

    entry.state = DeploymentState.running.value
    db.commit()
    db.close()

    def transformers_simple_generate(prompt: str, max_length: int) -> str:
        return llmw.transformers_simple_text_generation(prompt, max_length)
    
    def transformers_advanced_generate(prompt: str, 
            max_length: int = 20, 
            max_new_tokens: int = 20,
            min_length: int = 0,
            min_new_tokens: int = None,
            do_sample: bool = False, 
            num_beams: int = 1,
            num_beam_groups: int = 1,
            use_cache: bool = True,
            temperature: float = 1.0, 
            top_k: int = 50, 
            top_p: float = 1.0, 
            typical_p: float = 1.0,
        ) -> str:
        return llmw.transformers_advanced_text_generation(prompt, max_length, max_new_tokens, min_length, min_new_tokens, "never", None, do_sample, num_beams, num_beam_groups, use_cache, temperature, top_k, top_p, typical_p)

    def vllm_simple_generate(prompt: str, max_length: int) -> str:
        return llmw.vllm_simple_generation(prompt, max_length)

    def vllm_advanced_generate(
        prompt: str, 
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        repetition_penalty: float = 1.0,
        temperature: float = 1.0,
        top_p: float = 1.0,
        top_k: int = -1,
        min_p: float = 0.0,
        seed: int = None,
        use_beam_search: bool = False,
        length_penalty: float = 1.0,
        max_tokens: int = 16,
        min_tokens: int = 0,
    )-> str:
        sampling_params = {
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "repetition_penalty": repetition_penalty,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "min_p": min_p,
            "seed": seed,
            "use_beam_search": use_beam_search,
            "length_penalty": length_penalty,
            "max_tokens": max_tokens,
            "min_tokens": min_tokens,
        }
        return llmw.vllm_advanced_generation(prompt, sampling_params)

    transformers_simple_generate_iface = gr.Interface(
        fn=transformers_simple_generate, 
        inputs=[
            gr.Text(value="", label="Prompt"),  # Set value text
            gr.Number(value=128, label="Max new tokens"),  # Set value number
        ], 
        outputs="text",
        api_name="simple"
    )
    transformers_advanced_generate_iface = gr.Interface(
        fn=transformers_advanced_generate, 
        inputs=[
            gr.Textbox(value="", label="prompt"),  # Set default text
            gr.Slider(minimum=1, maximum=512, value=20, label="max_length"),  # Set default number
            gr.Slider(minimum=0, maximum=512, value=20, label="max_new_tokens"),  # Set default number
            gr.Slider(minimum=0, maximum=512, value=0, label="min_length"),  # Set default number
            gr.Slider(minimum=0, maximum=512, value=None, label="min_new_tokens"),  # Set default number
            gr.Checkbox(value=False, label="do_sample"),  # Set default checkbox
            gr.Slider(minimum=1, maximum=512, value=1, label="num_beams"),  # Set default number
            gr.Slider(minimum=1, maximum=512, value=1, label="num_beam_groups"),  # Set default number
            gr.Checkbox(value=True, label="use_cache"),  # Set default checkbox
            gr.Slider(minimum=0.0, maximum=1.0, value=1.0, label="temperature"),  # Set default number
            gr.Slider(minimum=0, maximum=512, value=50, label="top_k"),  # Set default number
            gr.Slider(minimum=0.0, maximum=1.0, value=1.0, label="top_p"),  # Set default number
            gr.Slider(minimum=0.0, maximum=1.0, value=1.0, label="typical_p"),  # Set default number
        ], 
        outputs="text",
        api_name="advanced"
    )

    vllm_simple_generate_iface = gr.Interface(
        fn=vllm_simple_generate, 
        inputs=[
            gr.Text(value="", label="Prompt"),  # Set value text
            gr.Number(value=128, label="Max new tokens"),  # Set value number
        ], 
        outputs="text",
        api_name="simple"
    )
    
    vllm_advanced_generate_iface = gr.Interface(
        fn=vllm_advanced_generate, 
        inputs=[
            gr.Textbox(value="", label="prompt"),  # Set default text
            gr.Slider(minimum=0.0, maximum=1.0, value=0.0, label="presence_penalty"),  # Set default number
            gr.Slider(minimum=0.0, maximum=1.0, value=0.0, label="frequency_penalty"),  # Set default number
            gr.Slider(minimum=0.0, maximum=1.0, value=1.0, label="repetition_penalty"),  # Set default number
            gr.Slider(minimum=0.0, maximum=1.0, value=1.0, label="temperature"),  # Set default number
            gr.Slider(minimum=0.0, maximum=1.0, value=1.0, label="top_p"),  # Set default number
            gr.Slider(minimum=-1, maximum=512, value=-1, label="top_k"),  # Set default number
            gr.Slider(minimum=0.0, maximum=1.0, value=0.0, label="min_p"),  # Set default number
            gr.Slider(minimum=0, maximum=512, value=None, label="seed"),  # Set default number
            gr.Checkbox(value=False, label="use_beam_search"),  # Set default checkbox
            gr.Slider(minimum=0.0, maximum=1.0, value=1.0, label="length_penalty"),  # Set default number
            gr.Slider(minimum=1, maximum=512, value=16, label="max_tokens"),  # Set default number
            gr.Slider(minimum=0, maximum=512, value=0, label="min_tokens"),  # Set default number
        ], 
        outputs="text",
        api_name="advanced"
    )

    valid_ifaces = []
    ifaces_name = []
    
    if not use_vllm:
        valid_ifaces = [
            transformers_simple_generate_iface,
            transformers_advanced_generate_iface
        ]
        ifaces_name = [
            "Simple Text Generation",
            "Advanced Text Generation"
        ]
    else:
        valid_ifaces = [
            vllm_simple_generate_iface,
            vllm_advanced_generate_iface
        ]
        ifaces_name = [
            "Simple Text Generation",
            "Advanced Text Generation"
        ]

    gr.TabbedInterface(valid_ifaces, ifaces_name).launch(
        share=False, server_port=port, server_name="0.0.0.0", root_path=f"/net/{port}/"
    )


def wrapper(deployment_id: int):
    try:
        run(deployment_id)
    except RuntimeError as e:
        if "cuda out of memory" in str(e).lower():
            db = get_db()
            entry = db.query(Deployment).filter(Deployment.id == deployment_id).first()
            entry.state = DeploymentState.error.value
            db.commit()
            submit_fault(
                [TaskType.deployment.value, str(deployment_id)],
                str(e),
                FaultCode.cuda_oom.value,
                entry.owner,
                False,
                generate_log_path(TaskType.deployment.value, str(deployment_id)),
            )
        else:
            raise e
    except Exception as e:
        db = get_db()
        entry = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        entry.state = DeploymentState.error.value
        db.commit()
        submit_fault(
            [TaskType.deployment.value, str(deployment_id)],
            str(e),
            FaultCode.other.value,
            entry.owner,
            False,
            generate_log_path(TaskType.deployment.value, str(deployment_id)),
        )


if __name__ == "__main__":
    Fire(wrapper)
