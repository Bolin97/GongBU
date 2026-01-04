import time
import os
import socket
import subprocess
import threading
import zmq
import torch
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Any, Dict, Optional, List, Union
from transformers.utils.dummy_pt_objects import StoppingCriteria
from transformers.generation.stopping_criteria import StoppingCriteriaList
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError
from datetime import datetime, timezone
import logging
from backend.db import get_db
from backend.models import ModelRegistry

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("llmw")

input_prompt_template = '''Task Overview:
You are a data science expert. Below, you are provided with a database schema and a natural language question. Your task is to understand the schema and generate a valid SQL query to answer the question.

Database Engine:
SQLite

Database Schema:
{db_details}
This schema describes the database's structure, including tables, columns, primary keys, foreign keys, and any relevant relationships or constraints.

Question:
{question}

Instructions:
- Make sure you only output the information that is asked in the question. If the question asks for a specific column, make sure to only include that column in the SELECT clause, nothing more.
- The generated query should return all of the information asked in the question without any missing or extra information.
- Before generating the final SQL query, please think through the steps of how to write the query.

Output Format:
In your answer, please enclose the generated SQL query in a code block:
```
-- Your SQL query
```

Take a deep breath and think step by step to find the correct SQL query.'''


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

# 全局变量
_zmq_context = zmq.Context()  # ZeroMQ上下文
_lock_timeout = 360  # 数据库锁超时时间（秒）
_connection_timeout = 300  # ZeroMQ连接超时时间（秒）
_service_check_interval = 5  # 服务检查间隔（秒）


