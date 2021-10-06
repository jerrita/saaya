from saaya.utils import PluginManager
from saaya.event import GroupMessage
from saaya.session import Bot
from saaya.message import *
from saaya import config
from functools import wraps
import time
from private import wsm

funcList = []
ft = ['os', 'system', 'so', 'import', 'open', 'while', '::-1', '__', 'lambda', 'builtin', 'exec', 'eval']
# 真正的 flag 在哪呢？
flag = 'flag{fake_flag}'


def FuncWrapper(func):
    limits = {}
    warn_limit = {}

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        key = func.__name__
        if key not in limits:
            limits[key] = 3
            warn_limit[key] = time.time()

        # 并非恶意调用，回满
        if time.time() - warn_limit[key] > 10:
            warn_limit[key] = time.time()
            limits[key] = 3

        if limits[key] > 0:
            limits[key] -= 1
            warn_limit[key] = time.time()
            func(*args, **kwargs)
        else:
            logger.warn('监测到恶意调用函数，终止.')

    return wrapped_func


# @PluginManager.registerEvent('OnLoad')
# def bd(bot: Bot):
#     config.feature['RepeatEnable'] = False
#     bot.sendGroupMessage(wsm[0], 'CloudFunc reloaded')


@PluginManager.registerEvent('GroupMessage')
async def func_plug(event: GroupMessage):
    if event.group.uid in wsm:
        if 'clear' in event.message.getContent():
            funcList.clear()
            event.group.sendMessage('Cleared')

        if 'cf_status' == event.message.getContent():
            event.group.sendMessage('Running.')

        try:
            for func in funcList:
                logger.debug(f'CloudFunc {func} computing...')
                exec(func)
        except Exception as e:
            logger.error(e)

    if event.group.uid in wsm:
        msg = event.message.getContent()

        if msg.startswith('PlugFunc:'):
            try:
                data = msg.split('\n')
                func = '\n'.join(data[1:])
                if data[0].split(':')[1] == 'GroupMessage':
                    fla = False
                    for f in ft:
                        if f in func:
                            fla = True
                            event.group.sendMessage('WAF！爬')
                    if not fla:
                        func = func.replace('def', '@FuncWrapper\ndef')
                        funcList.append(compile(func, '', 'exec'))
                        event.group.sendMessage('Plugin plugged.')
                else:
                    event.group.sendMessage('Unknown type.')
            except Exception as e:
                event.group.sendMessage(str(e))
