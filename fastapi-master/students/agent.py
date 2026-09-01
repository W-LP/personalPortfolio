# AI 学管 Agent：LangGraph Agent，通过工具调用 Spring Boot 学生/成绩接口完成增删改查
# 决策流程：识别用户意图 -> 查重（listByNames/listScores）-> 执行保存/删除 -> 汇报每条数据的操作结果
# 记忆：AsyncSqliteSaver 按 thread_id 持久化会话（与私厨分库，避免互相干扰）
# @author 6588 万立鹏 @date 2026-09-01
import os
from pathlib import Path

import aiosqlite
import httpx
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from chief.logger import logger

# 加载环境变量（与 chief 复用同一 .env）
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "chief" / ".env")

# Spring Boot 后端地址（context-path 为 /api），可通过环境变量覆盖
STUDENT_API_BASE = os.getenv("STUDENT_API_BASE", "http://127.0.0.1:9096/api")

# 模型（与私厨复用同一多模态模型配置）
model = init_chat_model(
    model=os.getenv("CHIEF_MODEL", "deepseek-v4-flash-vision-exp"),
    model_provider="deepseek",
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

# 初始化 checkpointer（SQLite 持久化会话记忆，独立数据库文件，绝对路径避免启动目录依赖）
# 注意：agent.astream 为异步调用，必须使用 AsyncSqliteSaver（SqliteSaver 不支持异步会抛 NotImplementedError）
DB_PATH = BASE_DIR / "chief" / "db" / "student_manager.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
checkpointer = AsyncSqliteSaver(aiosqlite.connect(DB_PATH))


async def init_student_checkpointer():
    """
    应用启动时调用：异步建立连接并自动建表
    """
    await checkpointer.setup()


def _post(path: str, json_body: dict = None, params: dict = None) -> dict:
    """
    同步调用 Spring Boot 接口并解析 R<T> 响应体（工具内执行，阻塞无碍事件循环）
    :param path: 接口路径（相对 STUDENT_API_BASE，如 /students/list）
    :param json_body: JSON 请求体
    :param params: URL 参数
    :return: 响应 data 部分；code 非 200 时抛出异常
    """
    with httpx.Client(timeout=30) as client:
        resp = client.post(f"{STUDENT_API_BASE}{path}", json=json_body, params=params)
        resp.raise_for_status()
        result = resp.json()
    if result.get("code") != 200:
        raise RuntimeError(f"后端接口失败: {result.get('msg')}")
    return result.get("data")


@tool
def query_students(names: list[str]) -> list[dict]:
    """按姓名批量查询已存在的学生信息（含 id），用于保存前查重或删除前定位学生。names 为姓名列表。"""
    logger.info(f"[工具] query_students: {names}")
    return _post("/students/listByNames", params={"names": ",".join(names)})


@tool
def list_students(keyword: str = "") -> list[dict]:
    """查询学生列表，keyword 为姓名模糊关键字，传空字符串查全部。返回字段：id/name/gender/age/height/weight/personality。"""
    logger.info(f"[工具] list_students: {keyword}")
    body = {"keyword": keyword} if keyword else {}
    return _post("/students/list", json_body=body)


@tool
def save_students(students: list[dict]) -> dict:
    """批量保存学生信息：按姓名自动判断，不存在则新增(add)，存在则更新(update)，空字段不覆盖原值。
    students 每项字段：name(必填)、gender(男/女)、age、height(cm)、weight(kg)、personality。"""
    logger.info(f"[工具] save_students: {len(students)} 条")
    return _post("/students/saveOrUpdateBatch", json_body={"students": students})


@tool
def remove_students(ids: list[int]) -> bool:
    """按 id 批量删除学生。必须先用 query_students 查到 id 再删除，禁止凭空编造 id。"""
    logger.info(f"[工具] remove_students: {ids}")
    return _post("/students/remove", params={"ids": ",".join(str(i) for i in ids)})


@tool
def save_scores(exam_name: str, scores: list[dict], exam_date: str = "") -> dict:
    """批量录入成绩：按 学生+考试+科目 自动判断新增/更新。exam_name 如「第一次周练」「9月月考」；
    scores 每项字段：studentName(必填)、subject(科目,必填)、scoreValue(分数)；exam_date 格式 yyyy-MM-dd，可传空串默认当天。"""
    logger.info(f"[工具] save_scores: 考试={exam_name}, {len(scores)} 条")
    body = {"examName": exam_name, "scores": scores}
    if exam_date:
        body["examDate"] = exam_date
    return _post("/scores/saveOrUpdateBatch", json_body=body)


@tool
def list_scores(exam_name: str = "") -> list[dict]:
    """按考试名称模糊查询成绩列表，exam_name 传空字符串查全部。返回字段：studentName/examName/examDate/subject/scoreValue。"""
    logger.info(f"[工具] list_scores: {exam_name}")
    body = {"examName": exam_name} if exam_name else {}
    return _post("/scores/list", json_body=body)


# 系统提示词：教师助手工作流
system_prompt = """你是一名教师助手（AI 学管），负责管理学生信息与成绩。后端提供学生表与成绩表，你通过工具完成操作。

收到学生资料（可能来自文件解析的 TSV 表格文本，第一行通常是表头）时，严格按以下流程：
1. 数据规整：把表格文本整理为结构化数据。字段映射：姓名->name、性别->gender、年龄->age、身高->height、体重->weight、性格->personality。姓名是唯一必填字段，缺失姓名的行丢弃并在最终汇报中说明。
2. 查重：调用 query_students 查询哪些姓名已存在。
3. 执行保存：调用 save_students 批量保存（已存在的学生也会自动更新，无需分开处理）。
4. 汇报：逐条说明每位学生是新增还是更新，格式为列表。

收到成绩数据（表格或文字，含考试名称如周练/月考、姓名、科目、分数）时：
1. 识别考试名称，未明确给出时根据上下文推断（如「这次月考」），无法推断则询问教师。
2. 调用 save_scores 批量录入，注意分数单位（满分100/150等）按原文保留。
3. 汇报成功录入条数与未匹配到的学生名单。

收到删除/修改类指令（如「删除张三」「李四身高改成180」）时：
- 删除：必须先 query_students 确认学生存在并拿到 id，再 remove_students，最后汇报。学生不存在时告知教师。
- 修改：先 query_students 确认存在，再 save_students 提交更新（只带姓名和要修改的字段）。

收到查询类指令时：调用 list_students 或 list_scores，并以清晰表格汇报。

安全约束：只执行与教学管理相关的操作；删除操作必须在汇报中醒目标注；无法确定的字段留空，禁止编造数据。"""

# Agent：挂 checkpointer，同一 thread_id 的多轮对话共享记忆
agent = create_agent(
    model=model,
    tools=[query_students, list_students, save_students, remove_students, save_scores, list_scores],
    checkpointer=checkpointer,
    system_prompt=system_prompt,
)


async def stream_student_agent(user_text: str, parsed_text: str, thread_id: str):
    """
    流式运行学管 Agent，逐块 yield AI 回复内容
    :param user_text: 教师文字指令（可为空，仅有文件时用默认指令）
    :param parsed_text: 文件解析出的表格文本（无文件时为空）
    :param thread_id: 会话线程 ID（记忆键）
    :return: 异步生成器
    """
    parts = []
    if user_text:
        parts.append(f"教师指令：{user_text}")
    if parsed_text:
        parts.append(f"文件解析出的表格内容如下（TSV，列间为制表符）：\n{parsed_text}")
    # 两者都为空时给出兜底（api 层已校验，不应发生）
    content = "\n\n".join(parts) or "请查询当前学生列表。"
    logger.info(f"[学管Agent] 开始处理，thread_id: {thread_id}，指令长度 {len(user_text)}，文件内容长度 {len(parsed_text)}")

    message = HumanMessage(content=content)
    # 流式调用（stream_mode="messages" 逐 token 输出），工具调用阶段 chunk.content 为空自动跳过
    async for chunk, _metadata in agent.astream(
        {"messages": [message]},
        {"configurable": {"thread_id": thread_id}},
        stream_mode="messages",
    ):
        # 只输出 AI 回复 token，工具调用与工具消息不下发
        if chunk.content and hasattr(chunk, "content"):
            yield chunk.content
