from datetime import datetime
from itertools import chain
import os
import sys
from accelerate.utils.modeling import (
    check_tied_parameters_in_config,
    find_tied_parameters,
)
from backend.enumerate import *
from backend.service.dataset import fetch_dataset
import fire
import psutil
from backend.service.fault import submit_fault
import torch
import transformers
from typing import List, Optional
from datasets import load_dataset
from pandas import DataFrame
from typing import List, Optional, Union, Any, Literal
import datasets
from backend.db import get_db
from backend.tuner.generate_prompt import generate_prompt, get_reference_output
from accelerate import infer_auto_device_map
from backend.service.fault import generate_log_path
from peft import (  # noqa: E402
    AdaLoraConfig,
    AdaptionPromptConfig,
    IA3Config,
    LoraConfig,
    PrefixTuningConfig,
    PromptTuningConfig,
    PromptEncoderConfig,
    LoKrConfig,
    LoHaConfig,
    get_peft_model,
    get_peft_model_state_dict,
    prepare_model_for_kbit_training,
    set_peft_model_state_dict,
)
from peft.utils import TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING
from backend.tuner.callback import ReportCallback
from backend.tuner.get_deepspeed_config import get_deepspeed_config

# peft IA3的参数
# from peft.utils import (
#     TRANSFORMERS_MODELS_TO_IA3_TARGET_MODULES_MAPPING,
#     TRANSFORMERS_MODELS_TO_IA3_FEEDFORWARD_MODULES_MAPPING,
# )
# 增加国产大模型后的常数
TRANSFORMERS_MODELS_TO_IA3_TARGET_MODULES_MAPPING = {
    "t5": ["k", "v", "wo"],
    "mt5": ["k", "v", "wi_1"],
    "gpt2": ["c_attn", "mlp.c_proj"],
    "bloom": ["query_key_value", "mlp.dense_4h_to_h"],
    "roberta": ["key", "value", "output.dense"],
    "opt": ["q_proj", "k_proj", "fc2"],
    "gptj": ["q_proj", "v_proj", "fc_out"],
    "gpt_neox": ["query_key_value", "dense_4h_to_h"],
    "gpt_neo": ["q_proj", "v_proj", "c_proj"],
    "bart": ["q_proj", "v_proj", "fc2"],
    "gpt_bigcode": ["c_attn", "mlp.c_proj"],
    "llama": ["k_proj", "v_proj", "down_proj"],
    "bert": ["key", "value", "output.dense"],
    "deberta-v2": ["key_proj", "value_proj", "output.dense"],
    "deberta": ["in_proj", "output.dense"],
    "chatglm": ["query_key_value", "mlp.dense_4h_to_h"],
    "qwen": ["c_attn", "mlp.c_proj"],
    "baichuan": ["W_pack", "o_project", "down_project"],
    "skywork": ["q_proj", "v_proj", "down_proj"],
    "internlm": ["q_proj", "v_proj", "down_proj"],
    "xverse": ["q_proj", "v_proj", "down_proj"],
    "mistral": ["k_proj", "v_proj", "down_proj"],
    "internlm": ["q_proj", "v_proj", "down_proj"],
    "gemma": ["q_proj", "v_proj", "down_proj"],
}
TRANSFORMERS_MODELS_TO_IA3_FEEDFORWARD_MODULES_MAPPING = {
    "t5": ["wo"],
    "mt5": [],
    "gpt2": ["mlp.c_proj"],
    "bloom": ["mlp.dense_4h_to_h"],
    "roberta": ["output.dense"],
    "opt": ["fc2"],
    "gptj": ["fc_out"],
    "gpt_neox": ["dense_4h_to_h"],
    "gpt_neo": ["c_proj"],
    "bart": ["fc2"],
    "gpt_bigcode": ["mlp.c_proj"],
    "llama": ["down_proj"],
    "bert": ["output.dense"],
    "deberta-v2": ["output.dense"],
    "deberta": ["output.dense"],
    "chatglm": ["mlp.dense_4h_to_h"],
    "qwen": ["mlp.c_proj"],
    "baichuan": ["down_project"],
    "skywork": ["down_proj"],
    "internlm": ["down_proj"],
    "xverse": ["down_proj"],
    "mistral": ["down_proj"],
    "gemma": ["down_proj"],
}
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    LlamaTokenizer,
    AutoModel,
    BitsAndBytesConfig,
)
from accelerate import Accelerator
from trl import SFTTrainer
from dataclasses import dataclass, field
import bitsandbytes as bnb


