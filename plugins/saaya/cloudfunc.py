from saaya.utils import PluginManager
from saaya.event import GroupMessage
from saaya.session import Bot
from saaya.message import *
from saaya import config
from private import wsm

funcList = []
ft = ['os', 'system', 'so', 'import', '__import__', 'open', 'while', '::-1', '__classes__']
# 真正的 flag 在哪呢？
flag = 'flag{fake_flag}'


@PluginManager.registerEvent('OnLoad')
def bd(bot: Bot):
    config.feature['RepeatEnable'] = False
    # bot.sendGroupMessage(wsm[0], 'CloudFunc reloaded')


@PluginManager.registerEvent('GroupMessage')
def func_plug(event: GroupMessage):
    if event.group.uid in wsm:
        if 'clear' in event.message.getContent():
            funcList.clear()
            event.group.sendMessage('Cleared')

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
                        funcList.append(compile(func, '', 'exec'))
                        event.group.sendMessage('Plugin plugged.')
                else:
                    event.group.sendMessage('Unknown type.')
            except Exception as e:
                event.group.sendMessage(str(e))
