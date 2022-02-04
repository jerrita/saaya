from __future__ import annotations

from .permission import Permission
from .logger import logger
from .message import Message
from typing import TYPE_CHECKING, Union

import json
import requests
import time

if TYPE_CHECKING:
    from saaya.message import Source
    from saaya.member import Group, Friend


class Protocol:
    retry = 5

    def __init__(self, addr: str, verifyKey: str, retry: int = 5):
        self.addr = addr
        self.baseUrl = addr if addr.startswith('http://') else 'http://' + addr
        self.mirai_version = self.json_query('/about', post=False)['data']['version']
        self.retry = retry
        logger.info(f'Connected to mirai-http backend. The version is {self.mirai_version}.')
        self.session = self.json_query('/verify', {'verifyKey': verifyKey})['session']
        # self.session = '8zHZb8kg'
        if self.session == 'SINGLE_SESSION':
            self.session = ''  # Single mode
        else:
            logger.info(f'Authed. Your session is {self.session}')

    def bind(self, qq):
        if self.session == '':
            logger.info('Running as Single Mode, skip bind.')
        else:
            res = self.json_query('/bind', {
                'sessionKey': self.session,
                'qq': qq
            })
            if res['code'] == 0:
                logger.info(f'Successfully bind on qq {qq}.')

    def send_friend_message(self, friend: Friend, msg: Message):
        res = self.json_query('/sendFriendMessage', {
            'sessionKey': self.session,
            'target': friend.uid,
            'messageChain': msg.getChain()
        })

        if res['code'] == 0:
            logger.info(f'{friend.remark}({friend.uid}) <- {msg.getContent(console=True)}')
        else:
            logger.error(f'Send message to {friend.remark}({friend.uid}) failed with code {res["code"]}')

    def send_group_message(self, group: Group, msg: Message):
        res = self.json_query('/sendGroupMessage', {
            'sessionKey': self.session,
            'target': group.uid,
            'messageChain': msg.getChain()
        })
        if res['code'] == 0:
            logger.info(f'{group.name}({group.uid}) <- {msg.getContent(console=True)}')
        else:
            logger.warn(f'Send message to {group.name}({group.uid}) failed with code {res["code"]}')

    def recall_message(self, target: int):
        """
        消息撤回

        :param target: MessageId
        :return:
        """
        res = self.json_query('/recall', {
            'sessionKey': self.session,
            'target': target
        })
        if res['code'] == 0:
            logger.info(f'Recalled message: {target}')
        else:
            logger.warn(f'Recall message {target} failed')

    def get_message_from_source(self, source: Source, rebuild_image: bool = False) -> Union[Message, None]:
        res = self.json_query(f'/messageFromId?sessionKey={self.session}&id={source.messageId}', post=False)
        if res['code']:
            logger.error(f'Get message from source error with code: {res["code"]}')
            return None
        else:
            msg = Message(serialize=res['data']['messageChain'], fromSource=True, rebuild_image=rebuild_image)
            logger.debug(f'Got chain: {msg.getContent(console=True)}')
            return msg

    def mute(self, target: Group, memberId: int, durTime: int):
        if target.permission != Permission.ADMINISTRATOR.name:
            logger.error(f'Mute error: Permission denied.')
            return -1

        res = self.json_query('/mute', {
            'sessionKey': self.session,
            'target': target.uid,
            'memberId': memberId,
            'time': durTime
        })

        if res['code'] == 0:
            logger.info(f'Muted {memberId} for {durTime}s from {target.name}({target.uid})')
        else:
            logger.warn(f'Mute error: {res["msg"]}')

    def unmute(self, target: Group, memberId: int):
        """
        解除群成员禁言

        :param target: 群号
        :param memberId: 成员qq
        :return:
        """
        if target.permission != Permission.ADMINISTRATOR.name:
            logger.error(f'Unmute error: Permission denied.')
            return -1

        res = self.json_query('/unmute', {
            'sessionKey': self.session,
            'target': target.uid,
            'memberId': memberId
        })

        if res['code'] == 0:
            logger.info(f'Unmuted {memberId} from {target.name}({target.uid})')
        else:
            logger.warn(f'Unmute error: {res["msg"]}')

    def change_member_info(self, group: Group, target: int, name=None, specialTitle=None):
        """
        更改群员信息

        :param group: 群
        :param target: 成员
        :param name: 需要更改的群名片（可选）
        :param specialTitle: 给予的头衔（可选）
        :return:
        """
        data = {
            'sessionKey': self.session,
            'target': group.uid,
            'memberId': target,
            'info': {}
        }
        if name:
            data['info']['name'] = name
        if specialTitle:
            data['info']['specialTitle'] = specialTitle
        res = self.json_query('/memberInfo', data)

        if res['code'] == 0:
            logger.info(f'Change {target} info from {group.name}({group.uid}) to ' + json.dumps(data['info']))
        else:
            logger.error(f'Member info change error: {res["msg"]}')

    def json_query(self, addr: str, data: dict = None, post: bool = True) -> dict:
        try:
            res = requests.post(self.baseUrl + addr, json=data) if post else requests.get(self.baseUrl + addr)
            res = json.loads(res.text)
            if res['code']:
                logger.error(f'{addr} got code: {res["code"]}')
            return res
        except Exception as e:
            logger.error(e)
            logger.info(f'Retry after {self.retry}s...')
            time.sleep(self.retry)
            return self.json_query(addr, data, post)
