from saaya.utils import PluginManager
from saaya.event import MemberCardChangeEvent
from saaya.session import Bot
from private import wsm, fhr

prevent = False


@PluginManager.registerEvent('OnLoad')
def hello(bot: Bot):
    bot.sendGroupMessage(wsm[0], 'Fhr plugin loaded')
    bot.changeMemberInfo(wsm[0], fhr, name='打死wsm')


@PluginManager.registerEvent('MemberCardChangeEvent')
def info(event: MemberCardChangeEvent):
    global prevent
    if prevent:
        prevent = False
    elif event.group.uid in wsm:
        event.group.sendMessage(f'探测到 fhr 试图将昵称由 {event.origin} 更改为 {event.new}，正在尝试拦截')
        event.bot.changeMemberInfo(event.group, event.member.uid, name=event.origin)
        prevent = True
