# import gradio as gr
# import requests
# import json

# MAX_HISTORY_LEN=50

# def chat_streaming(query,history):
#     # 调用api_server
#     response=requests.post('http://localhost:8000/chat',json={
#         'query':query,
#         'stream': True,
#         'history':history
#     },stream=True)
    
#     # 流式读取http response body, 按\0分割
#     for chunk in response.iter_lines(chunk_size=8192,decode_unicode=False,delimiter=b"\0"):
#         if chunk:
#             data=json.loads(chunk.decode('utf-8'))
#             text=data["text"].rstrip('\r\n') # 确保末尾无换行
#             yield text

# with gr.Blocks(css='.qwen-logo img {height:200px; width:600px; margin:0 auto;}') as app:
#     with gr.Row():
#         logo_img=gr.Image('./qwen.png',elem_classes='qwen-logo')
#     with gr.Row():
#         chatbot=gr.Chatbot(label='通义千问14B-Chat-Int4')
#     with gr.Row():
#         query_box=gr.Textbox(label='提问',autofocus=True,lines=5)
#     with gr.Row():
#         clear_btn=gr.ClearButton([query_box,chatbot],value='清空历史')
#         submit_btn=gr.Button(value='提交')

#     def chat(query,history):
#         for response in chat_streaming(query,history):
#             yield '',history+[(query,response)]
#         history.append((query,response))
#         while len(history)>MAX_HISTORY_LEN:
#             history.pop(0)
    
#     # 提交query
#     submit_btn.click(chat,[query_box,chatbot],[query_box,chatbot])
#     # query_box.submit(chat,[query_box,chatbot],[query_box,chatbot])

# if __name__ == "__main__":
#     app.queue(200)  # 请求队列
#     app.launch(server_name='0.0.0.0',max_threads=500) # 线程池



import gradio as gr
import httpx
import uuid
import json
from typing import List, AsyncGenerator
import pandas as pd

# 配置
BACKEND_URL = "http://127.0.0.1:8002"
# 直接调用后台接口获取支持的访问的模型
# TODO

MODELS = ["deepseek-reasoner", "Qwen-1.8B", "GPT-4", "Llama-3"]

CSS = """
.gradio-container {max-width: 1200px !important; margin: 0 auto;}
.sidebar {border-right: 1px solid #e5e7eb; height: 100vh;}
.chat-area {height: calc(100vh - 160px); overflow-y: auto;}
.input-group {position: fixed; bottom: 20px; width: 72%; background: white;}
.dark .input-group {background: #1a1a1a;}
.message-user {background: #f3f4f6; border-radius: 12px; padding: 12px;}
.message-bot {background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 12px;}
.dark .message-bot {background: #2d2d2d;}
.model-selector {padding: 6px 16px; border-bottom: 1px solid #e5e7eb;}

.start-group {
    position: absolute;
    bottom: 500px;
    width: 83%;
}
.compact-btn {
    background: #ADD8E6;
    color: #333 !important;
    position: absolute;
    width: 100px !important;
    height: 46px;
    top: 150px;
    left: 210px;
}
.start-input{
    position: absolute;
    width: 500px;
    top: 150px;
    left: 50px;
}

#welcome-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin-top: -60px;
}
.action-btns {
    position: absolute;
    min-width: 90px !important; 
    width: 90px !important;
    margin-top: 110px;
    left: 50px;
}
.deep-search-btn-active {
    min-width: 90px !important; 
    background: white !important;
    color: #20B2AA !important;
    width: 90px !important;
    border-radius: 15px !important;
    font-size: 13px;  /* 字体大小 */
    font-weight: bold;  /* 不加粗 */
    border: 2px solid rgba(51, 51, 51, 0.1); /* 黑色边框,2px宽 */
    height: 46px !important;
    transition: all 0.3s !important;
}
.deep-search-btn {
    min-width: 90px !important; 
    background: white !important;
    color: #333 !important;
    width: 90px !important;
    font-size: 13px;  /* 字体大小 */
    font-weight: bold;  /* 不加粗 */
    border: 2px solid rgba(51, 51, 51, 0.1); /* 黑色边框,2px宽 */
    border-radius: 15px !important;
    height: 46px !important;
    transition: all 0.3s !important;
}

"""
#20B2AA 浅绿色
CSS_title = """
#custom_html_section {
     display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin-top: -60px;
}
"""

JS_deep_search ="""
    (btn) => {
        const deepSearchElement = document.getElementById('deep-search');
        const currentColor = window.getComputedStyle(deepSearchElement).color;
        console.log(currentColor);
        if (currentColor === 'rgb(51, 51, 51)') {  // #333 的 RGB 值
            document.getElementById('deep-search').className = 'deep-search-btn-active';  // 如果是 #333,则改为 #20B2AA
        } else if (currentColor === 'rgb(32, 178, 170)') {  // #20B2AA 的 RGB 值
            document.getElementById('deep-search').className = 'deep-search-btn';  // 如果是 #20B2AA,则改为 #333
        }
    }
"""

