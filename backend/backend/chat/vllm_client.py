import requests
import json 

def clear_lines():
    print('\033[2J')
        
history=[]

while True:
    query=input('问题:')
    
    # 调用api_server
    response=requests.post('http://localhost:8888/chat',json={
        'query':query,
        'stream': True,
        'history':history,
    },stream=True)
    
    # 流式读取http response body, 按\0分割
    for chunk in response.iter_lines(chunk_size=8192,decode_unicode=False,delimiter=b"\0"):
        if chunk:
            data=json.loads(chunk.decode('utf-8'))
            text=data["text"].rstrip('\r\n') # 确保末尾无换行
            
            # 清空前一次的内容
            clear_lines()
            # 打印最新内容
            print(text)
    
    # 对话历史
    history.append((query,text))
    history=history[-5:] 
    