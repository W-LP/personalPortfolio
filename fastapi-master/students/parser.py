# 文件解析器：将教师上传的 word/excel/图片 提取为表格文本（TSV 行），供 Agent 规整
# 说明：
# 1. xlsx/docx 由 office_parser.py 以标准库解析（zipfile+xml，零第三方依赖）
# 2. 图片使用 DeepSeek 多模态模型提取文字表格
# 3. 旧版 .xls 为二进制格式不支持，提示转存为 .xlsx
# @author 6588 万立鹏 @date 2026-09-01
import base64
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from chief.logger import logger
from students.office_parser import parse_docx_bytes, parse_xlsx_bytes

# 加载环境变量（.env 与 chief 同目录复用一套模型配置）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, "chief", ".env"))

# 支持的文件类型
SUPPORTED_SUFFIX = {".xlsx", ".docx", ".jpg", ".jpeg", ".png", ".webp", ".csv", ".txt"}

# 图片识别提示词
IMAGE_PROMPT = """请提取图片中的学生信息或成绩表格，以 TSV 文本输出（每行一条记录，列之间用制表符分隔）。
- 第一行为表头，字段可能包含：姓名、性别、年龄、身高、体重、性格、科目分数、考试名称等
- 只输出 TSV 文本，不要输出任何解释
- 无法识别的字段留空，不要编造"""


def _parse_image_bytes(data: bytes, mime: str) -> str:
    """
    解析图片：调用多模态模型提取表格文本
    :param data: 图片字节
    :param mime: 图片 MIME 类型
    :return: 模型提取的 TSV 文本
    """
    # 模型初始化放函数内：仅图片上传时才会构建，避免纯表格场景的启动开销
    vision_model = init_chat_model(
        model=os.getenv("CHIEF_MODEL", "deepseek-v4-flash-vision-exp"),
        model_provider="deepseek",
        base_url=os.getenv("DEEPSEEK_BASE_URL"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    b64 = base64.b64encode(data).decode("utf-8")
    message = HumanMessage(content=[
        {"type": "image", "url": f"data:{mime};base64,{b64}"},
        {"type": "text", "text": IMAGE_PROMPT},
    ])
    response = vision_model.invoke([message])
    return response.content if isinstance(response.content, str) else str(response.content)


def parse_file(filename: str, data: bytes, mime: str = "") -> str:
    """
    文件解析总入口，按后缀分发
    :param filename: 上传文件名
    :param data: 文件字节
    :param mime: MIME 类型
    :return: 表格文本（TSV 行），供 Agent 规整
    """
    suffix = os.path.splitext(filename)[1].lower()
    logger.info(f"[文件解析] {filename}, {len(data)} bytes, mime: {mime}")
    if suffix == ".xlsx":
        return parse_xlsx_bytes(data)
    if suffix == ".docx":
        return parse_docx_bytes(data)
    if suffix in (".csv", ".txt"):
        # 兼容 BOM，按行原样输出
        return data.decode("utf-8-sig", errors="replace")
    if suffix in (".jpg", ".jpeg", ".png", ".webp"):
        return _parse_image_bytes(data, mime or "image/jpeg")
    raise ValueError(f"暂不支持该文件类型（{suffix or '未知'}），请上传 xlsx/docx/图片/csv")
