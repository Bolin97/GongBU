import copy
import os 
from vllm import LLM
from vllm.sampling_params import SamplingParams
from modelscope import AutoTokenizer, GenerationConfig, snapshot_download
from prompt_utils import _build_prompt,remove_stop_words

# 通义千问的特殊token
IMSTART='<|im_start|>'  
IMEND='<|im_end|>'
ENDOFTEXT='<|endoftext|>'     # EOS以及PAD都是它

class vLLMWrapper:
    def __init__(self, 
                 model_dir,
                 tensor_parallel_size=1,
                 gpu_memory_utilization=0.90,
                 dtype='float16',
                 quantization=None):
        # 模型目录下的generation_config.json文件，是推理的关键参数
        '''
        {
            "chat_format": "chatml",
            "eos_token_id": 151643,
            "pad_token_id": 151643,
            "max_window_size": 6144,
            "max_new_tokens": 512,
            "do_sample": true,
            "top_k": 0,
            "top_p": 0.8,
            "repetition_penalty": 1.1,
            "transformers_version": "4.31.0"
            }
        '''
        
        # 模型下载
        snapshot_download(model_dir)
        self.generation_config = GenerationConfig.from_pretrained(model_dir,trust_remote_code=True)
        
        # 加载分词器
        self.tokenizer=AutoTokenizer.from_pretrained(model_dir,trust_remote_code=True)
        self.tokenizer.eos_token_id=self.generation_config.eos_token_id
        # 推理终止词，遇到这些词停止继续推理
        self.stop_words_ids=[self.tokenizer.im_start_id,self.tokenizer.im_end_id,self.tokenizer.eos_token_id]
        # vLLM加载模型
        os.environ['VLLM_USE_MODELSCOPE']='True'
        self.model=LLM(model=model_dir,
                       tokenizer=model_dir,
                       tensor_parallel_size=tensor_parallel_size,
                       trust_remote_code=True,
                       quantization=quantization,
                       gpu_memory_utilization=gpu_memory_utilization, # 0.6
                       dtype=dtype)

    def chat(self,query,history=None,system="You are a helpful assistant.",extra_stop_words_ids=[]):
        # 历史聊天
        if history is None:
            history = []
        else:
            history = copy.deepcopy(history)

        # 额外指定推理停止词
        stop_words_ids=self.stop_words_ids+extra_stop_words_ids

        # 构造prompt
        prompt_text,prompt_tokens=_build_prompt(self.generation_config,self.tokenizer,query,history=history,system=system)
        
        # 打开注释，观测底层Prompt构造
        # print(prompt_text)

        # VLLM请求配置
        sampling_params=SamplingParams(stop_token_ids=stop_words_ids, 
                                         early_stopping=False,
                                         top_p=self.generation_config.top_p,
                                         top_k=-1 if self.generation_config.top_k == 0 else self.generation_config.top_k,
                                         temperature=self.generation_config.temperature,
                                         repetition_penalty=self.generation_config.repetition_penalty,
                                         max_tokens=self.generation_config.max_new_tokens)
        
        # 调用VLLM执行推理（批次大小1）
        req_outputs=self.model.generate(prompt_token_ids=[prompt_tokens],sampling_params=sampling_params,use_tqdm=False) # use_tqdm禁止进度条
        req_output=req_outputs[0]    
        
        # transformer模型的原生返回, 打开注释看一下原始推理结果
        # raw_response=req_output.outputs[0].text
        # print(raw_response)
        
        # 移除停用词        
        response_token_ids=remove_stop_words(req_output.outputs[0].token_ids,stop_words_ids)
        response=self.tokenizer.decode(response_token_ids)

        # 整理历史对话
        history.append((query,response))
        return response,history