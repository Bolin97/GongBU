from backend.llmw import LLMW, OpenAIChatCompletionRequest
from pydantic import BaseModel
from typing import Optional, List, Dict, Union

def create_openai_router(llmw: LLMW, use_vllm: bool):
    from fastapi import APIRouter

    openai_router = APIRouter()

    # POST https://api.openai.com/v1/chat/completions
    @openai_router.post("/v1/chat/completions")
    async def create_chat_completion(request: OpenAIChatCompletionRequest):
        return llmw.openai_chat_completion(request)

    return openai_router
    