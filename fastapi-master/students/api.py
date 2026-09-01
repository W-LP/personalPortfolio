# AI 学管路由：接收教师上传的文件 + 文字指令，流式返回 Agent 处理结果
# @author 6588 万立鹏 @date 2026-09-01
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from chief.logger import logger
from students.agent import stream_student_agent
from students.parser import SUPPORTED_SUFFIX, parse_file

router = APIRouter()

# 上传文件大小限制：20MB
MAX_FILE_SIZE = 20 * 1024 * 1024


@router.post("/stream")
async def student_agent_stream(
    text: str = Form(default=""),
    thread_id: str = Form(...),
    file: UploadFile | None = File(default=None),
):
    """
    学管 Agent 流式入口：文件（word/excel/图片）与文字指令至少提供其一，
    Agent 自动解析内容并调用 Spring Boot 接口完成增删改查，流式返回处理汇报
    :param text: 教师文字指令，可为空
    :param thread_id: 会话线程 ID（记忆键，前端持久化）
    :param file: 上传文件，可为空
    """
    has_file = file is not None and bool(file.filename)
    if not has_file and not text.strip():
        raise HTTPException(status_code=400, detail="请上传文件或输入指令")

    parsed_text = ""
    if has_file:
        # 校验文件类型与大小（流式开始前完成，错误以 HTTP 状态码返回）
        suffix = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if suffix not in SUPPORTED_SUFFIX:
            raise HTTPException(status_code=400, detail=f"暂不支持该文件类型（{suffix or '未知'}），请上传 xlsx/docx/图片/csv")
        data = await file.read()
        if len(data) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件超过 20MB 大小限制")
        try:
            parsed_text = parse_file(file.filename, data, file.content_type or "")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"[学管Agent] 文件解析失败: {e}")
            raise HTTPException(status_code=400, detail="文件解析失败，请检查文件内容")

    logger.info(f"[学管Agent] 收到请求，thread_id: {thread_id}，file: {file.filename if has_file else '无'}，指令: {text[:100]}")

    # 流式返回：文件解析已在生成器外完成，Agent 执行中的异常只能中断流
    return StreamingResponse(
        stream_student_agent(text.strip(), parsed_text, thread_id),
        media_type="text/event-stream",
        # 禁用各级缓冲，保证流式实时下发（X-Accel-Buffering 供 Nginx 反代场景）
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
