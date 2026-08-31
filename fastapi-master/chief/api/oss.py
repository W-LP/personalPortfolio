# OSS 预签名接口：前端直传阿里云 OSS
# 迁移自 hello 项目 app/api/v1/oss.py，并修复以下问题：
# 1. accessUrl 原来误将反引号包进 URL 导致 404，已去除
# 2. 函数名 chat_endpoint 与功能不符，改为 presign_upload
# 3. OSS_ENDPOINT 从环境变量读取并补默认值
# @author 万立鹏 @date 2026-08-31
import os
from datetime import timedelta
from pathlib import Path

import alibabacloud_oss_v2 as oss
from dotenv import load_dotenv
from fastapi import APIRouter

# 加载环境变量（.env 与 agent 模块同目录）
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

router = APIRouter()

# 从环境变量中加载凭证信息，用于身份验证
credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()

# 加载 SDK 的默认配置，并设置凭证提供者
cfg = oss.config.load_default()
cfg.credentials_provider = credentials_provider

# 必须指定 Region ID，SDK 会根据 Region 自动构造 HTTPS 访问域名
cfg.region = os.getenv("OSS_REGION", "cn-beijing")

# 使用配置好的信息创建 OSS 客户端
client = oss.Client(cfg)

# OSS 域名与桶配置
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
OSS_BUCKET = os.getenv("OSS_BUCKET")


@router.get("/oss/presign")
def presign_upload(filename: str):
    """
    申请直传预签名 URL
    :param filename: 文件名（含扩展名）
    :return: uploadUrl 直传地址、contentType、accessUrl 可访问地址
    """
    # 根据文件扩展名判断 Content-Type
    content_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    ext = filename.split(".")[-1].lower() if "." in filename else "jpg"
    content_type = content_type_map.get(ext, "application/octet-stream")

    # 生成 1 小时有效的 PUT 预签名
    pre_result = client.presign(oss.PutObjectRequest(
        bucket=OSS_BUCKET,
        key=filename,
        content_type=content_type,
    ), expires=timedelta(seconds=3600))

    # 返回上传 URL 和可访问的图片路径（不带反引号）
    return {
        "uploadUrl": pre_result.url.strip('"'),
        "contentType": content_type,
        "accessUrl": f"https://{OSS_BUCKET}.{OSS_ENDPOINT}/{filename}"
    }
