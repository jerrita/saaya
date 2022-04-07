from saaya.event import GroupMessage
from saaya.utils import CmdManager

from private import fhr


@CmdManager.registerCommand('info', help='fhr 群名片测试')
def get_info(event: GroupMessage, param):
    f = event.bot.getMemberInfo(event.group, fhr)
    event.sender.sendMessage(f'Fhr 当前信息为：{vars(f)}')
