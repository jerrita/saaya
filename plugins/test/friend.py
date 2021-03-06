from saaya.utils import PluginManager
from saaya.event import FriendMessage


@PluginManager.registerEvent('FriendMessage')
def friend(event: FriendMessage):
    if event.message.getContent() == 'ping':
        event.sender.sendMessage('pong')
