from __future__ import annotations

from .logger import logger
from .member import *
from .message import Message, Source
from .utils import PluginManager, CmdManager
import websockets
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saaya.session import Bot


class Event:
    def __init__(self, bot: Bot, eventType='Event'):
        """
        基类事件

        :param bot: Bot
        :param eventType: 事件类型，是个字符串
        """
        self.bot = bot
        self.qq = bot.qq
        self.type: str = eventType
        self.illustrate()

    def illustrate(self):
        """
        事件初始化结束后会调用此函数在控制台输出信息

        :return:
        """
        pass


class FriendMessage(Event):
    sender: Friend
    message: Message

    def __init__(self, event: Event, sender: Friend, message: Message):
        """
        好友消息事件

        :param event: 基类事件
        :param sender: Member.Friend
        """
        self.sender = sender
        self.message = message
        super().__init__(event.bot, event.type)

    def illustrate(self):
        logger.info(
            f'{self.sender.nickname}({self.sender.uid}): '
            f'{self.message.getContent(console=True)}')


class GroupMessage(Event):
    sender: GroupMember
    group: Group
    message: Message

    def __init__(self, event: Event, sender: GroupMember, group: Group, message: Message):
        """
        群消息事件

        :param event: 基类事件
        :param sender: Member.GroupMember
        :param group: Member.Group
        """
        self.sender = sender
        self.group = group
        self.message = message
        super().__init__(event.bot, event.type)

    def illustrate(self):
        logger.info(
            f'{self.group.name}({self.group.uid}) -> '
            f'{self.sender.name}({self.sender.uid}): {self.message.getContent(console=True)}')


class GroupRecallEvent(Event):
    def __init__(self, event: Event, operator: GroupMember, group: Group, source: Source):
        """
        群消息撤回事件

        :param event: 基类事件
        :param operator: Member.GroupMember
        :param group: Member.Group
        :param source: 撤回的消息源
        """
        self.operator = operator
        self.group = group
        self.source = source
        super().__init__(event.bot, event.type)

    def illustrate(self):
        logger.info(f'{self.group.name}({self.group.uid}): '
                    f'{self.operator.name}({self.operator.uid}) <- 撤回了'
                    f'{self.source.getContent()}')


class MemberCardChangeEvent(Event):
    def __init__(self, event: Event, origin: str, current: str,
                 member: GroupMember, group: Group):
        self.origin = origin
        self.current = current
        self.member = member
        self.group = group
        super().__init__(event.bot, event.type)

    def illustrate(self):
        logger.info(f'{self.group.name}({self.group.uid}) -> '
                    f'{self.member.uid} 的名称从 {self.origin} 变更为 {self.current}')


class Listener:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def processor(self, msg):
        event = Event(self.bot)
        logger.debug(msg)

        data: dict = json.loads(msg)['data']
        if 'type' not in data:
            return
        event.type = data['type']

        if event.type.endswith('Event'):
            logger.info(f'Receive event: {event.type}')

        if event.type == 'FriendMessage':
            sender = Friend(self.bot,
                            uid=data['sender']['id'],
                            nickname=data['sender']['nickname'],
                            remark=data['sender']['remark'])

            message = Message(data['messageChain'], fromSource=True)
            event = FriendMessage(event, sender, message)

        if event.type == 'GroupMessage':
            group = Group(self.bot,
                          qq=data['sender']['group']['id'],
                          name=data['sender']['group']['name'],
                          permission=data['sender']['group']['permission'])

            sender = GroupMember(self.bot,
                                 qq=data['sender']['id'],
                                 name=data['sender']['memberName'],
                                 group=group,
                                 permission=data['sender']['permission'])

            message = Message(data['messageChain'], fromSource=True)
            event = GroupMessage(event, sender, group, message)

        if event.type == 'GroupRecallEvent':
            group = Group(self.bot,
                          qq=data['group']['id'],
                          name=data['group']['name'],
                          permission=data['group']['permission'])

            operator = GroupMember(self.bot,
                                   qq=data['operator']['id'],
                                   name=data['operator']['memberName'],
                                   group=group,
                                   permission=data['operator']['permission'])

            source = Source(msgId=data['messageId'], time=data['time'])

            event = GroupRecallEvent(event, operator, group, source)

        if event.type == 'MemberCardChangeEvent':
            group = Group(self.bot,
                          qq=data['member']['group']['id'],
                          name=data['member']['group']['name'],
                          permission=data['member']['group']['permission'])
            member = GroupMember(self.bot,
                                 qq=data['member']['id'],
                                 name=data['member']['memberName'],
                                 group=group,
                                 permission=data['member']['permission'])
            origin = data['origin']
            current = data['current']

            event = MemberCardChangeEvent(event, origin, current, member, group)

        if event.type in ['GroupMessage', 'FriendMessage'] and CmdManager.enable:
            CmdManager.handle_msg(event)

        await PluginManager.broadCast(event)

    async def loop(self):
        uri = f'ws://{self.bot.protocol.addr}/all?verifyKey={self.bot.verifyKey}&sessionKey={self.bot.protocol.session}'
        async with websockets.connect(uri) as ws:
            while True:
                msg = await ws.recv()
                await self.processor(msg)
