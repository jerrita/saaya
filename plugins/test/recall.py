from saaya.utils import PluginManager
from saaya.event import GroupRecallEvent


@PluginManager.registerEvent('GroupRecallEvent')
def recall(event: GroupRecallEvent):
    pass
