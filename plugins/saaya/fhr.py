from saaya.utils import PluginManager
from saaya.event import MemberCardChangeEvent
from saaya.session import Bot
from private import wsm, fhr

prevent = False
name = '打死wsm'


@PluginManager.registerEvent('OnLoad')
def hello(bot: Bot):
    bot.sendGroupMessage(wsm[0], 'Fhr plugin loaded')
    bot.changeMemberInfo(wsm[0], fhr, name=name)


@PluginManager.registerEvent('MemberCardChangeEvent')
def info(event: MemberCardChangeEvent):
    if event.group.uid in wsm and event.member.uid == fhr and event.new != name:
        event.group.sendMessage(f'探测到 fhr 试图更改昵称，已拦截')
        event.bot.changeMemberInfo(event.group, event.member.uid, name=name)
