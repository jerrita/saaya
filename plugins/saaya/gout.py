from saaya.utils import CmdManager
from saaya.event import GroupMessage, FriendMessage
from private import we
from utils import cqupt_gout, cqupt_cheat
from typing import Union


@CmdManager.registerCommand('gout', alias=['离校', '出校'], help='一键快速离校')
def gout(event: Union[GroupMessage, FriendMessage], param):
    if event.sender.uid in we:
        event.sender.sendMessage(cqupt_gout(we[event.sender.uid]))
    else:
        event.sender.sendMessage('不存在此用户的预制模板，请联系管理员添加！')


@CmdManager.registerCommand('cheat', alias=['秘技'], help='自动离返校')
def cheat(event: Union[GroupMessage, FriendMessage], param):
    if event.sender.uid in we:
        if len(param) != 2 or param[1] not in ['离', '返']:
            event.sender.sendMessage('Usage: cheat [离/返]')
        else:
            event.sender.sendMessage(cqupt_cheat(we[event.sender.uid], param[1]))
    else:
        event.sender.sendMessage('不存在此用户的预制模板，请联系管理员添加！')


@CmdManager.registerCommand('test', alias=['测试'], help='参数测试')
def cheat(event: Union[GroupMessage, FriendMessage], param):
    event.sender.sendMessage('\n'.join(param))
