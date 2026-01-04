"""
模型服务进程脚本
负责加载模型并通过ZeroMQ提供服务
"""
import os
import sys
import time
import signal
import zmq
import json
import uuid
import queue
import threading
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import logging

# 导入llama_cpp用于GGUF模型
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    logging.warning("llama_cpp not available, GGUF models will not be supported")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("model_service.log")
    ]
)
logger = logging.getLogger("model_service")

# 导入数据库模型
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.models import ModelRegistry, Base
from backend.db import get_db

# 全局变量
model = None
tokenizer = None
vllm_model = None
llama_model = None  # 用于GGUF模型
model_path = None
model_type = None
adapter_path = None
port = None
pid = os.getpid()

def identify_model_type(model_dir):
    """识别模型类型，返回模型类型和模型文件路径"""
    for f in os.listdir(model_dir):
        if f.endswith('.gguf'):
            return 'gguf', os.path.join(model_dir, f)
        elif f.endswith('.safetensors'):
            return 'safetensors', os.path.join(model_dir, f)
        elif f.endswith('.bin') or f.endswith('.pt') or f == 'pytorch_model.bin':
            return 'pytorch', os.path.join(model_dir, f)
    return 'unknown', None

# 请求队列和结果字典
request_queue = queue.Queue()
results = {}  # 存储生成结果: {request_id: {"status": "pending|completed|error", "result": result, "error": error}}
results_lock = threading.Lock()  # 保护结果字典的锁

# 队列处理线程是否运行
worker_running = True

def load_model():
    """加载模型"""
    global model, tokenizer, vllm_model, llama_model, model_path, model_type, adapter_path

    logger.info(f"加载模型: {model_path}, 类型: {model_type}")

    if model_type == "vllm":
        vllm_model = LLM(model_path, model_path, enable_lora=True)
        if adapter_path and adapter_path != "":
            lora_request = LoRARequest("load_adapter", 1, adapter_path)
            # 应用LoRA适配器
            logger.info(f"加载LoRA适配器: {adapter_path}")
    else:
        # 自动检测模型类型
        detected_type, detected_path = identify_model_type(model_path)
        logger.info(f"检测到模型类型: {detected_type}")

        if detected_type == "gguf" and LLAMA_CPP_AVAILABLE:
            # 加载GGUF模型
            logger.info(f"加载GGUF模型: {detected_path}")
            try:
                llama_model = Llama(
                    model_path=detected_path,
                    n_ctx=4096,  # 上下文长度
                    n_batch=512,  # 批处理大小
                    verbose=False
                )
                logger.info("GGUF模型加载完成")
            except Exception as e:
                logger.error(f"加载GGUF模型失败: {e}")
                raise
        else:
            # 使用transformers加载模型
            logger.info(f"使用Transformers加载模型: {model_path}")
            model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True, device_map="auto")
            tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True, device_map="auto")
            if adapter_path and adapter_path != "":
                logger.info(f"加载适配器: {adapter_path}")
                model.load_adapter(adapter_path)

    logger.info(f"模型加载完成: {model_path}")

def generate_text(request):
    """同步生成文本（直接返回结果）"""
    global model, tokenizer, vllm_model, llama_model, model_type

    try:
        prompt = request.get("prompt", "")
        max_length = request.get("max_length", 100)

        if model_type == "vllm":
            sampling_params = SamplingParams(
                max_tokens=max_length,
            )

            if "sampling_params" in request:
                # 使用自定义采样参数
                sampling_params = SamplingParams(**request["sampling_params"])

            if "lora_request" in request and adapter_path:
                lora_request = LoRARequest("load_adapter", 1, adapter_path)
                result = vllm_model.generate(prompt, sampling_params=sampling_params, lora_request=lora_request)[0].outputs[0].text
            else:
                result = vllm_model.generate(prompt, sampling_params=sampling_params)[0].outputs[0].text

        elif llama_model is not None:
            # 使用llama_cpp生成
            logger.info("使用GGUF模型生成文本")

            # 设置生成参数
            llama_params = {
                "max_tokens": max_length,
                "temperature": 0.7,
                "top_p": 0.9,
                "echo": request.get("echo", False)
            }

            # 如果有自定义参数，更新生成参数
            if "llama_params" in request:
                llama_params.update(request["llama_params"])

            # 生成文本
            output = llama_model(prompt, **llama_params)
            result = output["choices"][0]["text"]

        else:
            # 使用transformers生成
            logger.info("使用Transformers模型生成文本")
            input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)

            generate_args = {
                "max_length": len(input_ids[0]) + max_length,
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9,
            }

            if "generate_args" in request:
                # 使用自定义生成参数
                generate_args.update(request["generate_args"])

            output = model.generate(input_ids, **generate_args)
            result = tokenizer.decode(output[0], skip_special_tokens=True)

            # 如果不需要回显提示词
            if not request.get("echo", False):
                result = result[len(tokenizer.decode(input_ids[0], skip_special_tokens=True)):]

        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"生成文本时出错: {e}")
        return {"status": "error", "error": str(e)}

