/**
 * class FinetuneParams(BaseModel):
    model_id: str
    dataset_id: str
    devices: List[int]
    eval_indexes: List[Literal["acc", "f1", "bleu", "rouge", "distinctn", "bert"]]
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
    lora_r: float
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
 */

export interface FinetuneParams {
	model_id: string;
	dataset_id: string;
	devices: Array<number> | "auto";
	eval_indexes: Array<string>;
	output_dir: string;
	adapter_name: string;
	batch_size: number;
	micro_batch_size: number;
	num_epochs: number;
	learning_rate: number;
	cutoff_len: number;
	val_set_size: number;
	use_gradient_checkpointing: boolean;
	eval_step: number;
	save_step: number;
	logging_step: number;
	lora_r: number;
	lora_alpha: number;
	lora_dropout: number;
	num_virtual_tokens: number;
	train_on_inputs: boolean;
	group_by_length: boolean;
	bits_and_bytes: boolean;
	load_8bit: boolean;
	load_4bit: boolean;
	llm_int8_threshold: number;
	llm_int8_enable_fp32_cpu_offload: boolean;
	llm_int8_has_fp16_weight: boolean;
	bnb_4bit_compute_dtype: string;
	bnb_4bit_quant_type: string;
	bnb_4bit_use_double_quant: boolean;
}

export function default_finetune_params(): FinetuneParams {
	return {
		model_id: "",
		dataset_id: "",
		devices: [],
		eval_indexes: [],
		output_dir: "",
		adapter_name: "",
		batch_size: -1,
		micro_batch_size: -1,
		num_epochs: -1,
		learning_rate: -1,
		cutoff_len: -1,
		val_set_size: -1,
		use_gradient_checkpointing: false,
		eval_step: -1,
		save_step: -1,
		logging_step: -1,
		lora_r: -1,
		lora_alpha: -1,
		lora_dropout: -1,
		num_virtual_tokens: -1,
		train_on_inputs: false,
		group_by_length: false,
		bits_and_bytes: false,
		load_8bit: false,
		load_4bit: false,
		llm_int8_threshold: -1,
		llm_int8_enable_fp32_cpu_offload: false,
		llm_int8_has_fp16_weight: false,
		bnb_4bit_compute_dtype: "",
		bnb_4bit_quant_type: "",
		bnb_4bit_use_double_quant: false
	};
}