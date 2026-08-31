# 私厨 Agent：多模态识别食材 + web 搜索食谱 + 结构化推荐报告
# 迁移自 hello 项目 app/agents/personal_chief.py，并修复以下问题：
# 1. SQLite 改为基于本文件的绝对路径，不再依赖启动目录
# 2. 日志统一使用 chief.logger 的 personal_chief logger（原来误用 pip 的 logger 包）
# @author 万立鹏 @date 2026-08-31
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage, AIMessageChunk, AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from chief.logger import logger

# 1. 加载环境变量（.env 与本文件同目录）
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# 2. web 搜索工具，使用 tavily
web_search = TavilySearch(
    max_results=5,
    topic="general"
)

# 3. 多模态模型（deepseek 视觉模型，支持图片 + 文本）
model = init_chat_model(
    model=os.getenv("CHIEF_MODEL", "deepseek-v4-flash-vision-exp"),
    model_provider="deepseek",
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

# 4. 初始化 checkpointer（SQLite 持久化会话记忆，绝对路径避免启动目录依赖）
DB_PATH = BASE_DIR / "db" / "personal_chief.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
connection = sqlite3.connect(DB_PATH, check_same_thread=False)
checkpointer = SqliteSaver(connection)
# 自动建表
checkpointer.setup()

# 5. Agent 系统提示词
system_prompt = """
你是一名私人厨师。收到用户提供的食材照片或清单后，请按以下流程操作：
1.识别和评估食材：若用户提供照片，首先辨识所有可见食材。基于食材的外观状态，评估其新鲜度与可用量，整理出一份"当前可用食材清单"。
2.智能食谱检索：优先调用 web_search 工具，以"可用食材清单"为核心关键词，查找可行菜谱。
3.多维度评估与排序：从营养价值和制作难度两个维度对检索到的候选食谱进行量化打分，并根据得分排序，制作简单且营养丰富的排名靠前。
4.结构化方案输出：把排序后的食谱整理为一份结构清晰的建议报告，要包含食谱信息、得分、推荐理由、食谱的参考图片，帮助用户快速做出决策。

请严格按照流程，优先调用 web_search 工具搜索食谱，搜索不到的情况下才能自己发挥。
"""

# 6. 创建 Agent
agent = create_agent(
    model=model,            # 模型
    tools=[web_search],     # 工具
    checkpointer=checkpointer,  # 会话记忆
    system_prompt=system_prompt  # 系统提示词
)


async def search_recipes(prompt: str, image: str, thread_id: str):
    """
    流式调用 Agent 搜索食谱
    :param prompt: 用户文字输入
    :param image: 食材图片地址，可为空
    :param thread_id: 会话线程 ID
    :return: 异步生成器，逐块输出 AI 回复内容
    """
    logger.info(f"[用户]: {prompt}, image: {image}, thread_id: {thread_id}")
    try:
        # 判断是否有图片，封装不同格式的消息
        if not image or image.strip() == "":
            message = HumanMessage(content=prompt)
        else:
            message = HumanMessage(content=[
                {"type": "image", "url": image},
                {"type": "text", "text": prompt}
            ])

        # 流式调用 Agent（astream 异步迭代，不阻塞事件循环，保证逐块实时下发）
        async for chunk, metadata in agent.astream(
            {"messages": [message]},
            {"configurable": {"thread_id": thread_id}},
            stream_mode="messages"
        ):
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                # 兼容纯文本与多模态内容块两种格式
                if isinstance(chunk.content, str):
                    yield chunk.content
                elif isinstance(chunk.content, list):
                    # 多模态分块：提取其中的文本块
                    for block in chunk.content:
                        if isinstance(block, dict) and block.get("type") == "text" and block.get("text"):
                            yield block["text"]

    except Exception as e:
        logger.error(f"[错误]: {str(e)}")
        yield "信息检索失败，试试看手动输入食物列表？"


def clear_messages(thread_id: str):
    """
    清空指定线程的会话记忆
    :param thread_id: 会话线程 ID
    """
    logger.info(f"清空历史消息，thread_id: {thread_id}")
    checkpointer.delete_thread(thread_id)


def get_messages(thread_id: str) -> list[dict[str, str]]:
    """
    查询指定线程的会话历史
    :param thread_id: 会话线程 ID
    :return: 消息列表，元素为 {"role": "user"|"assistant", "content": "..."}
    """
    logger.info(f"获取历史消息，thread_id: {thread_id}")

    # 根据 thread_id 查询 checkpoint
    checkpoint = checkpointer.get({"configurable": {"thread_id": thread_id}})

    # 如果不存在，返回空列表
    if not checkpoint:
        return []

    # 安全获取 messages
    channel_values = checkpoint.get("channel_values")
    if not channel_values:
        return []

    messages = channel_values.get("messages", [])
    if not messages:
        return []

    # 转换消息格式，仅保留 user / assistant
    result = []
    for msg in messages:
        if not msg.content:
            continue

        if isinstance(msg, HumanMessage):
            result.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            result.append({"role": "assistant", "content": msg.content})

    return result
