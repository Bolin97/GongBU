import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Any
from transformers.utils.dummy_pt_objects import StoppingCriteria
from transformers.generation.stopping_criteria import StoppingCriteriaList
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

class LLMW:

    model: Any
    tokenizer: AutoTokenizer

    base_model_path: str
    adapter_path: str
    
    vllm_model: LLM

    loaded: bool
    
    use_vllm: bool
    vllm_lora_request: Any
    
    use_deepseed: bool

    def __init__(self, base_model_path: str, adapter_path: str, use_vllm: bool = False, use_deepspeed: bool = False):
        self.base_model_path = base_model_path
        self.adapter_path = adapter_path
        self.loaded = False
        self.use_vllm = use_vllm
        self.use_deepspeed = use_deepspeed
        self.vllm_lora_request = None

    def load(self):
        if self.use_vllm:
            self.vllm_model = LLM(self.base_model_path, self.base_model_path, enable_lora=True)
            if self.adapter_path is not None and self.adapter_path != "":
                self.vllm_lora_request = LoRARequest(
                    "load_adapter",
                    1,
                    self.adapter_path,
                )
            self.loaded = True
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_path, trust_remote_code=True, device_map="auto"
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model_path, trust_remote_code=True, device_map="auto"
            )
            if self.adapter_path and self.adapter_path != "":
                self.model.load_adapter(self.adapter_path)
            self.loaded = True
    
    def vllm_simple_generation(self, prompt: str, max_length: int):
        if self.vllm_lora_request is None:
            return self.vllm_model.generate(prompt, sampling_params=SamplingParams(
                max_tokens=max_length,
                stop_token_ids=[self.vllm_model.get_tokenizer().eos_token_id]
            ))[0].outputs[0].text
        else:
            return self.vllm_model.generate(prompt, sampling_params=SamplingParams(
                max_tokens=max_length,
                stop_token_ids=[self.vllm_model.get_tokenizer().eos_token_id]
            ), lora_request=self.vllm_lora_request)[0].outputs[0].text
            
    def vllm_advanced_generation(self, prompt: str, sampling_params: dict):
        sampling_params["stop_token_ids"] = [self.vllm_model.get_tokenizer().eos_token_id]
        if self.vllm_lora_request is None:
            return self.vllm_model.generate(prompt, sampling_params=SamplingParams(
                **sampling_params
            ))[0].outputs[0].text
        else:
            return self.vllm_model.generate(prompt, sampling_params=SamplingParams(
                **sampling_params
            ), lora_request=self.vllm_lora_request)[0].outputs[0].text

    def simple_generation(self, prompt: str, max_length: int):
        if self.use_vllm:
            return self.vllm_simple_generation(prompt, max_length)
        else:
            return self.transformers_simple_text_generation(prompt, max_length)

    def transformers_simple_text_generation(self, prompt: str, max_length: int):
        stop_token_ids = [self.tokenizer.eos_token_id]

        class StopOnTokens(StoppingCriteria):
            def __call__(
                self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs
            ) -> bool:
                for stop_id in stop_token_ids:
                    if input_ids[0][-1] == stop_id:
                        return True
                return False

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to("cuda")
        output = self.model.generate(
            inputs=input_ids,
            max_length=max_length,
            stopping_criteria=StoppingCriteriaList([StopOnTokens()]),
        )
        out_text = self.tokenizer.decode(
            output[0], skip_special_tokens=True
        ).removeprefix(prompt)
        return out_text

    def transformers_advanced_text_generation(self, prompt: str, 
        max_length: int = 20, 
        max_new_tokens: int = None,
        min_length: int = 0,
        min_new_tokens: int = None,
        early_stopping: str = False,
        max_time: float = None,
        do_sample: bool = False, 
        num_beams: int = 1,
        num_beam_groups: int = 1,
        use_cache: bool = True,
        temperature: float = 1.0, 
        top_k: int = 50, 
        top_p: float = 1.0, 
        typical_p: float = 1.0,
    ):
        if str(early_stopping).lower() == "true":
            early_stopping = True
        elif str(early_stopping).lower() == "false":
            early_stopping = False
        else:
            early_stopping = early_stopping
        stop_token_ids = [self.tokenizer.eos_token_id]

        class StopOnTokens(StoppingCriteria):
            def __call__(
                self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs
            ) -> bool:
                for stop_id in stop_token_ids:
                    if input_ids[0][-1] == stop_id:
                        return True
                return False

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to("cuda")
        output = self.model.generate(
            inputs=input_ids,
            max_length=int(max_length),
            max_new_tokens=int(max_new_tokens),
            min_length=int(min_length),
            min_new_tokens=int(min_new_tokens),
            early_stopping=early_stopping,
            max_time=max_time,
            do_sample=do_sample,
            num_beams=num_beams,
            num_beam_groups=num_beam_groups,
            use_cache=use_cache,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            typical_p=typical_p,
            stopping_criteria=StoppingCriteriaList([StopOnTokens()]),
        )
        out_text = self.tokenizer.decode(
            output[0], skip_special_tokens=True
        ).removeprefix(prompt)
        return out_text