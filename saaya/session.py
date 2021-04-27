from __future__ import annotations

from saaya.event import Listener
from saaya.protocol import Protocol
from saaya.utils import PluginManager
from saaya.logger import logger

import asyncio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saaya.member import Group, Friend
    from saaya.message import Message


class Bot:
    def __init__(self, addr: str, authKey: str):
        self.qq = 0
        self.protocol = Protocol(addr, authKey)
        logger.info('Bot initialized.')

    def bind(self, qq):
        self.qq = qq
        self.protocol.verify(qq)
        PluginManager.bind(self)

    def sendFriendMessage(self, friend: Friend, msg: Message):
        """
        发送好友消息

        :param friend: 好友
        :param msg: 消息
        :return:
        """
        self.protocol.send_friend_message(friend, msg)

    def sendGroupMessage(self, group: Group, msg: Message):
        """
        发送群消息

        :param group: 群
        :param msg: 消息
        :return:
        """
        self.protocol.send_group_message(group, msg)

    def unmute(self, group: Group, target: int):
        """
        解除群成员禁言

        :param group: 群
        :param target: 成员
        :return:
        """
        self.protocol.unmute(group, target)

    @staticmethod
    def registerPlugins(plugins: list):
        for plugin in plugins:
            logger.info(f'Loading plugin: {plugin}')
            try:
                __import__(plugin)
            except Exception as e:
                logger.error(e)

    def loop(self):
        listener = Listener(self)
        asyncio.get_event_loop().run_until_complete(listener.loop())
