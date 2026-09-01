# AI 学管路由：接收教师上传的文件 + 文字指令，调用 Agent 完成学生/成绩管理
# @author 6588 万立鹏 @date 2026-09-01
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from chief.logger import logger
from students.agent import run_student_agent
from students.parser import SUPPORTED_SUFFIX, parse_file

router = APIRouter()

# 上传文件大小限制：20MB
MAX_FILE_SIZE = 20 * 1024 * 1024


@router.post("/agent")
async def student_agent(
    text: str = Form(default=""),
    file: UploadFile | None = File(default=None),
):
    """
    学管 Agent 入口：文件（word/excel/图片）与文字指令至少提供其一，
    Agent 自动解析内容并调用 Spring Boot 接口完成增删改查，返回处理汇报
    """
    has_file = file is not None and file.filename
    if not has_file and not text.strip():
        raise HTTPException(status_code=400, detail="请上传文件或输入指令")

    parsed_text = ""
    if has_file:
        # 校验文件类型与大小
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

    logger.info(f"[学管Agent] 收到请求，file: {file.filename if has_file else '无'}, 指令: {text[:100]}")
    try:
        reply = run_student_agent(text.strip(), parsed_text)
    except Exception as e:
        logger.error(f"[学管Agent] 处理失败: {e}")
        raise HTTPException(status_code=500, detail="Agent 处理失败，请稍后重试")

    return {"reply": reply, "parsed": bool(parsed_text)}
