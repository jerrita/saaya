from __future__ import annotations

from .event import Listener
from .protocol import Protocol
from .utils import PluginManager
from .logger import logger

from .member import Group, Friend
from .message import Message, Source
from .permission import Permission
from saaya import config

import asyncio

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    pass


class Bot:
    def __init__(self, addr: str, verifyKey: str):
        self.qq = 0
        self.protocol = Protocol(addr, verifyKey)
        self.verifyKey = verifyKey
        logger.info('Bot initialized.')

    def bind(self, qq):
        self.qq = qq
        self.protocol.bind(qq)
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

    def mute(self, group: Group, target: int, durTime: int):
        """
        禁言群成员

        :param group: 群
        :param target: 成员
        :param durTime: 禁言时间，单位为秒
        :return:
        """
        self.protocol.mute(group, target, durTime)

    def recall(self, messageId: Union[int, Source]):
        """
        撤回消息

        :param messageId: 待撤回消息的 MessageId
        :return:
        """
        tmp_id = messageId if type(messageId) is int else messageId.messageId
        self.protocol.recall_message(tmp_id)

    def getMessage(self, message: Union[int, Source], rebuild_image: bool = False) -> Union[Message, None]:
        """
        尝试通过缓存获取消息内容

        :param rebuild_image: 是否重建图片（忽略图片 id）
        :param message: 待恢复的 Source 或 MessageId
        :return:
        """
        tmp_source = Source(msgId=message) if type(message) is int else message
        return self.protocol.get_message_from_source(tmp_source, rebuild_image=rebuild_image)

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
