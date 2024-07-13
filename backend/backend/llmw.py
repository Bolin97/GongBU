import time
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Any
from transformers.utils.dummy_pt_objects import StoppingCriteria
from transformers.generation.stopping_criteria import StoppingCriteriaList
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
from typing import *

class OpenAIChatCompletionRequest(BaseModel):
    messages: List[Union[str, Dict[str, str]]]
    model: str
    frequency_penalty: Optional[float] = 0.0
    logit_bias: Optional[Dict[str, float]] = None
    logprobs: Optional[bool] = False
    top_logprobs: Optional[int] = None
    max_tokens: Optional[int] = None
    n: Optional[int] = 1
    presence_penalty: Optional[float] = 0.0
    response_format: Optional[dict] = None
    seed: Optional[int] = None
    service_tier: Optional[str] = None
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    stream_options: Optional[dict] = None
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    tools: Optional[List[dict]] = None
    tool_choice: Optional[dict] = None
    parallel_tool_calls: Optional[bool] = True
    user: Optional[str] = None
    function_call: Optional[Union[str, dict]] = None
    functions: Optional[List[dict]] = None
    
from typing import *

class LLMW:

    model: AutoModelForCausalLM
    tokenizer: AutoTokenizer

    base_model_path: str
    adapter_path: str
    
    vllm_model: LLM

    loaded: bool
    
    use_vllm: bool
    vllm_lora_request: Any
    
    use_deepseed: bool
    
    def construct_prompt(self, messages: List[Any]) -> str:
        tokenizer = self.tokenizer if not self.use_vllm else self.vllm_model.get_tokenizer()
        result = []
        for message in messages:
            if isinstance(message, str):
                result.append(message)
            elif isinstance(message, dict):
                if "role" in message:
                    result.append(
                        f"{message['role']}" + tokenizer.eos_token + f"{message['content']}"
                    )
            else:
                result.append(str(message))
        return tokenizer.eos_token.join(result)

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
        max_new_tokens: int = 20,
        min_length: int = 0,
        min_new_tokens: int = 0,
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

    def openai_chat_completion(self, request: OpenAIChatCompletionRequest):
        if self.use_vllm:
            return self.vllm_openai_chat_completion(request)
        else:
            return self.transformers_openai_chat_completion(request)

    def transformers_openai_chat_completion(
        self,
        request: OpenAIChatCompletionRequest,
    ):
        tokenizer = self.tokenizer
        model = self.model
        
        # Construct generate_args from request
        generate_args = {
            "do_sample": True,
            "temperature": request.temperature if request.temperature is not None else 1.0,
            "top_p": request.top_p if request.top_p is not None else 1.0,
            "max_length": request.max_tokens if request.max_tokens is not None else 128,
            "num_return_sequences": request.n if request.n is not None else 1,
        }

        # Adjust generate_args based on conditions
        if any(k in generate_args for k in ['top_p', 'top_k', 'temperature']) and 'do_sample' not in generate_args:
            generate_args['do_sample'] = True
            generate_args.pop('temperature', None) if generate_args.get('temperature', 1.0) == 0 else None
            generate_args.pop('top_p', None) if generate_args.get('top_p', 1.0) == 1.0 else None
            generate_args.setdefault('top_k', 0)

        # Extract prompts and handle echo
        prompt = self.construct_prompt(request.messages)
        echo = generate_args.pop('echo', False)
        n = generate_args.pop('n', 1)

        # Remove keys not needed for model generation
        for key in ['model', 'prompt', 'n', 'best_of', 'presence_penalty', 'frequency_penalty', 'logit_bias']:
            generate_args.pop(key, None)

        # Tokenize prompts
        prompt_tokens_count = 0
        # for prompt in prompts:
        #     input_ids = tokenizer(prompt, return_tensors="pt").input_ids
        #     input_ids = input_ids.to("cuda")
        #     prompt_tokens_count += input_ids.size(1)
        #     inputs.append(input_ids)
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        input_ids = input_ids.to("cuda")
        prompt_tokens_count = len(input_ids)
        

        class StopOnTokens(StoppingCriteria):
            def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
                for stop_id in [tokenizer.eos_token_id]:
                    if input_ids[0][-1] == stop_id:
                        return True
                return False

        # Generate and decode responses
        choices = []
        completion_tokens_count = 0
        for i in range(n):
            output_ids = model.generate(input_ids, stopping_criteria=StoppingCriteriaList([StopOnTokens()]), **generate_args)[0]
            completion_tokens_count += len(output_ids)
            text = tokenizer.decode(output_ids, skip_special_tokens=True)
            if not echo or echo is None:
                text = text.removeprefix(prompt)
            choices.append({'text': text, 'index': i})

        # Construct response object
        response = {
            "created": int(time.time()),
            "model": request.model,
            "choices": choices,
            "usage": {
                "prompt_tokens": prompt_tokens_count,
                "completion_tokens": completion_tokens_count,
                "total_tokens": prompt_tokens_count + completion_tokens_count
            }
        }

        return response

    def vllm_openai_chat_completion(
        self,
        request: OpenAIChatCompletionRequest,
    ):
        tokenizer = self.vllm_model.get_tokenizer()
        sample_params = SamplingParams(
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stop_token_ids=[tokenizer.eos_token_id],
            do_sample=True,
            num_return_sequences=request.n,
            best_of=request.best_of,
            presence_penalty=request.presence_penalty,
            frequency_penalty=request.frequency_penalty,
            logit_bias=request.logit_bias,
            # echo=request.echo,      
        )
        
        # Extract prompts and handle echo
        prompt = self.construct_prompt(request.messages)
        n = request.n
        
        # Tokenize prompts
        prompt_tokens_count = 0
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        input_ids = input_ids.to("cuda")
        prompt_tokens_count = len(input_ids)
        
        
        # Generate and decode responses
        choices = []
        completion_tokens_count = 0
        for i in range(n):
            output_ids = self.vllm_model.generate(
                input_ids, sampling_params=sample_params,
                lora_request=self.vllm_lora_request
            )[0].outputs[0].text
            completion_tokens_count += len(output_ids)
            text = tokenizer.decode(output_ids, skip_special_tokens=True)
            if not request.echo or request.echo is None:
                text = text.removeprefix(prompt)
            choices.append({'text': text, 'index': i})
        
        # Construct response object
        response = {
            "created": int(time.time()),
            "model": request.model,
            "choices": choices,
            "usage": {
                "prompt_tokens": prompt_tokens_count,
                "completion_tokens": completion_tokens_count,
                "total_tokens": prompt_tokens_count + completion_tokens_count
            }
        }
        
        return response