# 私厨应用统一日志配置
# @author 万立鹏 @date 2026-08-31
import logging
import sys

# 日志格式：时间 - 级别 - 模块 - 消息
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


def setup_logging():
    """
    初始化全局日志配置
    输出到控制台，级别 INFO
    """
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


# 全局 logger 实例，供 agent 与接口层共用
logger = logging.getLogger("personal_chief")
