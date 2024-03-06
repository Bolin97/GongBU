import os
import sys
from accelerate.utils.modeling import check_tied_parameters_in_config, find_tied_parameters
import fire
import psutil
import torch
import transformers
from typing import List, Optional
from datasets import load_dataset
from pandas import DataFrame
from typing import List, Optional, Union, Any, Literal
from .callback import ReportCallback
import datasets
import json
from .generate_prompt import generate_prompt
from accelerate import infer_auto_device_map
from peft import (  # noqa: E402
    AdaLoraConfig,
    AdaptionPromptConfig,
    IA3Config,
    LoraConfig,
    PrefixTuningConfig,
    PromptTuningConfig,
    PromptEncoderConfig,
    get_peft_model,
    get_peft_model_state_dict,
    prepare_model_for_kbit_training,
    set_peft_model_state_dict,
)
from peft.utils import TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING

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
}
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    LlamaTokenizer,
    AutoModel,
    BitsAndBytesConfig,
)  # noqa: F402
from accelerate import Accelerator

from dataclasses import dataclass, field

# from simpletuning.constants import *
import bitsandbytes as bnb


# 得到模型的linear层
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
            # 只保留最后的名称，前缀不保留
            lora_module_names.add(names[0] if len(names) == 1 else names[-1])

    # Remove 'lm_head' from the set if present (needed for 16-bit)
    if "lm_head" in lora_module_names:
        lora_module_names.remove("lm_head")

    # Convert the set into a list and return it
    return list(lora_module_names)


