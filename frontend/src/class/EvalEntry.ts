// export default interface EvalEntry {
// 	id: number;
// 	name: string;
// 	description: string;
// 	state: number;
// 	start_time: string;
// 	end_time?: string;
// 	model_path: string;
// 	peft_path: string;
// 	dataset_id: number;
// 	datapool_id: number;
// 	devices: Array<string>;
// 	metrics: Array<string>;
// 	deepspeed: boolean;
// 	shot: number;
// 	ins_prompt: boolean;
// 	do_sample: boolean;
// 	temperature: number;
// 	top_k: number;
// 	top_p: number;
// 	max_new_tokens: number;
// 	skip_speical_tokens: number;
// 	owner: string;
// 	public: boolean;
// }
/**
 * {
    "end_time": "2024-04-17T07:40:19.571442",
    "devices": [
      "auto"
    ],
    "model_or_adapter_id": 1,
    "indexes": [
      "A"
    ],
    "deploy_base_model": true,
    "dataset_id": 1,
    "name": "123",
    "bits_and_bytes": false,
    "val_set_size": 0.2,
    "id": 6,
    "load_8bit": true,
    "result": {
      "A": 0
    },
    "description": "123",
    "load_4bit": true,
    "owner": "u1",
    "state": 3,
    "use_flash_attention": true,
    "public": false,
    "start_time": "2024-04-17T07:39:09.570618",
    "use_deepspeed": true
  }
 */
export default interface EvalEntry {
  id: number;
  name: string;
  end_time: string;
  devices: string[];
  model_or_adapter_id: number;
  indexes: string[];
  deploy_base_model: boolean;
  dataset_id: number;
  bits_and_bytes: boolean;
  val_set_size: number;
  load_8bit: boolean;
  result: { [index: string]: number };
  description: string;
  load_4bit: boolean;
  owner: string;
  state: number;
  use_flash_attention: boolean;
  public: boolean;
  start_time: string;
  use_deepspeed: boolean;
}