def get_target(bnb_config: Optional[BitsAndBytesConfig], named_modules) -> List[str]:
    # Determine the correct linear layer class based on the value of `args.bits`
    if bnb_config is not None and bnb_config.load_in_4bit:
        cls = bnb.nn.Linear4bit
    elif bnb_config is not None and bnb_config.load_in_8bit:
        cls = bnb.nn.Linear8bitLt
    else:
        cls = torch.nn.Linear

    lora_module_names = set()
    for name, module in named_modules:
        # Check if the current module is an instance of the linear layer class
        if isinstance(module, cls):
            # If yes, split the name of the module into its component parts and add the first or last part to the set
            names = name.split(".")
            lora_module_names.add(names[0] if len(names) == 1 else names[-1])

    # Remove 'lm_head' from the set if present (needed for 16-bit)
    if "lm_head" in lora_module_names:
        lora_module_names.remove("lm_head")
    return list(lora_module_names)


def get_device_map(devices: list[int] | str, base_model: str):
    return "auto"


def get_peft_config(
    model: AutoModelForCausalLM,
    bnb_config: BitsAndBytesConfig,
    adapter_name: str,
    lora_r: int,
    lora_alpha: int,
    lora_dropout: float,
    num_virtual_tokens: int,
):
    target_modules = []
    if (
        model.config.model_type.lower()
        in TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING
    ):
        target_modules = TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING[
            model.config.model_type.lower()
        ]
    elif any(n in adapter_name.lower() for n in ["adalora", "lora", "lokr", "loha"]):
        target_modules = get_target(bnb_config, model.named_modules())

    if adapter_name == "adalora":
        return AdaLoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=target_modules,
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
        )
    # this is only for llama, not for general use, so abandon it
    # elif adapter_name == "adaption-prompt":
    #     return AdaptionPromptConfig(
    #         task_type="CAUSAL_LM",
    #     )
    elif adapter_name == "IA3":
        return IA3Config(
            target_modules=TRANSFORMERS_MODELS_TO_IA3_TARGET_MODULES_MAPPING[
                model.config.model_type.lower()
            ],
            feedforward_modules=TRANSFORMERS_MODELS_TO_IA3_FEEDFORWARD_MODULES_MAPPING[
                model.config.model_type.lower()
            ],
            task_type="CAUSAL_LM",
        )
    elif adapter_name == "lora" or adapter_name == "lomo-lora":
        return LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=target_modules,
            inference_mode=False,
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
        )
    elif adapter_name == "prefix-tuning":
        return PrefixTuningConfig(
            num_virtual_tokens=num_virtual_tokens,
            task_type="CAUSAL_LM",
        )
    elif adapter_name == "prompt-tuning":
        return PromptTuningConfig(
            num_virtual_tokens=num_virtual_tokens,
            task_type="CAUSAL_LM",
        )
    elif adapter_name == "p-tuning":
        return PromptEncoderConfig(
            num_virtual_tokens=num_virtual_tokens,
            task_type="CAUSAL_LM",
        )
    elif adapter_name == "lokr":
        return LoKrConfig(
            r=lora_r,
            alpha=lora_alpha,
            target_modules=target_modules,
            task_type="CAUSAL_LM",
        )
    elif adapter_name == "loha":
        return LoHaConfig(
            r=lora_r,
            alpha=lora_alpha,
            target_modules=target_modules,
            task_type="CAUSAL_LM",
        )
    else:
        raise ValueError(f"Unknown adapter name: {adapter_name}")


