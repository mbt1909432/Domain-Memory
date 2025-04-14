import os
import time
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware
from uvicorn.config import LOGGING_CONFIG
import uvicorn

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Body, Header, FastAPI
from fastapi.responses import StreamingResponse

from core.exceptions import register_exception_handlers
from database.connector import close_connection, init_redis_pool
from schemas.agents.agents_schema import AgentResponseData
from utils.config import LOG, CONFIG
from llm_agents.llm_connect_checker import llm_connect_test#测试llm连接的
from core.response_model import Response

from llm_agents.agent_factory import get_chat_agent
from schemas.agents.profile.profile_schema import (
    ChatBlob, ProfileSummary, ChatRequest, UserProfiles,
    ProfileProcessResult
)
from llm_agents.agent_group.profile.agent_group import process_user_chat_and_update_profile

"""
uvicorn api:app --reload --host 0.0.0.0
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    LOG.info("lifespan start")
    init_redis_pool()
    result=await llm_connect_test()#添加应用开启时测试llm连通性功能
    LOG.info(str(result))
    yield
    await close_connection()
    LOG.info("lifespan close")



app = FastAPI(
    summary="ProLTM",
    version="0.01",
    title="ProLTM",
    lifespan=lifespan,
)

router = APIRouter(prefix="/app/v1", tags=["api"])



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头部
)


LOGGING_CONFIG["handlers"]["file"] = {
    "class": "logging.FileHandler",
    "filename": "logs/uvicorn.log",
    "formatter": "default",
}
LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"].append("file")

# 注册全局异常处理器
register_exception_handlers(app)


@app.get("/models", response_model=Response[List[Dict[str, Any]]])
async def get_available_models():
    available_models = CONFIG.get_available_models()
    return Response.success(data=available_models)



@app.post("/chat_stream", response_model=Response[AgentResponseData])
async def chat_stream(
        request: ChatRequest,
        memory_list: List[Dict[str, str]] = Body(default=[]),
        keep_memory: int = Body(default=5),
        model: Optional[str] = Header(None, description="要使用的模型ID"),
):
    """流式聊天接口，保留上下文"""
    agent = get_chat_agent()

    async def serialize_generator():
        async for item in agent.generate_stream(
                request,
                with_memory=True,
                memory_list=memory_list,
                keep_memory=keep_memory,
                model=model
        ):
            time.sleep(0.05)
            yield Response.success(item).model_dump_json() + "\n"

    return StreamingResponse(serialize_generator(), media_type="text/plain")


@app.post("/process_profile_from_chat", response_model=Response[ProfileProcessResult])
async def process_profile_from_chat(
    chat: ChatBlob,
    model: Optional[str] = Header(None, description="要使用的模型ID")
):
    """
    处理用户聊天并更新个人资料
    
    Args:
        chat: 用户聊天历史
        model: 可选的模型ID
        
    Returns:
        Response[ProfileProcessResult]: 处理结果，包含提取的新信息、更新的信息和组织后的资料
    """
    try:
        result = await process_user_chat_and_update_profile(chat)
        return Response.success(data=result)
    except Exception as e:
        LOG.error(f"处理用户聊天并更新个人资料时出错: {str(e)}")
        return Response.error(message=f"处理失败: {str(e)}")






if __name__ == "__main__":
    if not os.path.exists('logs'):
        os.makedirs('logs')
    uvicorn.run(app, host="127.0.0.1", port=8000)
