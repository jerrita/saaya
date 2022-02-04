from .logger import logger
import logging

# 日志级别，logger 和 handler以最高级别为准，不同handler之间可以不一样，不相互影响
logger.setLevel(logging.INFO)

version = '2.0.2 dev'
logger.info(f'Welcome to use saaya({version}) based on mirai!')

flag = 'flag{wElc0me_u5e_Sa@ya}'
