# 私厨 FastAPI 入口
# 启动方式（工作目录须为 fastapi-master）：
#   .venv\Scripts\python.exe -m uvicorn chief.main:app --host 127.0.0.1 --port 8002 --reload
# @author 万立鹏 @date 2026-08-31
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chief.api import chat, oss
from chief.agent import init_checkpointer
from chief.logger import setup_logging, logger

# 初始化日志配置
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化 SQLite 异步 checkpointer（建表/建连接）"""
    await init_checkpointer()
    logger.info("checkpointer 初始化完成")
    yield


app = FastAPI(
    title="Personal Chief API",
    description="私厨：拍照识别食材，AI 推荐食谱",
    version="0.1.0",
    lifespan=lifespan
)

# 1. 配置跨域资源共享 (CORS)
# 前端开发经 Vite 代理转发，生产由 Nginx 反向代理，CORS 仅作兜底
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 挂载路由（统一前缀 /api/chief，与前端 Vite 代理规则对应）
app.include_router(chat.router, prefix="/api/chief", tags=["对话"])
app.include_router(oss.router, prefix="/api/chief", tags=["OSS直传"])


@app.get("/api/chief/health")
async def health():
    """
    健康检查
    """
    return {"status": "UP", "service": "personal-chief"}


if __name__ == "__main__":
    import uvicorn

    # 启动命令：python -m chief.main
    logger.info("私厨服务启动：127.0.0.1:8002")
    uvicorn.run("chief.main:app", host="127.0.0.1", port=8002, reload=True)
