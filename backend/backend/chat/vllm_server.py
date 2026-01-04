# 实现一个高并发流式的推理服务器
import os 
from vllm import AsyncEngineArgs,AsyncLLMEngine
from vllm.sampling_params import SamplingParams
from modelscope import AutoTokenizer, GenerationConfig,snapshot_download
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
import uvicorn
from prompt_utils import _build_prompt,remove_stop_words
import uuid
import json

app  = FastAPI()

model_dir = "tclf90/deepseek-r1-distill-qwen-32b-gptq-int4"
# model_dir="/home/tx/qwen/Qwen-14B-Chat-Int4"
tensor_parallel_size = 2
gpu_memory_utilization=0.9
quantization='gptq'
dtype='float16'

def load_vllm():
    global generation_config,tokenizer,stop_words_ids,engine    
    # 模型下载
    # snapshot_download(model_dir)
    # 模型基础配置
    generation_config=GenerationConfig.from_pretrained(model_dir,trust_remote_code=True)
    # 加载分词器
    tokenizer=AutoTokenizer.from_pretrained(model_dir,trust_remote_code=True)
    tokenizer.eos_token_id=generation_config.eos_token_id
    # 推理终止词
    stop_words_ids=[tokenizer.im_start_id,tokenizer.im_end_id,tokenizer.eos_token_id]
    # vLLM基础配置
    args=AsyncEngineArgs(model_dir)
    args.worker_use_ray=False
    args.engine_use_ray=False
    args.tokenizer=model_dir
    args.tensor_parallel_size=tensor_parallel_size
    args.trust_remote_code=True
    args.quantization=quantization
    args.gpu_memory_utilization=gpu_memory_utilization
    args.dtype=dtype
    args.max_num_seqs=20    # batch最大20条样本
    # 加载模型
    # os.environ['VLLM_USE_MODELSCOPE']='True'
    engine=AsyncLLMEngine.from_engine_args(args)
    return generation_config,tokenizer,stop_words_ids,engine

generation_config,tokenizer,stop_words_ids,engine=load_vllm()

# 用户停止句匹配
def match_user_stop_words(response_token_ids,user_stop_tokens):
    for stop_tokens in user_stop_tokens:
        if len(response_token_ids)<len(stop_tokens):
            continue 
        if response_token_ids[-len(stop_tokens):]==stop_tokens:
            return True  # 命中停止句, 返回True
    return False

# 后续这个接口需要改造成为chat_local函数而使用最下面的chat接口
@app.post("/chat")
async def chat(request: Request):
    
    
    request = await request.json()
    query=request.get('query',None)
    history=request.get('history',[])
    system=request.get('system','You are a helpful assistant.')
    stream=request.get("stream",False)
    user_stop_words=request.get("user_stop_words",[])    # list[str]，用户自定义停止句，例如：['Observation: ', 'Action: ']定义了2个停止句，遇到任何一个都会停止
    if query is None:
        return Response(status_code=502,content='query is empty')
    
     # 用户停止词
    user_stop_tokens=[]
    for words in user_stop_words:
        user_stop_tokens.append(tokenizer.encode(words))
    
    # 构造prompt
    prompt_text,prompt_tokens=_build_prompt(generation_config,tokenizer,query,history=history,system=system)
        
    # vLLM请求配置
    sampling_params=SamplingParams(stop_token_ids=stop_words_ids, 
                                    early_stopping=False,
                                    top_p=generation_config.top_p,
                                    top_k=-1 if generation_config.top_k == 0 else generation_config.top_k,
                                    temperature=generation_config.temperature,
                                    repetition_penalty=generation_config.repetition_penalty,
                                    max_tokens=generation_config.max_new_tokens)
    # vLLM异步推理（在独立线程中阻塞执行推理，主线程异步等待完成通知）
    request_id=str(uuid.uuid4().hex)
    results_iter=engine.generate(prompt=None,sampling_params=sampling_params,prompt_token_ids=prompt_tokens,request_id=request_id)

    # 流式返回，即迭代transformer的每一步推理结果并反复返回
    if stream:
        async def streaming_resp():
            async for result in results_iter:
                # 移除im_end,eos等系统停止词
                token_ids=remove_stop_words(result.outputs[0].token_ids,stop_words_ids)
                # 返回截止目前的tokens输出                
                text=tokenizer.decode(token_ids)
                yield (json.dumps({'text':text})+'\0').encode('utf-8')
                # 匹配用户停止词,终止推理
                if match_user_stop_words(token_ids,user_stop_tokens):
                    await engine.abort(request_id)   # 终止vllm后续推理
                    break
        return StreamingResponse(streaming_resp())

    # 整体一次性返回模式
    async for result in results_iter:
        # 移除im_end,eos等系统停止词
        token_ids=remove_stop_words(result.outputs[0].token_ids,stop_words_ids)
        # 返回截止目前的tokens输出                
        text=tokenizer.decode(token_ids)
        # 匹配用户停止词,终止推理
        if match_user_stop_words(token_ids,user_stop_tokens):
            await engine.abort(request_id)   # 终止vllm后续推理
            break

    ret={"text":text}
    return JSONResponse(ret)

