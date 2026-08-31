# 私厨接口出入参模型
# @author 万立鹏 @date 2026-08-31
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """流式对话请求体"""
    message: str = Field(min_length=1, description="用户输入的文字内容")
    image_url: Optional[str] = Field(default=None, description="食材图片的公网地址，可选")
    thread_id: str = Field(min_length=1, description="会话线程 ID，用于记忆隔离")