def process_request(request_id, request_data):
    """处理队列中的请求"""
    global results, results_lock

    try:
        # 生成文本
        result = generate_text(request_data)

        # 更新结果
        with results_lock:
            if result["status"] == "success":
                results[request_id] = {
                    "status": "completed",
                    "result": result["result"]
                }
            else:
                results[request_id] = {
                    "status": "error",
                    "error": result["error"]
                }
    except Exception as e:
        logger.error(f"处理请求 {request_id} 时出错: {e}")
        with results_lock:
            results[request_id] = {
                "status": "error",
                "error": str(e)
            }

def worker_thread():
    """工作线程，处理请求队列"""
    global worker_running, request_queue

    logger.info("启动工作线程")

    while worker_running:
        try:
            # 从队列获取请求（最多等待1秒）
            try:
                request_id, request_data = request_queue.get(timeout=1)
                logger.info(f"处理请求 {request_id}")

                # 处理请求
                process_request(request_id, request_data)

                # 标记任务完成
                request_queue.task_done()
                logger.info(f"请求 {request_id}处理完成")
            except queue.Empty:
                # 队列为空，继续循环
                time.sleep(1)
                logger.info(f"队列为空，继续循环")
                pass
        except Exception as e:
            logger.error(f"工作线程出错: {e}")

    logger.info("工作线程退出")

def check_ref_count():
    """检查引用计数，如果为0则退出服务"""
    db = get_db()
    try:
        stmt = select(ModelRegistry).where(ModelRegistry.model_path == model_path).with_for_update()
        model_record = db.execute(stmt).scalar_one_or_none()

        if model_record and model_record.ref_count <= 0:
            logger.info(f"引用计数为0，服务退出: {model_path}")
            db.commit()
            db.close()
            return True

        db.commit()
    except Exception as e:
        logger.error(f"检查引用计数时出错: {e}")
        db.rollback()
    finally:
        db.close()

    return False

