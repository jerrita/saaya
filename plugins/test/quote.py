from saaya.utils import PluginManager
from saaya.event import GroupMessage, GroupRecallEvent
from saaya.message import At
from private import wsm, cdd


@PluginManager.registerEvent('GroupMessage')
async def reply(event: GroupMessage):
    if event.group.uid in wsm:
        if event.message.quote:
            if 'recall' in event.message.getContent():
                event.bot.recall(messageId=event.message.quote.sourceId)
