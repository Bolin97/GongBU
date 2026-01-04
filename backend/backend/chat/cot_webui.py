import gradio as gr
import os 
from modelscope import AutoModelForCausalLM, AutoTokenizer
from transformers import TextIteratorStreamer
from threading import Thread

MAX_HISTORY_LEN=3
SYSTEM_PROMPT='''
# 任务
你现在扮演爸爸，给女儿赛西解答问题。

# 回答格式
<think>
针对问题，逐步拆解、分析、反思，整理解答思路。
</think>
以爸爸的第一人称视角，给赛西开始讲解。
'''

def chat_streaming(model_selector,query,history):
    messages=[
        {'role':'system','content':SYSTEM_PROMPT}, 
    ]
    for q,a in history:
        messages.append({'role':'user','content': q}, )
        messages.append({'role':'assistant','content': a}, )
    messages.append({'role':'user','content': query}, )
    messages.append({'role':'assistant','content': '<think>'})
    text=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=False,continue_final_message=True)
    model_inputs=tokenizer([text], return_tensors="pt").to(model.device)

    if model_selector=='Qwen Base Model':
        model.disable_adapters()
    else:
        model.enable_adapters()

    streamer=TextIteratorStreamer(tokenizer,skip_prompt=True,skip_special_tokens=True)
    generation_kwargs=dict(model_inputs,streamer=streamer,max_new_tokens=2000)
    thread=Thread(target=model.generate,kwargs=generation_kwargs)
    thread.start()
    for resp in streamer:
        yield resp
    thread.join()

with gr.Blocks(css='.qwen-logo img {height:200px; width:600px; margin:0 auto;}') as app:
    with gr.Row():
        chatbot=gr.Chatbot(label='DeepSeek Distill Qwen')
    with gr.Row():
        model_selector=gr.Dropdown(choices=['Qwen Base Model', 'Qwen Distll Model'],label='选择模型')
    with gr.Row():
        query_box=gr.Textbox(label='输入',autofocus=True,lines=2)
    with gr.Row():
        clear_btn=gr.ClearButton([query_box,chatbot],value='清空历史')
        submit_btn=gr.Button(value='提交')

    def chat(model_selector,query,history):
        full_resp='<think>'
        replace_resp=''
        for response in chat_streaming(model_selector,query,history):
            full_resp=full_resp+response
            replace_resp=full_resp.replace('<think>','[开始思考]\n').replace('</think>','\n[结束思考]\n')
            yield '',history+[(query,replace_resp)]
        history.append((query,replace_resp))
        while len(history)>MAX_HISTORY_LEN:
            history.pop(0)
    
    # 提交query
    submit_btn.click(chat,[model_selector,query_box,chatbot],[query_box,chatbot])

if __name__ == "__main__":
    # Load base model
    model_name='Qwen/Qwen2.5-3B-Instruct'
    model=AutoModelForCausalLM.from_pretrained(model_name,torch_dtype="auto",device_map="auto")
    tokenizer=AutoTokenizer.from_pretrained(model_name)
    
    # Find latest checkpoint
    checkpoints=os.listdir('qwen_distill/')
    latest_checkpoints=sorted(filter(lambda x: x.startswith('checkpoint'),checkpoints),key=lambda x: int(x.split('-')[-1]))[-1]
    lora_name=f'qwen_distill/{latest_checkpoints}'
    
    model.load_adapter(lora_name)
    
    app.queue(200)  # 请求队列
    app.launch(server_name='0.0.0.0',max_threads=500) # 线程池