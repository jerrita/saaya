from saaya.utils import PluginManager
from saaya.event import GroupMessage, GroupRecallEvent
from saaya.message import At, Message
from private import wsm, cdd, bot_admin

msg_stack = {}


@PluginManager.registerEvent('GroupRecallEvent')
async def recall_handler(event: GroupRecallEvent):
    if event.group.uid not in msg_stack:
        msg_stack[event.group.uid] = []

    msg = event.bot.getMessage(event.source)
    if type(msg) is Message:
        msg_stack[event.group.uid].append(msg)


@PluginManager.registerEvent('GroupMessage')
async def reply(event: GroupMessage):
    if event.group.uid in wsm:
        if event.message.getContent() == 'saaya':
            event.group.sendMessage('kirakirakira')
        if event.sender.uid == cdd:
            event.group.sendMessage(event.message)

        if event.message.quote:
            if 'recall' in event.message.getContent():
                event.bot.recall(messageId=event.message.quote.sourceId)

        if '说话' in event.message.getContent():
            flag = False
            for msg in event.message.chain:
                if type(msg) is At:
                    msg: At
                    event.bot.unmute(event.group, msg.target)
                    flag = msg.target

            if flag:
                event.group.sendMessage(f'已清除 [{flag}] 的负面状态')

        cmd = event.message.getContent().split(' ')
        if cmd[0] == 'back':
            if event.sender.uid not in bot_admin:
                event.group.sendMessage('Permission denied!')
            else:
                if event.group.uid in msg_stack and len(msg_stack[event.group.uid]):
                    pl = 1 if len(cmd) < 2 or not cmd[1].isdigit() else int(cmd[1])
                    t_msg: Message = msg_stack[event.group.uid][-1 * max(min(len(msg_stack[event.group.uid]), pl), 0)]
                    event.group.sendMessage(t_msg)
                else:
                    event.group.sendMessage('Permission denied!')
