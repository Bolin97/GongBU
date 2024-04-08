export default interface EvalEntry {
	id: number;
	name: string;
	description: string;
	state: number;
	start_time: string;
	end_time?: string;
	model_path: string;
	peft_path: string;
	dataset_id: number;
	datapool_id: number;
	devices: Array<string>;
	metrics: Array<string>;
	deepspeed: boolean;
	shot: number;
	ins_prompt: boolean;
	do_sample: boolean;
	temperature: number;
	top_k: number;
	top_p: number;
	max_new_tokens: number;
	skip_speical_tokens: number;
	owner: string;
	public: boolean;
}