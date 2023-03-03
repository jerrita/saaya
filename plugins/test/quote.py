from saaya.utils import PluginManager
from saaya.event import GroupMessage


@PluginManager.registerEvent('GroupMessage')
async def reply(event: GroupMessage):
    if event.message.quote:
        if 'recall' in event.message.getContent():
            event.bot.recall(messageId=event.message.quote.sourceId)
