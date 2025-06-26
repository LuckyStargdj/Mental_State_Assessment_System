import logging
import os
import sys

# 获取用户目录路径
# user_home = os.path.expanduser('~')
# log_file_path = os.path.join(user_home, 'error_log.log')

# 配置日志记录
logging.basicConfig(
    filename='error_log.log',  # 日志文件名
    filemode='a',  # 追加模式，'w' 为覆盖模式
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    level=logging.ERROR  # 只记录错误级别的日志
)

logger = logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    try:
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    except Exception as e:
        pass


