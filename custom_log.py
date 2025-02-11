from loguru import logger
from download import get_local_dir, get_current_hour
import os

# 获取日志保存路径
save_path = get_local_dir('log')
log_file = os.path.join(save_path, get_current_hour() + ".log")  # 保存的文件名

# 配置日志记录器
logger.add(
    log_file,
    format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
    enqueue=True,       # 启用队列模式，避免多进程写入同一文件时的冲突
    encoding="utf-8",   # 日志文件支持 UTF-8 编码
    backtrace=False,
    diagnose=False,
    rotation="1 hour",      # 每小时创建一个新的日志文件
    retention="7 days",     # 保留最近 7 天的日志文件
)

def write_log(level, message):
    """
    写入日志。

    :param level: 日志等级（例如 'info', 'error' 等）
    :param message: 日志消息
    """
    if level.lower() == 'info':
        logger.info(message)
    elif level.lower() == 'error':
        logger.error(message)
    elif level.lower() == 'warning':
        logger.warning(message)
    elif level.lower() == 'debug':
        logger.debug(message)
    elif level.lower() == 'critical':
        logger.critical(message)
    else:
        logger.info(message)  # 默认记录为 info 级别