def get_model_and_tokenizer(
    base_model: str,
    device_map: Any,
    bnb_config: BitsAndBytesConfig,
    zero_optimization: bool,
    zero_stage: int,
    zero_offload: bool,
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    model, tokenizer = None, None
    if zero_optimization:
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16,
            device_map=device_map,
            trust_remote_code=True,
            quantization_config=bnb_config,
        )
        tokenizer = AutoTokenizer.from_pretrained(
            base_model, trust_remote_code=True, use_fast=True
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            device_map=device_map,
            trust_remote_code=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(
            base_model, trust_remote_code=True, use_fast=True
        )
    if tokenizer.__class__.__name__ == "QWenTokenizer":
        tokenizer.pad_token_id = tokenizer.eod_id
        tokenizer.bos_token_id = tokenizer.eod_id
        tokenizer.eos_token_id = tokenizer.eod_id
    elif tokenizer.__class__.__name__ != "ChatGLMTokenizer":
        tokenizer.pad_token_id = (
            tokenizer.eos_token_id
            if tokenizer.pad_token_id is None
            else tokenizer.pad_token_id
        )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = "<pad>"
        tokenizer.pad_token_id = 0
    return model, tokenizer


def get_dataset(
    dataset_type: int,
    dataset: list,
    val_size: float,
    tokenizer: AutoTokenizer,
    cutoff_len: int,
    callback: ReportCallback,
    output_dir: str,
):
    def tokenize(prompt, add_eos_token=True):
        result = tokenizer(
            prompt,
            truncation=True,
            max_length=cutoff_len,
            padding=False,
            return_tensors=None,
        )
        if (
            result["input_ids"][-1] != tokenizer.eos_token_id
            and len(result["input_ids"]) < cutoff_len
            and add_eos_token
        ):
            result["input_ids"].append(tokenizer.eos_token_id)
            if "chatglm" not in tokenizer.__class__.__name__.lower():
                result["attention_mask"].append(1)

        result["labels"] = result["input_ids"].copy()

        if "chatglm" in tokenizer.__class__.__name__.lower():
            return {"input_ids": result["input_ids"], "labels": result["labels"]}
        else:
            return result

    def generate_and_tokenize_prompt(data_point):
        full_prompt = generate_prompt(data_point, dataset_type)
        tokenized_full_prompt = tokenize(full_prompt)
        user_prompt = generate_prompt({**data_point, "output": ""}, dataset_type, for_infer=True)
        tokenized_user_prompt = tokenize(user_prompt, add_eos_token=True)
        user_prompt_len = len(tokenized_user_prompt["input_ids"])
        tokenized_full_prompt["labels"] = [
            -100
        ] * user_prompt_len + tokenized_full_prompt["labels"][
            user_prompt_len:
        ]
        return tokenized_full_prompt
    
    if dataset_type > 1 and len(dataset) > 0:
        data = datasets.DatasetDict(
            {"train": dataset}
        )
    else:
        df = DataFrame(dataset)
        data = datasets.DatasetDict(
            {"train": datasets.Dataset.from_dict(df.to_dict("list"))}
        )
    
    # df = DataFrame(dataset).astype(str)
    # data = datasets.DatasetDict(
    #     {"train": datasets.Dataset.from_dict(df.to_dict("list"))}
    # )

    val_size = 0 if val_size == 0 else max(int(val_size * len(data["train"])), 2)

    text_train_data = None
    text_val_data = None

    if val_size > 0:
        train_val = data["train"].train_test_split(
            test_size=val_size, shuffle=True, seed=42
        )
        callback.set_eval_dataset(train_val["test"])
        train_val["test"].to_json(os.path.join(output_dir, "eval_dataset.json"))
        text_train_data = train_val["train"].shuffle()
        text_val_data = train_val["test"].shuffle()
        train_data = train_val["train"].shuffle().map(generate_and_tokenize_prompt)
        val_data = train_val["test"].shuffle().map(generate_and_tokenize_prompt)
    else:
        train_data = data["train"].shuffle().map(generate_and_tokenize_prompt)
        text_train_data = data["train"].shuffle()
        val_data = None
    return train_data, val_data, text_train_data, text_val_data


def train(
    # model params 模型参数
    base_model: str = "/data/yimin/model/bloom-800m-zh",
    dataset_type: int = 0,
    dataset: list = [],
    devices: list[int] | str = "auto",
    report_callback: ReportCallback = None,
    output_dir: str = "./test",
    adapter_name: str = "lora",
    # training hyperparams  训练超参数
    batch_size: int = 128,
    micro_batch_size: int = 4,
    num_epochs: int = 3,
    learning_rate: float = 3e-4,
    cutoff_len: int = 256,
    val_set_size: float = 0,
    use_gradient_checkpointing: bool = False,
    eval_step: int = 200,
    save_step: int = 200,
    logging_step: int = 10,
    # lora hyperparams  lora方法超参数
    lora_r: int = 8,
    lora_alpha: int = 16,
    lora_dropout: float = 0.05,
    # target_modules: List[str] = None,       
    # prefix tuning hyperparams prefix tuning方法的超参数
    num_virtual_tokens: int = 30,
    # llm hyperparams   大模型超参数
    train_on_inputs: bool = True,
    group_by_length: bool = False,
    # wandb params      项目可视化的参数
    wandb_project: str = "",
    wandb_run_name: str = "",
    wandb_watch: str = "",
    wandb_log_model: str = "",
    resume_from_checkpoint: str = None,
    # bits and bytes params     量化的参数
    bits_and_bytes: bool = False,
    load_8bit: bool = False,
    load_4bit: bool = False,
    llm_int8_threshold: float = 6.0,  
    llm_int8_skip_modules: Any = None,
    llm_int8_enable_fp32_cpu_offload: bool = False,
    llm_int8_has_fp16_weight: bool = False,
    # bnb_4bit_compute_dtype: Any | None = None,
    bnb_4bit_compute_dtype: Any = None,
    bnb_4bit_quant_type: str = "fp4",
    bnb_4bit_use_double_quant: bool = False,
    zero_optimization: bool = True,
    zero_stage: int = 2,
    zero_offload: bool = False,
    eval_indexes: list[str] | None = None
):
    torch.cuda.empty_cache()

    gradient_accumulation_steps = batch_size // micro_batch_size
    device_map = None

    if not zero_optimization:
        device_map = get_device_map(devices, "")

    bnb_config = None
    if bits_and_bytes:
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=load_8bit,
            load_in_4bit=load_4bit,
            llm_int8_threshold=llm_int8_threshold,
            llm_int8_skip_modules=llm_int8_skip_modules,
            llm_int8_enable_fp32_cpu_offload=llm_int8_enable_fp32_cpu_offload,
            llm_int8_has_fp16_weight=llm_int8_has_fp16_weight,
            bnb_4bit_compute_dtype=bnb_4bit_compute_dtype,
            bnb_4bit_quant_type=bnb_4bit_quant_type,
            bnb_4bit_use_double_quant=bnb_4bit_use_double_quant,
        )

    model, tokenizer = get_model_and_tokenizer(
        base_model, device_map, bnb_config, zero_optimization, zero_stage, zero_offload
    )
    
    optim_dict = {
        "lomo": "lomo",
        "lomo-ada": "adalomo",
        "galore": "galore_adamw",
    }
    use_peft = not adapter_name in optim_dict.keys()

    if use_peft:
        model = get_peft_model(
            model,
            get_peft_config(
                model,
                bnb_config,
                adapter_name,
                lora_r,
                lora_alpha,
                lora_dropout,
                num_virtual_tokens,
            ),
        )
        model.print_trainable_parameters()

    if bits_and_bytes:
        model = prepare_model_for_kbit_training(
            model, use_gradient_checkpointing=use_gradient_checkpointing
        )

    if use_peft:
        model.print_trainable_parameters()  # Be more transparent about the % of trainable params.

    if torch.cuda.device_count() > 1:
        # keeps Trainer from trying its own DataParallelism when more than 1 gpu is available
        model.is_parallelizable = True
        model.model_parallel = True

    train_data, val_data, _a, _b= get_dataset(
        dataset_type,
        dataset,
        val_set_size,
        tokenizer,
        cutoff_len,
        report_callback,
        output_dir,
    )

    data_collator = transformers.DataCollatorForSeq2Seq(
        tokenizer, model=model, return_tensors="pt", padding=True, pad_to_multiple_of=16
    )
    
    
    optim = "adamw_torch" if not adapter_name in optim_dict.keys() else optim_dict[adapter_name]
    if optim.startswith("galore"):
        galore_params = {
            "optim_target_modules": [r".*.attn.*", r".*.mlp.*"],
            "optim_args": "rank=128, update_proj_gap=100, scale=0.1",
        }
    else:
        galore_params = {}


    training_args = transformers.TrainingArguments(
        per_device_train_batch_size=micro_batch_size,
        per_device_eval_batch_size=micro_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        warmup_steps=100,
        num_train_epochs=num_epochs,
        learning_rate=learning_rate,
        fp16=False,
        bf16=True,
        logging_steps=logging_step,
        optim=optim,
        evaluation_strategy="steps" if val_set_size > 0 else "no",
        save_strategy="steps",
        eval_steps=eval_step if val_set_size > 0 else None,
        save_steps=save_step,
        output_dir=output_dir,
        save_total_limit=15,
        load_best_model_at_end=False,
        group_by_length=group_by_length,
        report_to=None,
        run_name=None,
        deepspeed=(
            None
            if not zero_optimization
            else get_deepspeed_config(zero_stage, zero_offload)
        ),
        **galore_params,
    )
    # from backend.tuner.metrics import get_compute_metrics_func
    # compute_metrics = get_compute_metrics_func(eval_indexes, tokenizer)
    trainer = transformers.Trainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_data,
        eval_dataset=val_data,
        callbacks=[report_callback],
        args=training_args,
        data_collator=data_collator,
    )
    # Currently pytorch requires python <= 3.10
    if (
        torch.__version__ >= "2"
        and sys.platform != "win32"
        and sys.version_info[0] == 3
        and sys.version_info[1] <= 10
    ):
        model = torch.compile(model)

    trainer.train(resume_from_checkpoint=resume_from_checkpoint)
    model.save_pretrained(output_dir)
    # session_name = f"{TaskType.finetune.value}_task_{entry.id}"
    # base_dir = os.path.join(os.environ.get("FINETUNE_OUTPUT"), identifier, session_name)
    # full_path = os.path.abspath(base_dir)
    # entry.output_dir = full_path


