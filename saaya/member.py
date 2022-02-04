from __future__ import annotations

from .permission import Permission
from .message import Message
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from saaya.session import Bot


class BaseMember:
    def __init__(self, bot: Bot, uid):
        """
        基础成员类

        :param bot: Bot
        :param uid: 可能为qq号、群号等
        """
        self.bot = bot
        self.uid = uid

    def sendMessage(self, messageChain: list):
        """
        对成员发送消息

        :param messageChain: 一个列表，函数将自动调用 Message.build 将其构造为消息链
        :return:
        """
        pass


class Friend(BaseMember):
    def __init__(self, bot: Bot, uid, nickname: str, remark: str):
        """
        好友

        :param bot: 机器人
        :param uid: qq号
        :param nickname: 昵称
        :param remark: 备注
        """
        self.nickname = nickname
        self.remark = remark
        super().__init__(bot, uid)

    def sendMessage(self, msg: Union[list, Message, str]):
        msg_chain = Message([])
        msg_chain.build(msg)
        self.bot.sendFriendMessage(self, msg_chain)


class GroupMember(BaseMember):
    def __init__(self, bot: Bot, qq: int, name: str, group: Group, permission: Permission):
        """
        群成员

        :param bot: Bot
        :param qq: qq号
        :param name: 群昵称 或 昵称
        :param permission: 群内权限
        """
        super().__init__(bot, qq)
        self.name = name
        self.group = group
        self.permission = permission

    def sendMessage(self, msg: Union[list, Message, str]):
        msg_chain = Message([])
        msg_chain.build(msg)
        self.bot.sendGroupMessage(self.group, msg_chain)


class Group(BaseMember):
    def __init__(self, bot: Bot, qq: int, name: str, permission: Permission):
        """
        表示一个群

        :param bot: Bot
        :param qq: 群号
        :param name: 群昵称
        :param permission: 机器人在所在群的权限
        """
        super().__init__(bot, qq)
        self.name = name
        self.permission = permission

    def mute(self, target: int, durTime: int):
        """
        禁言群成员

        :param target: 目标
        :param durTime: 时间，单位为秒
        :return:
        """
        self.bot.mute(self, target, durTime)

    def unmute(self, target: int):
        """
        解禁群成员

        :param target: 目标
        :return:
        """
        self.bot.unmute(self, target)

    def sendMessage(self, msg: Union[list, Message, str]):
        msg_chain = Message([])
        msg_chain.build(msg)
        self.bot.sendGroupMessage(self, msg_chain)
