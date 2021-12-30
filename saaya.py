from saaya.session import Bot
from saaya.logger import logger
from private import address, verifyKey, botqq
import logging

logger.setLevel(logging.INFO)

if __name__ == '__main__':
    bot = Bot(address, verifyKey)  # 创建一个 Bot 实例
    bot.bind(botqq)  # 登陆 Bot （注意：需要主程序已登陆对应 qq）

    bot.registerPlugins([
        'plugins.turing.main',
        'plugins.saaya.misc',
        # 'plugins.saaya.fhr'
        'plugins.saaya.cloudfunc',
        'plugins.saaya.gout',
        'plugins.saaya.notice'
        # 'plugins.test.quote'
    ])  # 插件注册，规范如上

    bot.loop()  # 开始监听事件循环