def main():
    """主函数"""
    global model_path, model_type, adapter_path, port, pid, worker_running

    if len(sys.argv) < 5:
        logger.error("用法: python -m backend.model_service <model_path> <model_type> <adapter_path> <port>")
        sys.exit(1)

    model_path = sys.argv[1]
    model_type = sys.argv[2]
    adapter_path = sys.argv[3]
    port = int(sys.argv[4])

    logger.info(f"启动模型服务进程，PID: {pid}")
    logger.info(f"模型路径: {model_path}")
    logger.info(f"模型类型: {model_type}")
    logger.info(f"适配器路径: {adapter_path}")
    logger.info(f"服务端口: {port}")

    # 初始化ZeroMQ
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.setsockopt(zmq.LINGER, 0)  # 不等待关闭
    socket.bind(f"tcp://*:{port}")
    logger.info(f"ZeroMQ服务绑定到端口: {port}")

    # 加载模型
    try:
        load_model()
    except Exception as e:
        logger.error(f"加载模型失败: {e}")
        socket.close()
        context.term()
        sys.exit(1)

    # 启动工作线程
    worker = threading.Thread(target=worker_thread, daemon=True)
    worker.start()
    logger.info("工作线程已启动")

    global llama_model

    # 处理SIGTERM信号
    def handle_sigterm(signum, frame):
        global worker_running
        logger.info("收到SIGTERM信号，服务退出")
        worker_running = False  # 停止工作线程

        # 清理资源
        try:
            if 'llama_model' in globals() and llama_model is not None:
                del llama_model
        except Exception as e:
            logger.error(f"清理GGUF模型资源时出错: {e}")

        socket.close()
        context.term()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_sigterm)

    # 主循环
    last_check_time = time.time()
    check_interval = 60  # 每60秒检查一次引用计数

    while True:
        try:
            # 设置接收超时，允许定期检查引用计数
            socket.setsockopt(zmq.RCVTIMEO, 60000)  # 1分钟超时

            try:
                message = socket.recv_json()
                command = message.get("command", "")

                if command == "generate":
                    # 同步生成（直接处理）
                    if message.get("sync", False):
                        response = generate_text(message)
                        socket.send_json(response)
                    # 异步生成（加入队列）
                    else:
                        # 生成请求ID
                        request_id = str(uuid.uuid4())

                        # 将请求加入队列
                        with results_lock:
                            results[request_id] = {"status": "pending"}

                        request_queue.put((request_id, message))
                        logger.info(f"请求 {request_id} 已加入队列，当前队列长度: {request_queue.qsize()}")

                        # 返回请求ID
                        socket.send_json({
                            "status": "accepted",
                            "request_id": request_id,
                            "queue_position": request_queue.qsize()
                        })

                elif command == "check_status":
                    # 检查请求状态
                    request_id = message.get("request_id")
                    if not request_id:
                        socket.send_json({"status": "error", "error": "缺少请求ID"})
                        continue

                    with results_lock:
                        if request_id in results:
                            result_data = results[request_id]
                            socket.send_json({
                                "status": "success",
                                "request_status": result_data["status"],
                                "result": result_data.get("result", ""),
                                "error": result_data.get("error", "")
                            })

                            # 如果状态是已完成或错误，并且客户端已获取结果，可以清理结果
                            if result_data["status"] in ["completed", "error"]:
                                # 可选：清理结果，防止内存泄漏
                                del results[request_id]
                                pass
                        else:
                            socket.send_json({"status": "error", "error": "请求ID不存在"})

                elif command == "ping":
                    # 返回服务状态
                    socket.send_json({
                        "status": "success",
                        "message": "pong",
                        "queue_size": request_queue.qsize()
                    })

                else:
                    socket.send_json({"status": "error", "error": "未知命令"})
            except zmq.Again:
                # 超时，继续循环
                logger.error(f"处理请求超时，当前队列长度: {request_queue.qsize()}")
                pass
            except Exception as e:
                # 处理其他异常
                logger.error(f"处理请求时出错: {e}")
                try:
                    # 尝试发送错误响应
                    socket.send_json({"status": "error", "error": str(e)})
                except:
                    # 如果无法发送，忽略错误
                    pass

            # 定期检查引用计数
            current_time = time.time()
            if current_time - last_check_time > check_interval:
                if check_ref_count():
                    # 引用计数为0，退出服务
                    logger.info("引用计数为0，服务退出")
                    db = get_db()
                    model_record = db.query(ModelRegistry).filter(ModelRegistry.model_path == model_path).first()
                    if model_record:
                        model_record.loading_status = 0
                        db.commit()

                    # 停止工作线程
                    worker_running = False
                    worker.join(timeout=5)  # 等待工作线程结束

                    # 清理GGUF模型资源
                    try:
                        if 'llama_model' in globals() and llama_model is not None:
                            del llama_model
                    except Exception as e:
                        logger.error(f"清理GGUF模型资源时出错: {e}")

                    socket.close()
                    context.term()
                    sys.exit(0)
                last_check_time = current_time

        except KeyboardInterrupt:
            logger.info("收到中断信号，服务退出")
            db = get_db()
            model_record = db.query(ModelRegistry).filter(ModelRegistry.model_path == model_path).first()
            if model_record:
                model_record.loading_status = 0
                db.commit()

            # 停止工作线程
            worker_running = False
            worker.join(timeout=5)  # 等待工作线程结束

            # 清理GGUF模型资源
            try:
                if 'llama_model' in globals() and llama_model is not None:
                    del llama_model
            except Exception as e:
                logger.error(f"清理GGUF模型资源时出错: {e}")

            socket.close()
            context.term()
            sys.exit(0)
        except Exception as e:
            logger.error(f"服务运行时出错: {e}")
            # 如果是引用计数为0的情况下出错，尝试强制退出
            try:
                db = get_db()
                stmt = select(ModelRegistry).where(ModelRegistry.model_path == model_path)
                model_record = db.execute(stmt).scalar_one_or_none()

                if model_record and model_record.ref_count <= 0:
                    logger.info("检测到引用计数为0且出现错误，强制退出服务")
                    socket.close()
                    context.term()
                    sys.exit(0)
                db.close()
            except Exception as exit_error:
                logger.error(f"尝试强制退出时出错: {exit_error}")
            # 继续运行，不退出

if __name__ == "__main__":
    main()