# 标题流式打印
JS_streamPrint = """
    function createGradioAnimation(){
        // 流式显示内容配置
        const content = {
            title: "我是乐于助人的AI助手🎉",
            subtitle: "我善于解决各种问题，有什么可以帮您的！"
        };
        console.log(content);
        
        // 打字机效果实现
        function typeWriter(elementId, text, speed=80, callback) {
            let i = 0;
            const elem = document.getElementById(elementId);
            console
           elem.innerText = '';
            
            function type() {
                if (i < text.length) {
                    elem.innerText += text.charAt(i);
                    i++;
                    setTimeout(type, speed);
                } else if (callback) {
                    callback();
                }
            }
            type();
        }

        // 启动动画
        setTimeout(() => {
            typeWriter('main-title', content.title, 80, () => {
                typeWriter('subtitle', content.subtitle, 50);
            });
        }, 200); // 延迟启动确保组件加载完成

    }
"""

# 严格前后端分离的API客户端
class APIClient:
    @staticmethod
    async def create_session(model: str, system_prompt: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/sessions",
                headers={"Authorization": f"Bearer {ui_state.token}"},
                json={
                    "model": model,
                    "system_prompt": system_prompt,
                }
            )
            return response.json()

    @staticmethod
    async def get_infer_point() -> List:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/infer/model/infer_points",
                                        headers={"Authorization": f"Bearer {ui_state.token}"})
            MODELS =  await response.json()

BASE_URL = "http://127.0.0.1:8002/ai"  # 替换为你的实际服务器地址

# 模拟获取JWT Token
def get_jwt_token():
    # 在这里实现获取JWT token的逻辑，假设它是静态的
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdXJvcmF5dWh1IiwiZXhwIjoxNzUzNDE5NTY0fQ.piS8S7NbHT1HQixP8tzzD8TYcu6Yh0FZeJjTlhWFCtM"


# GET /sessions 接口
async def get_sessions():
    url = f"{BASE_URL}/sessions"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {get_jwt_token()}"
               }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url,headers=headers)
        return response.json()

# GET /session/{session_id} 接口
async def get_session_messages(session_id: str):
    url = f"{BASE_URL}/session/{session_id}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# 流式聊天接口
