from saaya.utils import PluginManager
from saaya.event import GroupMessage
from private import test_groups


@PluginManager.registerEvent('GroupMessage')
def hello(event: GroupMessage):
    if event.group.uid in test_groups:
        if event.message.getContent() == 'hello':
            event.group.sendMessage('world!')
