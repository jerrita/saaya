from .logger import logger
import logging

# 日志级别，logger 和 handler以最高级别为准，不同 handler 之间可以不一样，不相互影响
logger.setLevel(logging.INFO)

version = '2.1.0 dev'
logger.info(f'Welcome to use saaya({version}) based on mirai!')