# from fastapi import FastAPI, Depends, HTTPException, Request, Cookie
# from sqlalchemy import Column, Integer, String, DateTime, Text, desc
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from datetime import datetime
# import uuid
# import os
# from openai import OpenAI
# from backend.auth import accessible, get_current_identifier

# DATABASE_URL = "mysql+aiomysql://root:lq123456@localhost/ai_db"
# engine = create_async_engine(DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
# Base = declarative_base()

# # 定义数据库模型
# class SessionModel(Base):
#     __tablename__ = "sessions"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     session_id = Column(String(36), unique=True, nullable=False)
#     username = Column(String(100), nullable=False)
#     title = Column(String(100), nullable=False)
#     model = Column(String(100), nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# class MessageModel(Base):
#     __tablename__ = "messages"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     session_id = Column(String(36), nullable=False)
#     role = Column(String(20), nullable=False)
#     content = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)

# # 创建表
# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# # 依赖项：获取数据库会话
# async def get_db():
    
#     async with SessionLocal() as session:
#         yield session

# # 获取会话标题
# async def get_session_title(message: str) -> str:
#     doubao_api_key = os.getenv("doubao_api_key")
#     client = OpenAI(api_key=doubao_api_key, base_url="https://ark.cn-beijing.volces.com/api/v3/chat/completions")
#     response = client.chat.completions.create(
#         model="doubao-1-5-pro-32k-250115",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant"},
#             {"role": "user", "content": "请你根据下面内容生成一个总结title, 并限制在十个(中文就对应字，英文就对应词)之内：" + message},
#         ],
#         stream=False
#     )
#     return response.choices[0].message.content

# # 创建会话
# @app.post("/create_session")
# async def create_session(
#     request: Request, 
#     username:str =  Depends(get_current_identifier),
#     db: AsyncSession = Depends(get_db)
# ):
#     # if not username:
#     #     raise HTTPException(status_code=401, detail="User not authenticated")
#     request = await request.json()
#     title = await get_session_title(request.get('message'))
#     session_id = str(uuid.uuid4())
#     new_session = SessionModel(session_id=session_id, model=request.get('model'), username=username, title=title)
#     db.add(new_session)
#     await db.commit()
#     return {"session": {"id": session_id, "title": title}}

# # 获取用户会话列表
# @app.get("/sessions")
# async def get_sessions(
#     username:str =  Depends(get_current_identifier),
#     db: AsyncSession = Depends(get_db)
#     ):
#     result = await db.execute(
#         SessionModel.select().where(SessionModel.username == username).order_by(desc(SessionModel.updated_at))
#     )
#     sessions = result.scalars().all()
#     return [{"id": s.id, "title": s.title, "model": s.model, "updated_at": s.updated_at} for s in sessions]

# # 获取会话消息
# @app.get("/session/{session_id}")
# async def get_session_messages(session_id: str, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(
#         MessageModel.select().where(MessageModel.session_id == session_id).order_by(MessageModel.created_at)
#     )
#     messages = result.scalars().all()
#     return [{"role": m.role, "content": m.content} for m in messages]

# # 处理聊天
# @app.post("/chat")
# async def chat(request: Request, db: AsyncSession = Depends(get_db)):
#     # 历史会话
#     history_limit = 10
#     request = await request.json()
#     sessionId = request.get('sessionId')
#     query = request.get('query',None)
#     system = request.get('system','You are a helpful assistant.')
#     stream = request.get("stream",False)
#     user_stop_words=request.get("user_stop_words",[])
#     if query is None:
#         return Response(status_code=502,content='query is empty')
    

#     user_msg = MessageModel(session_id=request.get('sessionId'), role='user', content=query)
#     db.add(user_msg)
    
#     result = await db.execute(
#         MessageModel.select().where(MessageModel.session_id == sessionId).order_by(desc(MessageModel.created_at)).limit(history_limit * 2)
#     )
#     history = result.scalars().all()[::-1]
#     conversation_history = [(history[i].content, history[i+1].content) for i in range(0,len(history),2)]

#     # 构造成一个具体格式，然后调用本地的接口
#     # chat_local()

#     # response = OpenAI(api_key=os.getenv("OPENAI_API_KEY")).chat.completions.create(
#     #     model="gpt-3.5-turbo",
#     #     messages=conversation
#     # )
#     # gpt_reply = response['choices'][0]['message']['content']


#     assistant_msg = MessageModel(session_id=sessionId, role='assistant', content=text)
#     db.add(assistant_msg)
    
#     session = await db.get(SessionModel, sessionId)
#     if session:
#         session.updated_at = datetime.utcnow()
    
#     await db.commit()

# # 运行数据库初始化
# import asyncio
# asyncio.run(init_db())








# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8888)
