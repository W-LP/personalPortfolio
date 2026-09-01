# 私厨对话接口：流式对话 / 查询历史 / 清空会话
# @author 万立鹏 @date 2026-08-31
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from chief.agent import search_recipes, get_messages, clear_messages
from chief.logger import logger
from chief.schemas import ChatRequest

router = APIRouter()


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式对话：接收用户消息（可选食材图片），流式返回 AI 食谱建议
    """
    return StreamingResponse(
        search_recipes(request.message, request.image_url, request.thread_id),
        media_type="text/event-stream",
        # 禁用各级缓冲，保证流式实时下发（X-Accel-Buffering 供 Nginx 反代场景）
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/chat/messages")
async def get_chat_messages(thread_id: str):
    """
    查询指定线程的历史消息
    """
    messages = await get_messages(thread_id)
    return {"messages": messages}


@router.delete("/chat/messages")
async def clear_chat_messages(thread_id: str):
    """
    清空指定线程的历史消息
    """
    logger.info(f"接口调用清空会话，thread_id: {thread_id}")
    await clear_messages(thread_id)
    return {"success": True}