def train(
    # model params 模型参数
    base_model: str = "/data/yimin/model/bloom-800m-zh",  # 模型(绝对)路径 # the only required argument
    dataset_type: int = 0,
    dataset: list = [],
    devices: list[int] | str = [0],
    report_callback: ReportCallback = None,
    output_dir: str = "./test",  # 输出文件夹
    adapter_name: str = "lora",  # 微调方法
    # training hyperparams  训练超参数
    batch_size: int = 128,  # 单次训练数据样本个数
    micro_batch_size: int = 4,  # 每次流水并行的训练样本个数
    num_epochs: int = 3,  # 训练迭代次数
    learning_rate: float = 3e-4,  # 学习率
    cutoff_len: int = 256,  # 文本最大长度
    val_set_size: float = 0,  # 评估数据集的大小
    use_gradient_checkpointing: bool = False,  # 是否使用梯度检查点
    eval_step: int = 200,  # 评估步数间隔
    save_step: int = 200,  # 保存步数间隔
    logging_step: int = 10,
    # lora hyperparams  lora方法超参数
    lora_r: int = 8,  # lora的秩
    lora_alpha: int = 16,  # lora对模型效果的贡献度
    lora_dropout: float = 0.05,  # lora剪枝率
    # target_modules: List[str] = None,       # 目标模块(使用lora优化的矩阵乘法的linear模块，可以从model的named_modules中获取，)
    # prefix tuning hyperparams prefix tuning方法的超参数
    num_virtual_tokens: int = 30,  # 虚拟tokens长度
    # llm hyperparams   大模型超参数
    train_on_inputs: bool = True,  # 是否使用输入进行训练
    group_by_length: bool = False,  # 是否使用adafactor优化算法
    # wandb params      项目可视化的参数
    wandb_project: str = "",
    wandb_run_name: str = "",
    wandb_watch: str = "",  # options: false | gradients | all
    wandb_log_model: str = "",  # options: false | true
    resume_from_checkpoint: str = None,  # either training checkpoint or final adapter
    # bits and bytes params     量化的参数
    bits_and_bytes: bool = False,  # 是否量化
    load_8bit: bool = False,  # 8bit量化
    load_4bit: bool = False,  # 4bit量化
    llm_int8_threshold: float = 6.0,  # LLM.int8()方法的量化阈值：绝对值低于这个值正常量化，绝对值高于阈值的‘离群特征’保留其原来精度
    # 这个参数的设置可能会影响模型的推断速度和精度
    # 较低的阈值可能会导致更多的值被量化为整数，从而降低内存使用和加速推断，但可能会牺牲一些模型的精度
    # 较高的阈值可能会保留更多的精度，但可能会增加内存使用和推断时间
    # 具体的最佳阈值设置取决于模型的具体架构、任务、精度要求以及硬件环境等因素。
    # llm_int8_skip_modules: Any | None = None,
    llm_int8_skip_modules: Any = None,  # 不转换为8位的模块，以确保稳定性。例如“llm_head”
    llm_int8_enable_fp32_cpu_offload: bool = False,  # 允许使用CPU进行fp32的卸载，可是将模型分别装载在cpu和gpu上，例如如下代码：
    # 将lm_head装入cpu
    # device_map = {
    # "transformer.word_embeddings": 0,
    # "transformer.word_embeddings_layernorm": 0,
    # "lm_head": "cpu",
    # "transformer.h": 0,
    # "transformer.ln_f": 0,
    # }
    llm_int8_has_fp16_weight: bool = False,  # 使用fp16旬行LLM.int8()
    # bnb_4bit_compute_dtype: Any | None = None,
    bnb_4bit_compute_dtype: Any = None,  # 设置计算类型
    bnb_4bit_quant_type: str = "fp4",  # 设置量化类型：fp4或nf4，默认是fp4
    bnb_4bit_use_double_quant: bool = False,  # 是否开启二次量化
):
    torch.cuda.empty_cache()
    # 梯度累积步数
    gradient_accumulation_steps = batch_size // micro_batch_size
    device_map = {}
    if devices == "auto":
        device_map = "auto"
    else:
        model_on_cpu = AutoModelForCausalLM.from_pretrained(
            base_model, trust_remote_code=True, device_map={"": "cpu"}
        )
        distribution = {
            each: int(torch.cuda.get_device_properties(each).total_memory - torch.cuda.memory_allocated(each) - torch.cuda.memory_reserved(each)) * 0.8 - 5 * (10 ** 9)
            for each in devices
        }
        distribution.update({"cpu": psutil.virtual_memory().available})
        device_map = infer_auto_device_map(
            model_on_cpu,
            distribution,
            no_split_module_classes=type(model_on_cpu)._no_split_modules
        )
        del model_on_cpu
        # device_map = "auto"
    use_wandb = len(wandb_project) > 0 or (
        "WANDB_PROJECT" in os.environ and len(os.environ["WANDB_PROJECT"]) > 0
    )

    acc = Accelerator()
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
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16,
            device_map=device_map,
            trust_remote_code=True,
            quantization_config=bnb_config,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16,
            device_map=device_map,
            trust_remote_code=True,
        )
    if (
        model.config.model_type.lower()
        in TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING
    ):
        target_modules = TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING[
            model.config.model_type.lower()
        ]
    elif any(n in adapter_name.lower() for n in ["lora"]):
        target_modules = get_target(bnb_config, model.named_modules())
    #

    # tokenizer
    if model.config.model_type.lower() == "llama":
        # Due to the name of transformers' LlamaTokenizer, we have to do this
        tokenizer = LlamaTokenizer.from_pretrained(base_model)
    else:
        tokenizer = AutoTokenizer.from_pretrained(
            base_model, trust_remote_code=True, use_fast=True
        )

    model, tokenizer = acc.prepare(model, tokenizer)

    # QWenTokenizer比较特殊，pad_token_id、bos_token_id、eos_token_id均为None。eod_id对应的token为<|endoftext|>
    if tokenizer.__class__.__name__ == "QWenTokenizer":
        tokenizer.pad_token_id = tokenizer.eod_id
        tokenizer.bos_token_id = tokenizer.eod_id
        tokenizer.eos_token_id = tokenizer.eod_id
    # ChatGLMTokenizer不需要设置，仅设置其他tokenizer
    elif tokenizer.__class__.__name__ != "ChatGLMTokenizer":
        # assert tokenizer.eos_token_id is not None
        # assert tokenizer.bos_token_id is not None
        tokenizer.pad_token_id = (
            tokenizer.eos_token_id
            if tokenizer.pad_token_id is None
            else tokenizer.pad_token_id
        )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = "<pad>"
        tokenizer.pad_token_id = 0
    # tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})
    # if not any(n not in model.config.model_type.lower() for n in ["qwen", "chatglm"]):
    #     tokenizer.pad_token_id = (
    #         0  # unk. we want this to be different from the eos token
    #     )
    #     tokenizer.padding_side = "left"  # Allow batched inference

    def tokenize(prompt, add_eos_token=True):
        # there's probably a way to do this with the tokenizer settings
        # but again, gotta move fast
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
            if "chatglm" not in base_model:
                result["attention_mask"].append(1)

        result["labels"] = result["input_ids"].copy()

        if "chatglm" in base_model:
            return {"input_ids": result["input_ids"], "labels": result["labels"]}
        else:
            return result

    def generate_and_tokenize_prompt(data_point):
        full_prompt = generate_prompt(data_point)
        tokenized_full_prompt = tokenize(full_prompt)
        if not train_on_inputs:
            user_prompt = generate_prompt({**data_point, "output": ""})
            tokenized_user_prompt = tokenize(user_prompt, add_eos_token=False)
            user_prompt_len = len(tokenized_user_prompt["input_ids"])

            tokenized_full_prompt["labels"] = [
                -100
            ] * user_prompt_len + tokenized_full_prompt["labels"][
                user_prompt_len:
            ]  # could be sped up, probably
        return tokenized_full_prompt

    if adapter_name == "adalora":
        config = AdaLoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=target_modules,
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
        )
    # elif adapter_name == "adaption-prompt":
    #     config = AdaptionPromptConfig(
    #         task_type="CAUSAL_LM",
    #     )
    elif adapter_name == "IA3":
        config = IA3Config(
            target_modules=TRANSFORMERS_MODELS_TO_IA3_TARGET_MODULES_MAPPING[
                model.config.model_type.lower()
            ],
            feedforward_modules=TRANSFORMERS_MODELS_TO_IA3_FEEDFORWARD_MODULES_MAPPING[
                model.config.model_type.lower()
            ],
            task_type="CAUSAL_LM",
        )
    elif adapter_name == "lora":
        config = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=target_modules,
            inference_mode=False,
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
        )
    elif adapter_name == "prefix-tuning":
        config = PrefixTuningConfig(
            num_virtual_tokens=num_virtual_tokens,
            task_type="CAUSAL_LM",
        )
    elif adapter_name == "prompt-tuning":
        config = PromptTuningConfig(
            num_virtual_tokens=num_virtual_tokens,
            task_type="CAUSAL_LM",
        )
    elif adapter_name == "p-tuning":
        config = PromptEncoderConfig(
            num_virtual_tokens=num_virtual_tokens,
            task_type="CAUSAL_LM",
        )
    else:
        raise ValueError(f"Unknown adapter name: {adapter_name}")
    if bits_and_bytes:
        model = prepare_model_for_kbit_training(
            model, use_gradient_checkpointing=use_gradient_checkpointing
        )
    model = get_peft_model(model, config)

    df = DataFrame(dataset)
    data = datasets.DatasetDict(
        {"train": datasets.Dataset.from_dict(df.to_dict("list"))}
    )

    if resume_from_checkpoint:
        # Check the available weights and load them
        checkpoint_name = os.path.join(
            resume_from_checkpoint, "pytorch_model.bin"
        )  # Full checkpoint
        if not os.path.exists(checkpoint_name):
            checkpoint_name = os.path.join(
                resume_from_checkpoint, "adapter_model.bin"
            )  # only LoRA model - LoRA config above has to fit
            resume_from_checkpoint = False  # So the trainer won't try loading its state
        # The two files above have a different name depending on how they were saved, but are actually the same.
        if os.path.exists(checkpoint_name):
            print(f"Restarting from {checkpoint_name}")
            adapters_weights = torch.load(checkpoint_name)
            model = set_peft_model_state_dict(model, adapters_weights)
        else:
            print(f"Checkpoint {checkpoint_name} not found")

    model.print_trainable_parameters()  # Be more transparent about the % of trainable params.

    if val_set_size > 0:
        train_val = data["train"].train_test_split(
            test_size=val_set_size, shuffle=True, seed=42
        )
        report_callback.set_eval_dataset(train_val["test"])
        train_data = train_val["train"].shuffle().map(generate_and_tokenize_prompt)
        val_data = train_val["test"].shuffle().map(generate_and_tokenize_prompt)
    else:
        train_data = data["train"].shuffle().map(generate_and_tokenize_prompt)
        val_data = None

    if torch.cuda.device_count() > 1:
        # keeps Trainer from trying its own DataParallelism when more than 1 gpu is available
        model.is_parallelizable = True
        model.model_parallel = True

    data_collator = transformers.DataCollatorForSeq2Seq(
        tokenizer, model=model, return_tensors="pt", padding=True, pad_to_multiple_of=16
    )

    train_data, val_data = acc.prepare(train_data, val_data)

    trainer = transformers.Trainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_data,
        eval_dataset=val_data,
        callbacks=[report_callback],
        args=transformers.TrainingArguments(
            per_device_train_batch_size=micro_batch_size,
            per_device_eval_batch_size=micro_batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            warmup_steps=100,
            num_train_epochs=num_epochs,
            learning_rate=learning_rate,
            fp16=False,
            bf16=True,
            logging_steps=logging_step,
            optim="adamw_torch",
            evaluation_strategy="steps" if val_set_size > 0 else "no",
            save_strategy="steps",
            eval_steps=eval_step if val_set_size > 0 else None,
            save_steps=save_step,
            output_dir=output_dir,
            save_total_limit=15,
            load_best_model_at_end=True if val_set_size > 0 else False,
            # ddp_find_unused_parameters=False if ddp else None,
            group_by_length=group_by_length,
            report_to="wandb" if use_wandb else None,
            run_name=wandb_run_name if use_wandb else None,
        ),
        data_collator=data_collator,
    )
    model.config.use_cache = False

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

    # print("\n If there's a warning about missing keys above, please disregard :)")


if __name__ == "__main__":
    fire.Fire(train)
