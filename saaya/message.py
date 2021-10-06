from __future__ import annotations

from .logger import logger

from typing import List, Type, Union, TYPE_CHECKING


class ChainObj:
    type: str

    def __init__(self, t: str):
        """
        消息链成员基类

        :param t: 消息类型
        """
        self.type = t

    def serialize(self):
        """
        返回序列化字典

        :return:
        """
        return vars(self)

    def getContent(self, console: bool = False) -> str:
        """
        返回可显示的值，比如： [图片]

        :param console: 是否在控制台简化
        :return:
        """
        pass


class Source(ChainObj):
    def __init__(self, source: dict = None, msgId: int = None, time: int = None):
        self.messageId = source['id'] if not msgId else msgId
        self.timeStamp = source['time'] if not time else time
        super().__init__('Source')

    def getContent(self, console: bool = False) -> str:
        return f'[Source & id: {self.messageId}, time: {self.timeStamp}]'


class Plain(ChainObj):
    def __init__(self, source: Union[dict, str]):
        if type(source) is str:
            self.text = source
        else:
            self.text = source['text']
        super().__init__('Plain')

    def getContent(self, console: bool = False) -> str:
        return self.text


class At(ChainObj):
    def __init__(self, source: dict = None, target: int = None, display: str = None):
        self.target: int = source['target'] if not target else target
        self.display: str = source['display'] if not display else display
        super().__init__('At')

    def getContent(self, console: bool = False) -> str:
        if self.display:
            return f'[At: {self.display}({self.target})]'
        else:
            return f'[At: {self.target}]'


class Quote(ChainObj):
    """
    引用消息类型，默认在非控制台下返回空值\n
    可通过是否存在 `Message.quote` 判断该消息是否为其他消息的引用
    """

    def __init__(self, source: dict = None, msgId: int = None, senderId: int = None, origin: Message = None):
        self.sourceId: int = source['id'] if not msgId else msgId
        self.senderId: int = source['senderId'] if not senderId else senderId
        self.origin: Message = Message(serialize=source['origin']) if not origin else origin
        super().__init__('Quote')

    def getContent(self, console: bool = False) -> str:
        if console:
            return f'[Quote & {self.senderId}: {self.origin.getContent(console=True)}]'
        else:
            return ''


class Image(ChainObj):
    def __init__(self, source: dict, ignoreId: bool = False, url: str = None):
        if not ignoreId:
            self.imageId = source['imageId']
        self.url = source['url'] if not url else url
        super().__init__('Image')

    def getContent(self, console: bool = False) -> str:
        if console:
            return f'[Image: {self.url if not "imageId" in vars(self) else self.imageId}]'
        else:
            return '[图片]'


class Message:
    source: Source
    chain: List[ChainObj]
    quote: Union[Quote, None]  # 这条消息是否为某一条消息的回复

    def __init__(self, serialize: list, fromSource: bool = False, rebuild_image: bool = False):
        """
        使用序列化列表构建消息链

        :param serialize: 序列化字符串
        :param fromSource: 是否从消息源构建（发送消息时应为 false）
        :param rebuild_image: 是否重建图片（忽略图片 id）
        """
        self.chain = []
        if fromSource:
            if len(serialize) < 2 or serialize[0]['type'] != 'Source':
                logger.warn('MessageChain serialize is illegal!')
            else:
                self.source = Source(serialize[0])
                serialize.__delitem__(0)

        has_quote = False
        for obj in serialize:
            if obj['type'] == 'Plain':
                self.chain.append(Plain(obj))
            if obj['type'] == 'Image':
                self.chain.append(Image(obj, ignoreId=True if rebuild_image else False))
            if obj['type'] == 'At':
                self.chain.append(At(obj))
            if obj['type'] == 'Quote':
                self.chain.insert(1, Quote(obj))
                self.quote = Quote(obj)
                has_quote = True
        if not has_quote:
            self.quote = None

    def build(self, mixed_chain: Union[list, Message, str]):
        """
        用混合消息链构造消息链

        :param mixed_chain:
        :return:
        """
        self.chain = []
        if type(mixed_chain) is not list:
            mixed_chain = [mixed_chain]

        for msg in mixed_chain:
            if issubclass(type(msg), ChainObj):
                self.chain.append(msg)
            if type(msg) is str:
                self.chain.append(Plain(msg))
            if type(msg) is Message:
                self.chain += msg.chain

    def getContent(self, console=False) -> str:
        """
        返回尽量可读的内容，比如：[图片]

        :param console: 是否在控制台上简化
        :return:
        """
        res = ''
        for element in self.chain:
            res += element.getContent(console)

        return res

    def getChain(self) -> List[dict]:
        """
        返回朴素的消息链

        :return:
        """
        res = []
        for element in self.chain:
            res.append(element.serialize())
        return res
