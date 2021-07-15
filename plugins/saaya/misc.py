from saaya.utils import PluginManager
from saaya.event import GroupMessage
from saaya.message import At
from private import wsm, cdd


@PluginManager.registerEvent('GroupMessage')
async def reply(event: GroupMessage):
    if event.group.uid in wsm:
        if event.message.getContent() == 'saaya':
            event.group.sendMessage('kirakirakira')
        if event.sender.uid == cdd:
            event.group.sendMessage(event.message)

        if '说话' in event.message.getContent():
            flag = False
            for msg in event.message.chain:
                if type(msg) is At:
                    msg: At
                    event.bot.unmute(event.group, msg.target)
                    flag = msg.target

            if flag:
                event.group.sendMessage(f'已清除 [{flag}] 的负面状态')