# 辅助函数
def find_available_port():
    """查找可用端口"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


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
        # for message in messages:
        #     if isinstance(message, str):
        #         result.append(message)
        #     elif isinstance(message, dict):
        #         if "role" in message:
        #             result.append(
        #                 f"{message['role']}" + tokenizer.eos_token + f"{message['content']}"
        #             )
        #     else:
        #         result.append(str(message))
        # return tokenizer.eos_token.join(result)
        for message in messages:
            if isinstance(message, dict):
                prompt = input_prompt_template.format(
                    db_details=message[0]["db_details"],
                    question=message[1]["question"]
                )
        return prompt

    def __init__(self, base_model_path: str, adapter_path: str, use_vllm: bool = False, use_deepspeed: bool = False):
        self.base_model_path = base_model_path
        self.adapter_path = adapter_path if adapter_path else ""
        self.loaded = False
        self.use_vllm = use_vllm
        self.use_deepspeed = use_deepspeed

        # 确定模型类型 - 只需要区分vllm和非vllm
        # 非vllm的情况下，model_service.py会自动检测是gguf还是transformers
        self.model_type = "vllm" if use_vllm else "transformers"

        self.zmq_socket = None
        self.service_port = None
        self.service_pid = None

    def load(self):
        """加载模型或连接到模型服务进程"""
        global _zmq_context, _lock_timeout, _connection_timeout

        # 获取数据库连接
        db = get_db()
        try:
            # 开始事务
            db.begin()

            # 1. 先插入占位记录（如果不存在）
            db.execute(text("""
                INSERT INTO model_registry (model_path, model_type, loading_status, ref_count, last_used, created_at)
                VALUES (:path, :model_type, 0, 0, :now, :now)
                ON CONFLICT (model_path) DO NOTHING
            """), {
                "path": self.base_model_path,
                "model_type": self.model_type,
                "now": datetime.now(timezone.utc)
            })

            # 2. 设置锁超时并加锁获取记录
            db.execute(text(f"SET LOCAL lock_timeout = '{_lock_timeout}s';"))
            stmt = select(ModelRegistry).where(ModelRegistry.model_path == self.base_model_path).with_for_update()
            model_record = db.execute(stmt).scalar_one()  # 使用scalar_one确保记录存在

            if model_record.loading_status == 0:
                # 模型未加载，启动新的服务进程
                logger.info(f"模型 {self.base_model_path} 未加载，启动新的服务进程")

                # 查找可用端口
                port = find_available_port()
                logger.info(f"找到可用端口: {port}")

                # 更新记录状态为"正在加载"
                model_record.loading_status = 1  # 1=已加载
                model_record.ref_count = 1
                model_record.service_port = port
                model_record.last_used = datetime.now(timezone.utc)
                db.flush()

                # 启动服务进程
                try:
                    # 构建命令
                    cmd = [
                        "python", "-m", "backend.model_service",
                        self.base_model_path, self.model_type, self.adapter_path, str(port)
                    ]
                    # preexec_fn=os.setsid 是 subprocess.Popen 的一个参数用法，意思是：
                    # 在启动子进程 之前，执行 os.setsid() 这个函数。
                    # os.setsid() 的作用是让当前进程：
                    # 创建一个新的会话（session）
                    # 成为该会话的首进程（session leader）
                    # 脱离原来的控制终端（终端断开不会影响它）
                    # 从原有的进程组中脱离，创建新的进程组
                    # 简单说：它可以让子进程“自立门户”，不会因为父进程退出或 tmux 被杀而受到影响。
                    # 启动进程
                    process = subprocess.Popen(cmd, preexec_fn=os.setsid)
                    logger.info(f"启动模型服务进程，PID: {process.pid}")

                    # 更新进程ID
                    model_record.process_id = process.pid
                    self.service_pid = process.pid

                    # 等待服务启动
                    self.service_port = port
                    self.zmq_socket = _zmq_context.socket(zmq.REQ)
                    self.zmq_socket.setsockopt(zmq.LINGER, 0)  # 不等待关闭
                    self.zmq_socket.connect(f"tcp://localhost:{port}")

                    # 等待服务就绪
                    start_time = time.time()
                    connected = False

                    while time.time() - start_time < _connection_timeout:
                        try:
                            # 关闭之前的套接字（如果存在）
                            if hasattr(self, 'zmq_socket') and self.zmq_socket:
                                self.zmq_socket.close()

                            # 创建新的套接字
                            logger.info(f"尝试连接到服务 (端口: {port})...")
                            self.zmq_socket = _zmq_context.socket(zmq.REQ)
                            self.zmq_socket.setsockopt(zmq.LINGER, 0)  # 不等待关闭
                            self.zmq_socket.setsockopt(zmq.RCVTIMEO, 2000)  # 2秒接收超时
                            self.zmq_socket.setsockopt(zmq.SNDTIMEO, 2000)  # 2秒发送超时
                            self.zmq_socket.connect(f"tcp://localhost:{port}")

                            # 发送ping请求
                            self.zmq_socket.send_json({"command": "ping"})

                            # 接收响应
                            response = self.zmq_socket.recv_json()
                            if response.get("status") == "success":
                                logger.info("服务连接成功")
                                connected = True
                                break

                            time.sleep(2)
                        except zmq.Again:
                            logger.info("等待服务响应...")
                            time.sleep(2)
                        except Exception as e:
                            logger.error(f"连接服务时出错: {e}")
                            time.sleep(2)

                    if not connected:
                        # 连接失败，更新状态
                        model_record.loading_status = 0
                        model_record.ref_count = 0
                        # 提交事务以释放锁
                        db.commit()
                        raise Exception(f"服务启动超时 (端口: {port})")

                    self.loaded = True

                except Exception as e:
                    # 启动失败，更新状态
                    model_record.loading_status = 0
                    model_record.ref_count = 0
                    logger.error(f"启动服务进程失败: {e}")
                    # 提交事务以释放锁
                    db.commit()
                    raise Exception(f"启动模型服务进程失败: {e}")
            else:
                # 模型已加载，增加引用计数
                logger.info(f"模型 {self.base_model_path} 已加载，连接到现有服务")
                model_record.ref_count += 1
                model_record.last_used = datetime.now(timezone.utc)

                # 连接到现有服务
                self.service_port = model_record.service_port
                self.service_pid = model_record.process_id

                # 创建ZMQ连接
                self.zmq_socket = _zmq_context.socket(zmq.REQ)
                self.zmq_socket.setsockopt(zmq.LINGER, 0)  # 不等待关闭
                self.zmq_socket.connect(f"tcp://localhost:{self.service_port}")

                # 测试连接
                try:
                    # 设置超时
                    self.zmq_socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5秒接收超时
                    self.zmq_socket.setsockopt(zmq.SNDTIMEO, 5000)  # 5秒发送超时

                    logger.info(f"测试连接到服务 (端口: {self.service_port})...")
                    self.zmq_socket.send_json({"command": "ping"})

                    # 直接接收响应
                    response = self.zmq_socket.recv_json()
                    if response.get("status") != "success":
                        raise Exception("服务响应错误")

                    logger.info("服务连接成功")
                    self.loaded = True
                except Exception as e:
                    # 连接失败，可能服务已崩溃
                    logger.error(f"连接服务失败: {e}")

                    # 尝试重启服务
                    try:
                        # 关闭现有连接
                        if self.zmq_socket:
                            self.zmq_socket.close()

                        # 更新状态
                        model_record.loading_status = 0
                        # 提交当前事务以释放锁
                        db.commit()
                        db.close()

                        # 重新加载
                        logger.info("尝试重启服务...")
                        self.load()
                        return
                    except Exception as restart_error:
                        logger.error(f"重启服务失败: {restart_error}")
                        raise Exception(f"连接模型服务失败: {e}")

            # 提交事务，只有在模型成功加载或连接后才释放锁
            db.commit()
            logger.info(f"模型 {self.base_model_path} 加载成功")
        except OperationalError as e:
            db.rollback()
            logger.error(f"数据库锁超时: {e}")
            raise Exception(f"模型 {self.base_model_path} 正在被其他进程加载，请稍后重试")
        except Exception as e:
            db.rollback()
            logger.error(f"加载模型时出错: {e}")
            raise
        finally:
            db.close()

    def simple_generation(self, prompt: str, max_length: int, timeout: int = 3600, sync: bool = False):
        """通过ZeroMQ发送生成请求到模型服务进程

        Args:
            prompt: 提示词
            max_length: 最大生成长度
            timeout: 超时时间（秒），默认1小时
            sync: 是否同步执行，默认异步

        Returns:
            生成的文本
        """
        if not self.loaded or not self.zmq_socket:
            raise Exception("模型未加载")

        # 构建请求
        request = {
            "command": "generate",
            "prompt": prompt,
            "max_length": max_length,
            "sync": sync  # 是否同步执行
        }

        # 添加模型特定参数
        if self.use_vllm:
            request["sampling_params"] = {
                "max_tokens": max_length,
                "temperature": 0.7,
                "top_p": 0.9
            }
        else:
            # 添加两种可能的参数，让model_service.py根据实际加载的模型类型选择使用
            # 为GGUF模型添加参数
            request["llama_params"] = {
                "max_tokens": max_length,
                "temperature": 0.7,
                "top_p": 0.9,
                "echo": False
            }
            # 为Transformers模型添加参数
            request["generate_args"] = {
                "max_length": max_length,
                "max_new_tokens": max_length,
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9
            }

        # 发送请求
        try:
            logger.info(f"发送生成请求: {prompt[:50]}...")

            # 设置超时
            self.zmq_socket.setsockopt(zmq.RCVTIMEO, 60000)  # 60秒接收超时
            self.zmq_socket.setsockopt(zmq.SNDTIMEO, 5000)   # 5秒发送超时

            # 发送请求
            self.zmq_socket.send_json(request)

            # 接收响应
            response = self.zmq_socket.recv_json()

            # 同步模式
            if sync:
                if response.get("status") == "success":
                    return response.get("result", "")
                else:
                    error = response.get("error", "未知错误")
                    logger.error(f"生成失败: {error}")
                    raise Exception(f"生成失败: {error}")

            # 异步模式
            else:
                if response.get("status") == "accepted":
                    request_id = response.get("request_id")
                    queue_position = response.get("queue_position", 0)
                    logger.info(f"请求已接受，ID: {request_id}，队列位置: {queue_position}")

                    # 等待结果
                    return self._wait_for_result(request_id, timeout)
                else:
                    error = response.get("error", "未知错误")
                    logger.error(f"请求失败: {error}")
                    raise Exception(f"请求失败: {error}")

        except zmq.Again:
            logger.error("生成请求超时")
            raise Exception("生成请求超时")
        except Exception as e:
            logger.error(f"生成请求出错: {e}")

            # 尝试重新连接
            try:
                logger.info("尝试重新连接服务...")
                if hasattr(self, 'zmq_socket') and self.zmq_socket:
                    self.zmq_socket.close()

                self.zmq_socket = _zmq_context.socket(zmq.REQ)
                self.zmq_socket.setsockopt(zmq.LINGER, 0)
                self.zmq_socket.setsockopt(zmq.RCVTIMEO, 5000)
                self.zmq_socket.setsockopt(zmq.SNDTIMEO, 5000)
                self.zmq_socket.connect(f"tcp://localhost:{self.service_port}")

                # 重新发送请求
                self.zmq_socket.send_json({"command": "ping"})
                response = self.zmq_socket.recv_json()

                if response.get("status") == "success":
                    logger.info("重新连接成功，重试请求...")
                    return self.simple_generation(prompt, max_length, timeout, sync)
            except Exception as reconnect_error:
                logger.error(f"重新连接失败: {reconnect_error}")

            raise Exception(f"生成请求出错: {e}")

    def _wait_for_result(self, request_id: str, timeout: int = 3600):
        """等待异步请求结果

        Args:
            request_id: 请求ID
            timeout: 超时时间（秒）

        Returns:
            生成的文本
        """
        start_time = time.time()
        check_interval = 20  # 每20秒检查一次

        while time.time() - start_time < timeout:
            try:
                # 设置超时
                self.zmq_socket.setsockopt(zmq.RCVTIMEO, 3600000)  # 50秒接收超时
                self.zmq_socket.setsockopt(zmq.SNDTIMEO, 5000)   # 5秒发送超时

                # 发送状态检查请求
                self.zmq_socket.send_json({
                    "command": "check_status",
                    "request_id": request_id
                })

                # 接收响应
                response = self.zmq_socket.recv_json()

                if response.get("status") == "success":
                    request_status = response.get("request_status")

                    # 请求已完成
                    if request_status == "completed":
                        logger.info(f"请求 {request_id} 处理完成")
                        return response.get("result", "")

                    # 请求出错
                    elif request_status == "error":
                        error = response.get("error", "未知错误")
                        logger.error(f"生成失败: {error}")
                        raise Exception(f"生成失败: {error}")

                    # 请求仍在处理中
                    elif request_status == "pending":
                        elapsed = int(time.time() - start_time)
                        logger.info(f"请求 {request_id} 仍在处理中，已等待 {elapsed} 秒...")
                        time.sleep(check_interval)

                    else:
                        logger.warning(f"未知的请求状态: {request_status}")
                        time.sleep(check_interval)

                else:
                    error = response.get("error", "未知错误")
                    logger.error(f"检查状态失败: {error}")
                    time.sleep(check_interval)

            except zmq.Again:
                logger.warning("检查状态超时，重试...")
                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"检查状态出错: {e}")

                # 尝试重新连接
                try:
                    logger.info("尝试重新连接服务...")
                    if hasattr(self, 'zmq_socket') and self.zmq_socket:
                        self.zmq_socket.close()

                    self.zmq_socket = _zmq_context.socket(zmq.REQ)
                    self.zmq_socket.setsockopt(zmq.LINGER, 0)
                    self.zmq_socket.setsockopt(zmq.RCVTIMEO, 5000)
                    self.zmq_socket.setsockopt(zmq.SNDTIMEO, 5000)
                    self.zmq_socket.connect(f"tcp://localhost:{self.service_port}")
                except Exception as reconnect_error:
                    logger.error(f"重新连接失败: {reconnect_error}")

                time.sleep(check_interval)

        # 超时
        raise Exception(f"等待请求 {request_id} 结果超时，已等待 {timeout} 秒")

    def advanced_generation(self, prompt: str, timeout: int = 3600, sync: bool = False, **kwargs):
        """高级生成，支持自定义参数

        Args:
            prompt: 提示词
            timeout: 超时时间（秒），默认1小时
            sync: 是否同步执行，默认异步
            **kwargs: 模型特定参数

        Returns:
            生成的文本
        """
        if not self.loaded or not self.zmq_socket:
            raise Exception("模型未加载")

        # 构建请求
        request = {
            "command": "generate",
            "prompt": prompt,
            "sync": sync  # 是否同步执行
        }

        # 添加模型特定参数
        if self.use_vllm:
            request["sampling_params"] = kwargs
        else:
            # 添加两种可能的参数，让model_service.py根据实际加载的模型类型选择使用
            request["llama_params"] = kwargs  # 为GGUF模型添加参数
            request["generate_args"] = kwargs  # 为Transformers模型添加参数

        # 发送请求
        try:
            logger.info(f"发送高级生成请求: {prompt[:50]}...")

            # 设置超时
            self.zmq_socket.setsockopt(zmq.RCVTIMEO, 60000)  # 60秒接收超时
            self.zmq_socket.setsockopt(zmq.SNDTIMEO, 5000)   # 5秒发送超时

            # 发送请求
            self.zmq_socket.send_json(request)

            # 接收响应
            response = self.zmq_socket.recv_json()

            # 同步模式
            if sync:
                if response.get("status") == "success":
                    return response.get("result", "")
                else:
                    error = response.get("error", "未知错误")
                    logger.error(f"生成失败: {error}")
                    raise Exception(f"生成失败: {error}")

            # 异步模式
            else:
                if response.get("status") == "accepted":
                    request_id = response.get("request_id")
                    queue_position = response.get("queue_position", 0)
                    logger.info(f"请求已接受，ID: {request_id}，队列位置: {queue_position}")

                    # 等待结果
                    return self._wait_for_result(request_id, timeout)
                else:
                    error = response.get("error", "未知错误")
                    logger.error(f"请求失败: {error}")
                    raise Exception(f"请求失败: {error}")

        except zmq.Again:
            logger.error("生成请求超时")
            raise Exception("生成请求超时")
        except Exception as e:
            logger.error(f"生成请求出错: {e}")

            # 尝试重新连接
            try:
                logger.info("尝试重新连接服务...")
                if hasattr(self, 'zmq_socket') and self.zmq_socket:
                    self.zmq_socket.close()

                self.zmq_socket = _zmq_context.socket(zmq.REQ)
                self.zmq_socket.setsockopt(zmq.LINGER, 0)
                self.zmq_socket.setsockopt(zmq.RCVTIMEO, 5000)
                self.zmq_socket.setsockopt(zmq.SNDTIMEO, 5000)
                self.zmq_socket.connect(f"tcp://localhost:{self.service_port}")

                # 重新发送请求
                self.zmq_socket.send_json({"command": "ping"})
                response = self.zmq_socket.recv_json()

                if response.get("status") == "success":
                    logger.info("重新连接成功，重试请求...")
                    return self.advanced_generation(prompt, timeout, sync, **kwargs)
            except Exception as reconnect_error:
                logger.error(f"重新连接失败: {reconnect_error}")

            raise Exception(f"生成请求出错: {e}")

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

    def __del__(self):
        """当对象被销毁时释放模型"""
        if hasattr(self, 'base_model_path') and hasattr(self, 'loaded') and self.loaded:
            self.release()

    def release(self):
        """释放模型，减少引用计数"""
        if not hasattr(self, 'base_model_path') or not hasattr(self, 'loaded') or not self.loaded:
            return

        # 关闭ZMQ连接
        if hasattr(self, 'zmq_socket') and self.zmq_socket:
            self.zmq_socket.close()
            self.zmq_socket = None

        # 获取数据库连接
        db = get_db()
        try:
            # 开始事务
            db.begin()

            # 获取模型记录
            stmt = select(ModelRegistry).where(ModelRegistry.model_path == self.base_model_path).with_for_update()
            model_record = db.execute(stmt).scalar_one_or_none()

            if model_record:
                # 减少引用计数
                model_record.ref_count -= 1
                logger.info(f"模型 {self.base_model_path} 引用计数减少为 {model_record.ref_count}")

                # 如果引用计数为0，服务进程会自行检查并退出
                if model_record.ref_count <= 0:
                    logger.info(f"模型 {self.base_model_path} 引用计数为0，服务进程将自行退出")

            # 提交事务
            db.commit()

            # 标记为未加载
            self.loaded = False
            logger.info(f"模型 {self.base_model_path} 已释放")
        except Exception as e:
            db.rollback()
            logger.error(f"释放模型时发生错误: {e}")
        finally:
            db.close()
