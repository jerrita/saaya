from __future__ import annotations

import asyncio

from .logger import logger
from .permission import Permission
from typing import List, Dict, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from saaya.session import Bot
    from saaya.event import Event, GroupMessage, FriendMessage


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

    async def broadCast(self, event: Event):
        event_name = event.type
        if event_name in self.plugins:
            logger.debug(f'BroadCast {event} to {self.plugins[event_name]}')
            task_list = []
            for plugin in self.plugins[event_name]:
                task_list.append(asyncio.create_task(plugin(event)))
            try:
                await asyncio.wait(task_list)
            except Exception as e:
                if type(e) is not ValueError:  # 忽略空插件
                    logger.error(f'{type(e)}: {e}')

    def registerEvent(self, eventName: str):
        """
        参见 saaya.event \n
        注册事件，除生命周期事件以外，传入参数均为 Event。\n
        生命周期事件类型：OnLoad
        生命周期事件所给参数为: Bot

        :param eventName: 事件名称
        :return:
        """

        def plugin(func):
            logger.debug(f'Registering {func} on {eventName}')
            self.plugins[eventName].append(func)

        return plugin


class CmdProvider:
    """
    CMD 管理器，独立于 PluginManager，用于回应命令
    """
    starter: str  # Start alphabet
    funcs: Dict[str, Dict] = {}  # name: {alias: [], params: [], help: '', func: function, permission: Permission}
    enable: bool = True
    cmd_mapper: Dict[str, str]  # map of command

    def __init__(self, starter='/'):
        self.starter = starter
        self.funcs['help'] = {
            'alias': ['帮助'],
            'params': [],
            'help': '获得命令列表',
            'func': None,
            'permission': Permission.ALL,
        }
        self.gen_map()

    def handle_msg(self, event: Union[GroupMessage, FriendMessage]):
        msg = event.message.getContent()
        if len(msg) and msg[0] == self.starter:
            cmd = msg[1:].strip().split(' ')
            if len(cmd):
                logger.debug(f'Searching command: {cmd[0]}')
                if cmd[0] in self.cmd_mapper:
                    caller = self.cmd_mapper[cmd[0]]
                    logger.info(f'Calling command handler: {caller}')
                    try:
                        if caller == 'help':
                            self.gen_help(event)
                        else:
                            self.funcs[caller]['func'](event, cmd)
                    except Exception as e:
                        logger.error(f'Error exec command: {e}')

    def gen_help(self, event: Union[GroupMessage, FriendMessage]):
        res = ['-------CmdManager------']
        for func in self.funcs:
            res.append(f'{func}: {self.funcs[func]["help"]}')
        event.sender.sendMessage('\n'.join(res))

    def gen_map(self):
        self.cmd_mapper = {}
        for func in self.funcs:
            self.cmd_mapper[func] = func
            for alias in self.funcs[func]['alias']:
                self.cmd_mapper[alias] = func

    def registerCommand(self, cmd: str, alias: List[str] = [], help: str = '',
                        permission: List[str] = None):
        """
        注册命令

        :param permission:
        :param help: 命令帮助
        :param cmd: 命令名称
        :param alias: 命令别名
        :return:
        """

        if permission is None:
            permission = [Permission.ALL]

        def parser(func):
            logger.info(f'Registering command {cmd}')
            if func in self.funcs:
                logger.warn(f'Command {func} exists! It will be overwrite!')
            self.funcs[cmd] = {
                'alias': alias,
                'params': [],
                'func': func,
                'help': help,
                'permission': permission,
            }
            self.gen_map()

        return parser


PluginManager = BaseManager()
CmdManager = CmdProvider(starter='%')
