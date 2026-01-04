"""
测试模型服务进程
"""
import os
import sys
import time
import logging
import zmq
from backend.llmw import LLMW

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_model_service")

def test_single_instance():
    """测试单个实例"""
    logger.info("=== 测试单个实例 ===")

    # 创建LLMW实例
    model_path = "/models/Qwen2-7B-Instruct"  # 替换为实际的模型路径
    llm = LLMW(model_path, adapter_path=None, use_vllm=False)

    try:
        # 加载模型
        logger.info("加载模型...")
        llm.load()

        # 同步生成文本
        logger.info("同步生成文本...")
        prompt = "Hello, I am a language model. "
        result = llm.simple_generation(prompt, 50, sync=True)
        logger.info(f"同步生成结果: {result}")

        # 异步生成文本
        logger.info("异步生成文本...")
        prompt = "Tell me a short story about a cat. "
        result = llm.simple_generation(prompt, 100, timeout=600)  # 10分钟超时
        logger.info(f"异步生成结果: {result}")

        # 释放模型
        logger.info("释放模型...")
        llm.release()

        logger.info("测试成功")
    except Exception as e:
        logger.error(f"测试失败: {e}")
        if hasattr(llm, 'release'):
            llm.release()

def test_multiple_instances():
    """测试多个实例"""
    logger.info("=== 测试多个实例 ===")

    # 创建多个LLMW实例
    model_path = "/models/Qwen2-7B-Instruct"  # 替换为实际的模型路径
    llm1 = LLMW(model_path, adapter_path=None, use_vllm=False)
    llm2 = LLMW(model_path, adapter_path=None, use_vllm=False)

    try:
        # 加载第一个模型
        logger.info("加载第一个模型...")
        llm1.load()

        # 生成文本
        logger.info("使用第一个模型生成文本...")
        prompt = "Hello, I am a language model. "
        result1 = llm1.simple_generation(prompt, 50)
        logger.info(f"第一个模型生成结果: {result1}")

        # 加载第二个模型（应该连接到同一个服务进程）
        logger.info("加载第二个模型...")
        llm2.load()

        # 生成文本
        logger.info("使用第二个模型生成文本...")
        prompt = "Tell me a short story about a cat. "
        result2 = llm2.simple_generation(prompt, 100)
        logger.info(f"第二个模型生成结果: {result2}")

        # 释放第一个模型
        logger.info("释放第一个模型...")
        llm1.release()

        # 使用第二个模型再次生成文本
        logger.info("使用第二个模型再次生成文本...")
        prompt = "What is the capital of France? "
        result3 = llm2.simple_generation(prompt, 30)
        logger.info(f"第二个模型再次生成结果: {result3}")

        # 释放第二个模型
        logger.info("释放第二个模型...")
        llm2.release()

        logger.info("测试成功")
    except Exception as e:
        logger.error(f"测试失败: {e}")
        if hasattr(llm1, 'release'):
            llm1.release()
        if hasattr(llm2, 'release'):
            llm2.release()

def test_reference_counting():
    """测试引用计数"""
    logger.info("=== 测试引用计数 ===")

    # 创建多个LLMW实例
    model_path = "/models/Qwen2-7B-Instruct"  # 替换为实际的模型路径
    llm1 = LLMW(model_path, adapter_path=None, use_vllm=False)
    llm2 = LLMW(model_path, adapter_path=None, use_vllm=False)
    llm3 = LLMW(model_path, adapter_path=None, use_vllm=False)

    try:
        # 加载所有模型
        logger.info("加载所有模型...")
        llm1.load()
        llm2.load()
        llm3.load()

        # 生成文本
        logger.info("使用第一个模型生成文本...")
        result = llm1.simple_generation("Hello, world!", 20)
        logger.info(f"生成结果: {result}")

        # 释放第一个模型
        logger.info("释放第一个模型...")
        llm1.release()

        # 释放第二个模型
        logger.info("释放第二个模型...")
        llm2.release()

        # 使用第三个模型生成文本
        logger.info("使用第三个模型生成文本...")
        result = llm3.simple_generation("How are you?", 20)
        logger.info(f"生成结果: {result}")

        # 释放第三个模型（引用计数应该为0，服务进程应该退出）
        logger.info("释放第三个模型...")
        llm3.release()

        # 等待一段时间，让服务进程有时间退出
        logger.info("等待服务进程退出...")
        time.sleep(10)

        # 重新加载模型（应该启动新的服务进程）
        logger.info("重新加载模型...")
        llm1 = LLMW(model_path, adapter_path=None, use_vllm=False)
        llm1.load()

        # 生成文本
        logger.info("使用新加载的模型生成文本...")
        result = llm1.simple_generation("Tell me a joke.", 50)
        logger.info(f"生成结果: {result}")

        # 释放模型
        logger.info("释放模型...")
        llm1.release()

        logger.info("测试成功")
    except Exception as e:
        logger.error(f"测试失败: {e}")
        if hasattr(llm1, 'release'):
            llm1.release()
        if hasattr(llm2, 'release'):
            llm2.release()
        if hasattr(llm3, 'release'):
            llm3.release()

def test_async_queue():
    """测试异步队列"""
    logger.info("=== 测试异步队列 ===")

    # 创建LLMW实例
    model_path = "/models/Qwen2-7B-Instruct"  # 替换为实际的模型路径
    llm = LLMW(model_path, adapter_path=None, use_vllm=False)

    try:
        # 加载模型
        logger.info("加载模型...")
        llm.load()

        # 提交多个异步请求
        requests = []
        results = []

        # 提交5个请求
        for i in range(5):
            prompt = f"Write a short paragraph about topic {i+1}: "
            if i == 0:
                prompt += "cats"
            elif i == 1:
                prompt += "dogs"
            elif i == 2:
                prompt += "birds"
            elif i == 3:
                prompt += "fish"
            else:
                prompt += "rabbits"

            logger.info(f"提交异步请求 {i+1}...")
            # 这里不等待结果，只获取请求ID
            request = {
                "command": "generate",
                "prompt": prompt,
                "max_length": 100,
                "sync": False
            }

            # 设置超时
            llm.zmq_socket.setsockopt(zmq.RCVTIMEO, 60000)  # 60秒接收超时
            llm.zmq_socket.setsockopt(zmq.SNDTIMEO, 5000)   # 5秒发送超时

            # 发送请求
            llm.zmq_socket.send_json(request)

            # 接收响应
            response = llm.zmq_socket.recv_json()

            if response.get("status") == "accepted":
                request_id = response.get("request_id")
                queue_position = response.get("queue_position", 0)
                logger.info(f"请求 {i+1} 已接受，ID: {request_id}，队列位置: {queue_position}")
                requests.append(request_id)
            else:
                logger.error(f"请求 {i+1} 失败: {response.get('error', '未知错误')}")

        # 等待所有请求完成
        for i, request_id in enumerate(requests):
            logger.info(f"等待请求 {i+1} 完成...")
            result = llm._wait_for_result(request_id, timeout=1200)  # 20分钟超时
            results.append(result)
            logger.info(f"请求 {i+1} 完成，结果长度: {len(result)}")

        # 显示所有结果
        for i, result in enumerate(results):
            logger.info(f"请求 {i+1} 结果: {result[:100]}...")

        # 释放模型
        logger.info("释放模型...")
        llm.release()

        logger.info("测试成功")
    except Exception as e:
        logger.error(f"测试失败: {e}")
        if hasattr(llm, 'release'):
            llm.release()

if __name__ == "__main__":
    # 运行测试
    test_single_instance()
    test_multiple_instances()
    test_reference_counting()
    test_async_queue()

