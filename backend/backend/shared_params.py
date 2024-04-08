from typing import Literal, List
from pydantic import BaseModel


class FinetuneParams(BaseModel):
    model_id: str
    dataset_id: str
    devices: List[str]
    eval_indexes: List[Literal["F", "R", "P", "A", "B", "D"]]
    output_dir: str
    adapter_name: str
    batch_size: int
    micro_batch_size: int
    num_epochs: int
    learning_rate: float
    cutoff_len: int
    val_set_size: int
    use_gradient_checkpointing: bool
    eval_step: int
    save_step: int
    logging_step: int
    lora_r: int
    lora_alpha: float
    lora_dropout: float
    num_virtual_tokens: int
    train_on_inputs: bool
    group_by_length: bool
    bits_and_bytes: bool
    load_8bit: bool
    load_4bit: bool
    llm_int8_threshold: float
    llm_int8_enable_fp32_cpu_offload: bool
    llm_int8_has_fp16_weight: bool
    bnb_4bit_compute_dtype: str
    bnb_4bit_quant_type: str
    bnb_4bit_use_double_quant: bool
    zero_optimization: bool
    zero_stage: int
    zero_offload: bool
    use_dora: bool
    use_rslora: bool
    rank_dropout: float
    module_dropout: float
    use_effective_conv2d: bool
    use_flash_attention: bool
