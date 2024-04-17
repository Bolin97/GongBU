import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Any
from transformers.utils.dummy_pt_objects import StoppingCriteria
from transformers.generation.stopping_criteria import StoppingCriteriaList

class LLMW:
    
    model: Any
    tokenizer: AutoTokenizer
    
    base_model_path: str
    adapter_path: str
    
    loaded: bool
    
    def __init__(self, base_model_path: str, adapter_path: str):
        self.base_model_path = base_model_path
        self.adapter_path = adapter_path
        self.loaded = False
        
    def load(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.base_model_path, trust_remote_code=True, device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_path, trust_remote_code=True, device_map="auto")
        if self.adapter_path and self.adapter_path != "":
            self.model.load_adapter(self.adapter_path)
        self.loaded = True
    
    def simple_text_generation(self, prompt: str, max_length: int):
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
        output = self.model.generate(inputs=input_ids, max_length=max_length, stopping_criteria=StoppingCriteriaList([StopOnTokens()]))
        out_text = self.tokenizer.decode(output[0], skip_special_tokens=True).removeprefix(prompt)
        return out_text