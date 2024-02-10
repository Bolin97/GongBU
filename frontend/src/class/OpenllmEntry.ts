export default interface OpenllmEntry {
	model_id: string;
	model_name: string;
	model_description: string;
	view_pic: string;
	remote_path: string;
	local_path: string;
	local_store: number;
	lora_support: number;
	lora_multi_device: number;
	prefix_tuning_support: number;
	prefix_tuning_multi_device: number;
	ptuning_support: number;
	ptuning_multi_device: number;
	prompt_tuning_support: number;
	prompt_tuning_multi_device: number;
	IA3_support: number;
	IA3_multi_device: number;
	storage_state: string;
	storage_date: string;
	finetune: number;
	deployment: number;
}