async def chat_stream(session_id: str, model: str, message: str, is_stream: bool, deep_think: bool):
    url = f"{BASE_URL}/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_jwt_token()}"
    }
    payload = {
        "model": model,
        "sessionId": session_id,
        "message": message,
        "stream": is_stream,
        "deep_think": deep_think
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        if is_stream:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                reasoning_count = 0
                content_count = 0
                full_resp = ''
                async for chunk in response.aiter_bytes():
                    data = json.loads(chunk)

                    if data.get("reasoning_content"):
                        if reasoning_count == 0:
                            full_resp += '[开始思考]\n'
                        full_resp += data["reasoning_content"]
                        reasoning_count += 1

                    if data.get("content"):
                        if reasoning_count == 0:
                            replace_resp = data["content"].replace('<think>', '[开始思考]\n').replace('</think>', '\n[结束思考]\n')
                            full_resp += replace_resp
                        else:
                            if content_count == 0:
                                full_resp += '\n[结束思考]\n'
                            full_resp += data["content"]
                            content_count += 1

                    yield full_resp
        else:
            # 非流式：一次性响应，直接获取 JSON 数据
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                yield data["reply"]
            else:
                print(f"请求失败，状态码: {response.status_code}, 内容: {response.text}")


# POST /create_session 接口
async def create_session(model:str, message:str):
    url = f"{BASE_URL}/create_session"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_jwt_token()}"
    }
    payload = {
        "model": model,
        "message":  message
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        print(f"Create session response: {response.json()}")
        return response.json()

# 前端状态管理
class UIState:
    def __init__(self):
        
        self.current_session = None
        self.selected_model = MODELS[0]
        self.session_list = []
        # 用户是否选择了深度搜索
        self.deep_think = True
        self.token = None
        # <think>

ui_state = UIState()


# 创建新会话
async def create_new_session(model: str, start_input: str):
    response = await create_session(model, start_input)
    ui_state.current_session = response["id"]
    ui_state.selected_model = model
    # 获取会话数据存储在前端UI中 
    session_list = await refresh_session_list()
    yield [   
            '',
            gr.update(visible=False),  # 隐藏欢迎页
            gr.update(visible=True),   # 显示聊天页
            session_list,
            gr.update( visible=False),  # 隐藏模型选择框
            gr.update(value=ui_state.selected_model, visible=True), #显示选择模型
            [(start_input,'')]
        ] 
    # 异步调用
    async for chat_history in handle_stream_response(current_session, model, start_input, ui_state.deep_think):
        yield [
            '',   
            gr.update(visible=False),  # 隐藏欢迎页
            gr.update(visible=True),   # 显示聊天页
            session_list,
            gr.update( visible=False),  # 隐藏模型选择框
            gr.update(value=ui_state.selected_model, visible=True), #显示选择模型
            [(start_input, chat_history)]
            
        ]
# 刷新会话列表
async def refresh_session_list():
    
    sessions = await get_sessions()
    # 按照修改时间排序
    sessions.sort(key=lambda x: x['updated_at'], reverse=True)
    ui_state.session_list = sessions
    return [[s["title"]] for s in ui_state.session_list]

# 处理消息流式响应
async def handle_stream_response(session_id: str, model:str, message: str, deep_think, is_stream:bool = True):
    async for chunk in chat_stream(session_id, model, message, is_stream, deep_think):
        yield chunk

# 主消息处理流程
async def process_message(history:list, message: str):
    yield [   
            history  + [(message,'')]
        ] 
    # 异步调用
    async for chat_history in handle_stream_response(ui_state.current_session, ui_state.selected_model, message, ui_state.deep_think):
        yield [
            history + [(message, chat_history)]
        ]

# 会话点击处理
async def load_session(evt: gr.SelectData, history: list):
    # 根据选择的index, 获取选择的会话数据
    selected_session = ui_state.session_list[evt.index]
    if selected_session["title"] != evt.value:
        return [
            history,
            gr.update(value=ui_state.selected_model)
        ]
    ui_state.current_session = selected_session['id']
    ui_state.selected_model = selected_session["model"]
    session_history = await get_session_messages(selected_session['id'])
    # 将返回转化为chatbox需要的元组
    chat_history = []
    current_user_msg = None
    for msg in session_history:
        role = msg.get("role")
        content = msg.get("content", "")

        if role == "user":
            # 如果之前已经有未匹配的 user，先将其配对为空回答
            if current_user_msg is not None:
                chat_history.append((current_user_msg, ""))
            current_user_msg = content

        elif role == "assistant":
            if current_user_msg is not None:
                chat_history.append((current_user_msg, content))
                current_user_msg = None
            else:
                # 没有 user 却来 assistant，默认忽略（可按需处理）
                pass

    # 如果最后还有未匹配的 user，补空助手回答
    if current_user_msg is not None:
        chat_history.append((current_user_msg, ""))

    return [
        chat_history,
        gr.update(value=selected_session["model"])
    ]

async def switch_deep_search():
   ui_state.deep_think = not ui_state.deep_think


# 新建会话返回主页面
async def create_new_chat():
    # 清空UI状态
    ui_state.current_session = None
    ui_state.selected_model = None
    return [   
            gr.update(visible=True),  # 返回欢迎页
            gr.update(visible=False),   # 隐藏聊天页
            gr.update(visible=True),  # 回到模型选择框
            gr.update(visible=False), # 隐藏选择模型
            gr.update(choices=MODELS,value=MODELS[0]),
        ]



async def save_token_to_state(token):
    """这个函数在页面加载时调用,把提取到的token保存到UIState"""
    ui_state.token = token
    print(f"[Info] 保存了Token: {token}")
    return [await refresh_session_list()]

# 这个JS脚本，提取URL里的 `id=xxx`
GET_TOKEN_FROM_URL = """
() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('id'); 
    console.log("提取到Token: ", token);
    return token || "";
}
"""

CSS += """
/* 青色调按钮 */
.cyan-btn {
    background: #00bcd4 !important;
    color: white !important;
    border: none !important;
}

/* 历史会话标题样式 */
.history-header {
    margin: 15px 0 !important;
    color: #333 !important;
}

/* 紧凑型表格样式 */
.compact-table table {
    border-collapse: collapse !important;
    width: 100% !important;
}

.compact-table th {
    display: none !important; /* 隐藏表头 */
}

.compact-table td {
    padding: 12px 8px !important;
    border-bottom: 1px solid #eee !important;
    font-size: 14px !important;
    line-height: 1.4 !important;
}

.compact-table tr:last-child td {
    border-bottom: none !important;
}

.compact-table tr:hover td {
    background: #f8f8f8 !important;
    cursor: pointer;
}
"""

# 标题流式打印
with gr.Blocks(css=CSS, title="AI Assistant", js=JS_streamPrint) as app:
    # 全局状态
    current_session = gr.State()
    
    with gr.Row():
        # 左侧会话列（优化后）
        with gr.Column(scale=1, elem_classes="sidebar"):
            create_btn = gr.Button("新建会话", variant="primary", elem_classes="cyan-btn")
            gr.Markdown("### 历史会话", elem_classes="history-header")
            
            # 优化后的历史会话列表
            session_list = gr.Dataframe(
                headers=["会话标题", "日期"],
                interactive=False,
                datatype=["str", "str"],
                height="85vh",
                elem_classes="compact-table",
                value=[
                    ["如何配置网络？", "2025/04/29"],
                    ["系统安装问题", "2025/04/29"]
                ]
            )

        # 右侧主内容
        with gr.Column(scale=3):
            # 模型选择器
            with gr.Row(visible=True) as model_selector:
                model_dropdown = gr.Dropdown(
                    MODELS,
                    value=MODELS[0],
                    label="选择模型",
                    show_label=False,
                    # container=False,
                    elem_classes="model-selector"
                )
            with gr.Row(visible=False) as model_selected:
                gr.Markdown(f"### {ui_state.selected_model}", elem_classes="model-selector")

            
            # 聊天区域
            with gr.Column(visible=False) as chat_container:
                chatbot = gr.Chatbot(
                    elem_classes="chat-area",
                    bubble_full_width=False,
                    show_label=False
                )
                
                with gr.Row(elem_classes="input-group"):
                    with gr.Column(scale=6):
                        msg_input = gr.Textbox(
                            label="请输入您的问题: ",
                            show_label=False,
                            placeholder="在此输入您的问题..."
                            # container=False,
                            # lines=2
                        )
                    with gr.Column(scale=1):
                        send_btn = gr.Button("发送", variant="primary")

            # 欢迎页面
            with gr.Column(visible=True,elem_id='welcome-container') as welcome:
                # gr.Markdown("我是乐于助人的AI助手🎉", elem_id="welcome-title")
                # gr.Markdown("我可以帮助您解决各种问题，请开始对话吧！", elem_id="welcome-description")
            
                # 不知道为什么，这里使用js的时候不生效，只有最外面在这层block使用js才生效
                # with gr.Blocks(css=CSS_title,js=JS_streamPrint) as app1:
                with gr.Blocks(css=CSS_title) as app1:
                    with gr.Column(elem_id="custom_html_section"):
                        gr.HTML("""
                            <div class="welcome-container">
                                <h1 id="main-title" class="welcome-title" style="font-size: 2rem !important; font-weight: 700 !important;  margin-top: 340px  !important;
                                    text-align: center;">
                                    </h1>
                                <div style=" color: #666;margin-bottom: 440px;text-align: center;">
                                    <span id="subtitle" ></span>
                                </div>
                            </div>
                                
                        """)
                with gr.Row(elem_classes="start-group"):
                    with gr.Column(scale=8):
                        start_input = gr.Textbox(
                            label="请输入您的问题: ",
                            show_label=False,
                            container=False,
                            placeholder="在此输入您的问题...",
                            elem_classes="start-input"
                        )
                    with gr.Column(scale=1):
                        start_btn = gr.Button(
                            '发送',
                            icon='../icon/send.png',
                            variant="primary",
                            elem_classes="compact-btn"
                        )
                    with gr.Row(visible=True, elem_classes="action-btns"):
                            deep_search_btn = gr.Button(
                                "深度搜索",
                                elem_classes="deep-search-btn-active",
                                elem_id = "deep-search"
                            )

    # 有些模型不支持深度搜索
    model_dropdown.change(
        lambda x: setattr(ui_state, "selected_model", x),
        model_dropdown
    )
    # 将多个触发器绑定到同一函数 ----> 支持点击提交按钮，或者按下回车键来提交
    gr.on(
        triggers=[start_input.submit, start_btn.click],
        fn=create_new_session,
        inputs=[model_dropdown, start_input],
        outputs=[start_input, welcome, chat_container, session_list, model_selector,model_selected, chatbot])


    send_btn.click(
        process_message,
        [chatbot, msg_input],
        [chatbot]
    )

    session_list.select(
        load_session,
        [chatbot],
        outputs=[chatbot, model_dropdown]
    )

    create_btn.click(
        create_new_chat,
        [],
        [welcome, chat_container, model_selector,model_selected, model_dropdown]
    )
    # 深度搜索按钮交互
    deep_search_btn.click(
        switch_deep_search,
        js=JS_deep_search
    )

    # 页面一加载，调用JS提取token
    app.load(save_token_to_state, inputs=[], outputs=[session_list], js=GET_TOKEN_FROM_URL)

if __name__ == "__main__":
    app.queue(500)  # 请求队列
    app.launch(server_name='0.0.0.0', share=True, max_threads=200) # 线程池

# 热更新启动
# gradio gradio_webui.py --demo-name=app
