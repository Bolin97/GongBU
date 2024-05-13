export default interface Deployment {
  model_or_adapter_id: number;
  name: string;
  description: string;
  bits_and_bytes: boolean;
  load_4bit: boolean;
  use_deepspeed: boolean;
  devices: string[];
  public: boolean;
  state: number;
  id: number;
  deploy_base_model: boolean;
  load_8bit: boolean;
  use_flash_attention: boolean;
  use_vllm: boolean;
  port: number;
}
