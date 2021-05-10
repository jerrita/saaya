from __future__ import annotations

from saaya.logger import logger
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from saaya.session import Bot
    from saaya.event import Event


class BaseManager:
    plugins: Dict[str, List]
    bot: Bot

    def __init__(self):
        # 手动写入是为了防止注册某些未实现的事件
        self.plugins = {
            'OnLoad': [],  # 插件注册时运行
            'GroupMessage': [],
            'GroupRecallEvent': [],
            'FriendMessage': [],
            'MemberCardChangeEvent': []
        }

    def bind(self, bot: Bot):
        self.bot = bot

    def broadCast(self, event: Event):
        event_name = event.type
        if event_name in self.plugins:
            logger.debug(f'BroadCast {event} to {self.plugins[event_name]}')
            for plugin in self.plugins[event_name]:
                try:
                    plugin(event)
                except Exception as e:
                    logger.error(e)

    def registerEvent(self, eventName: str):
        def plugin(func):
            logger.debug(f'Registering {func} on {eventName}')
            self.plugins[eventName].append(func)

        return plugin


PluginManager = BaseManager()