from backend.models import *


def wrapper(
    finetune_id: int,
):
    try:
        db = get_db()
        entry = db.query(FinetuneEntry).filter(FinetuneEntry.id == finetune_id).first()
        owner = entry.owner
        public = entry.public
        base_model = db.query(OpenLLM).filter(OpenLLM.id == entry.model_id).first()
        model_path = base_model.local_path
        dataset_json_obj, dataset_type = fetch_dataset(entry.dataset_id, 1)
        callback = ReportCallback(
            finetune_id,
            dataset_type,
            entry.eval_indexes,
            owner,
            public,
            entry.name,
            entry.description,
            base_model.model_name,
        )
        train(
            base_model=model_path,
            dataset_type=dataset_type,
            dataset=dataset_json_obj,
            devices="auto",
            report_callback=callback,
            output_dir=entry.output_dir,
            adapter_name=entry.adapter_name,
            batch_size=entry.batch_size,
            micro_batch_size=entry.micro_batch_size,
            num_epochs=entry.num_epochs,
            learning_rate=entry.learning_rate,
            cutoff_len=entry.cutoff_len,
            val_set_size=entry.val_set_size,
            use_gradient_checkpointing=entry.use_gradient_checkpointing,
            eval_step=entry.eval_step,
            save_step=entry.save_step,
            logging_step=entry.logging_step,
            lora_r=entry.lora_r,
            lora_alpha=entry.lora_alpha,
            lora_dropout=entry.lora_dropout,
            num_virtual_tokens=entry.num_virtual_tokens,
            train_on_inputs=entry.train_on_inputs,
            group_by_length=entry.group_by_length,
            # wandb_project=entry.wandb_project,
            # wandb_run_name=entry.wandb_run_name,
            # wandb_watch=entry.wandb_watch,
            # wandb_log_model=entry.wandb_log_model,
            # resume_from_checkpoint=entry.resume_from_checkpoint,
            bits_and_bytes=entry.bits_and_bytes,
            load_8bit=entry.load_8bit,
            load_4bit=entry.load_4bit,
            llm_int8_threshold=entry.llm_int8_threshold,
            # llm_int8_skip_modules=entry.llm_int8_skip_modules,
            llm_int8_enable_fp32_cpu_offload=entry.llm_int8_enable_fp32_cpu_offload,
            llm_int8_has_fp16_weight=entry.llm_int8_has_fp16_weight,
            bnb_4bit_compute_dtype=entry.bnb_4bit_compute_dtype,
            bnb_4bit_quant_type=entry.bnb_4bit_quant_type,
            bnb_4bit_use_double_quant=entry.bnb_4bit_use_double_quant,
            zero_optimization=entry.zero_optimization,
            zero_stage=entry.zero_stage,
            zero_offload=entry.zero_offload,
            eval_indexes=entry.eval_indexes,
        )
    except RuntimeError as e:
        if "cuda out of memory" in str(e).lower():
            db = get_db()
            entry = db.query(FinetuneEntry).filter(FinetuneEntry.id == finetune_id).first()
            entry.state = FinetuneState.error.value
            entry.end_time = datetime.utcnow()
            db.commit()
            submit_fault(
                [TaskType.finetune.value, str(finetune_id)],
                str(e),
                FaultCode.cuda_oom.value,
                entry.owner,
                False,
                generate_log_path(TaskType.finetune.value, entry.id),
            )
            db.close()
        elif "rtx 4000 series" in str(e).lower():
            db = get_db()
            entry = db.query(FinetuneEntry).filter(FinetuneEntry.id == finetune_id).first()
            entry.state = FinetuneState.error.value
            entry.end_time = datetime.utcnow()
            db.commit()
            submit_fault(
                [TaskType.finetune.value, str(finetune_id)],
                str(e),
                FaultCode.nccl_issue.value,
                entry.owner,
                False,
                generate_log_path(TaskType.finetune.value, entry.id),
            )
            db.close()
        else:
            db = get_db()
            entry = db.query(FinetuneEntry).filter(FinetuneEntry.id == finetune_id).first()
            entry.state = FinetuneState.error.value
            entry.end_time = datetime.utcnow()
            db.commit()
            submit_fault(
                [TaskType.finetune.value, str(finetune_id)],
                str(e),
                FaultCode.other.value,
                entry.owner,
                False,
                generate_log_path(TaskType.finetune.value, entry.id),
            )
    except Exception as e:
        import traceback
        print(
            traceback.format_exc()
        )
        db = get_db()
        entry = db.query(FinetuneEntry).filter(FinetuneEntry.id == finetune_id).first()
        entry.state = FinetuneState.error.value
        entry.end_time = datetime.utcnow()
        db.commit()
        submit_fault(
            [TaskType.finetune.value, str(finetune_id)],
            str(e),
            FaultCode.other.value,
            entry.owner,
            False,
            generate_log_path(TaskType.finetune.value, entry.id),
        )
        db.close()


if __name__ == "__main__":
    fire.Fire(wrapper)