from saaya.utils import CmdManager
from saaya.event import GroupMessage


@CmdManager.registerCommand('mute', help='测试禁言')
async def mute(event: GroupMessage, parm):
    event.group.mute(2756456886, 60)


@CmdManager.registerCommand('unmute', help='测试解禁')
async def unmute(event: GroupMessage, parm):
    event.group.unmute(2756456886)
