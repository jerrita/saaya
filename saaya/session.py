from __future__ import annotations

from saaya.event import Listener
from saaya.protocol import Protocol
from saaya.utils import PluginManager
from saaya.logger import logger

from saaya.member import Group, Friend
from saaya.message import Message
from saaya.permission import Permission
from saaya import config

import asyncio

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    pass


class Bot:
    def __init__(self, addr: str, authKey: str):
        self.qq = 0
        self.protocol = Protocol(addr, authKey)
        logger.info('Bot initialized.')

    def bind(self, qq):
        self.qq = qq
        self.protocol.verify(qq)
        PluginManager.bind(self)

    def sendFriendMessage(self, friend: Union[int, Friend], msg: Union[list, Message, str]):
        """
        发送好友消息

        :param friend: 好友
        :param msg: 消息
        :return:
        """
        if type(friend) is int:
            friend = Friend(self, friend, 'Friend', 'Nickname')

        if type(msg) is not Message:
            t = Message([])
            t.build(msg)
            msg = t

        self.protocol.send_friend_message(friend, msg)

    def sendGroupMessage(self, group: Union[int, Group], msg: Union[list, Message, str]):
        """
        发送群消息

        :param group: 群
        :param msg: 消息
        :return:
        """
        if type(msg) not in [list, Message, str]:
            logger.warn('非法消息！')
            return

        if type(group) is int:
            group = Group(self, group, 'Group', Permission.MEMBER)

        if type(msg) is not Message:
            t = Message([])
            t.build(msg)
            msg = t

        if not config.feature['RepeatEnable'] and msg.getContent() == config.store['LastMessage']:
            logger.warn('Disabled msg send because Repeat is Disabled.')
            return

        config.store['LastMessage'] = msg.getContent()
        self.protocol.send_group_message(group, msg)

    def unmute(self, group: Group, target: int):
        """
        解除群成员禁言

        :param group: 群
        :param target: 成员
        :return:
        """
        self.protocol.unmute(group, target)

    def changeMemberInfo(self, group: Union[Group, int], target: int, name=None, specialTitle=None):
        """
        更改群员信息

        :param group: 群
        :param target: 成员
        :param name: 需要更改的群名片（可选）
        :param specialTitle: 给予的头衔（可选）
        :return:
        """
        if type(group) is int:
            group = Group(self, group, 'Group', Permission.MEMBER)
        self.protocol.change_member_info(group, target, name, specialTitle)

    def registerPlugins(self, plugins: list):
        for plugin in plugins:
            logger.info(f'Loading plugin: {plugin}')
            try:
                __import__(plugin)
            except Exception as e:
                logger.error(e)

        # 处理 OnLoad
        for func in PluginManager.plugins['OnLoad']:
            try:
                logger.info(f'Calling OnLoad func from {func}')
                func(self)
            except Exception as e:
                logger.error(e)

    def loop(self):
        listener = Listener(self)
        asyncio.get_event_loop().run_until_complete(listener.loop())
