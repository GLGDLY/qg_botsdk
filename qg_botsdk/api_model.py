from io import BufferedReader
from os.path import exists
from typing import BinaryIO, Dict, List, Optional, Union

from ._api_model import BaseMessage
from ._api_model import MessageConstructRet as _MessageConstructRet
from ._utils import sdk_error_temp
from .http import FormData_


class ApiModel:
    class Message(BaseMessage):
        def __init__(
            self,
            content: Optional[str] = None,
            image: Optional[str] = None,
            file_image: Optional[Union[bytes, BinaryIO, str]] = None,
            message_reference_id: Optional[str] = None,
            ignore_message_reference_error: bool = False,
        ):
            """
            构建一个消息对象，用于发送消息

            :param content: 消息文本（选填，此项与image至少需要有一个字段，否则无法下发消息）
            :param image: 图片url，不可发送本地图片（选填，此项与msg至少需要有一个字段，否则无法下发消息）
            :param file_image: 本地图片，可选三种方式传参，具体可参阅github中的example_10或帮助文档，与image同时存在时优先使用此项
            :param message_reference_id: 引用消息的id（选填）
            :param ignore_message_reference_error: 是否忽略获取引用消息详情错误，默认否（选填）
            """
            super().__init__()
            if content is not None and not isinstance(content, str):
                content = str(content)
            self.__content = content
            self.__image = image
            self.__file_image = file_image
            self.__message_reference_id = message_reference_id
            if ignore_message_reference_error is None:
                ignore_message_reference_error = False
            self.__ignore_message_reference_error = ignore_message_reference_error

        def __repr__(self):
            return (
                f"<Message content={self.__content}, image={self.__image}, file_image={self.__file_image}, "
                f"message_reference_id={self.__message_reference_id}, "
                f"ignore_message_reference_error={self.__ignore_message_reference_error}>"
            )

        def construct(self, message_id, event_id) -> _MessageConstructRet:
            """
            internal construct method

            :return: kwargs for http api request
            """
            if self.__message_reference_id is not None:
                json_ = {
                    "content": self.__content,
                    "msg_id": message_id,
                    "event_id": event_id,
                    "image": self.__image,
                    "message_reference": {
                        "message_id": self.__message_reference_id,
                        "ignore_get_message_error": self.__ignore_message_reference_error,
                    },
                }
            else:
                json_ = {
                    "content": self.__content,
                    "msg_id": message_id,
                    "event_id": event_id,
                    "image": self.__image,
                }
            if self.__file_image is not None:
                if isinstance(self.__file_image, BufferedReader):
                    self.__file_image = self.__file_image.read()
                elif isinstance(self.__file_image, str):
                    if exists(self.__file_image):
                        with open(self.__file_image, "rb") as img:
                            self.__file_image = img.read()
                    else:
                        if self.__file_image.startswith("http"):
                            return _MessageConstructRet(
                                result=False,
                                error_ret=sdk_error_temp(
                                    "发送网络图片请使用image参数，而非file_image"
                                ),
                            )
                        return _MessageConstructRet(
                            result=False, error_ret=sdk_error_temp("目标图片路径不存在，无法发送")
                        )
                elif not isinstance(self.__file_image, bytes):
                    return _MessageConstructRet(
                        result=False,
                        error_ret=sdk_error_temp(
                            f"file_image不支持{type(self.__file_image)}的内容"
                        ),
                    )
                json_["file_image"] = self.__file_image
                data_ = FormData_()
                for keys, values in json_.items():
                    if values is not None and keys != "image":
                        data_.add_field(keys, values)
                return _MessageConstructRet(result=True, kwargs={"data": data_})
            else:
                return _MessageConstructRet(result=True, kwargs={"json": json_})

    class MessageEmbed(BaseMessage):
        def __init__(
            self,
            title: Optional[str] = None,
            content: Optional[List[str]] = None,
            image: Optional[str] = None,
            prompt: Optional[str] = None,
        ):
            """
            构建一个embed消息对象，用于发送消息

            :param title: 标题文本（选填）
            :param content: 内容文本列表，每一项之间将存在分行（选填）
            :param image: 略缩图url，不可发送本地图片（选填）
            :param prompt: 消息弹窗通知的文本内容（选填）
            """
            super().__init__()
            self.__title = title
            self.__content = content
            self.__image = image
            self.__prompt = prompt

        def __repr__(self):
            return (
                f"<MessageEmbed title={self.__title}, content={self.__content}, image={self.__image}, "
                f"prompt={self.__prompt}>"
            )

        def construct(self, message_id, event_id) -> _MessageConstructRet:
            """
            internal construct method

            :return: kwargs for http api request
            """
            json_ = {
                "embed": {
                    "title": self.__title,
                    "prompt": self.__prompt,
                    "thumbnail": {"url": self.__image},
                    "fields": [],
                },
                "msg_id": message_id,
                "event_id": event_id,
            }
            if self.__content is not None:
                for items in self.__content:
                    json_["embed"]["fields"].append({"name": str(items)})
            return _MessageConstructRet(result=True, kwargs={"json": json_})

    class MessageArk23(BaseMessage):
        def __init__(
            self,
            content: List[str],
            link: List[str],
            desc: Optional[str] = None,
            prompt: Optional[str] = None,
        ):
            """
            构建一个ark23消息对象，用于发送消息

            :param content: 内容文本列表，每一项之间将存在分行
            :param link: 链接url列表，长度应与内容列一致。将根据位置顺序填充文本超链接，如文本不希望填充链接可使用空文本或None填充位置
            :param desc: 描述文本内容（选填）
            :param prompt: 消息弹窗通知的文本内容（选填）
            """
            super().__init__()
            self.__content = content
            self.__link = link
            self.__desc = desc
            self.__prompt = prompt

        def __repr__(self):
            return (
                f"<MessageArk23 content={self.__content}, link={self.__link}, desc={self.__desc}, "
                f"prompt={self.__prompt}>"
            )

        def construct(self, message_id, event_id) -> _MessageConstructRet:
            """
            internal construct method

            :return: kwargs for http api request
            """
            if len(self.__content) != len(self.__link):
                return _MessageConstructRet(
                    result=False, error_ret=sdk_error_temp("注意内容列表长度应与链接列表长度一致")
                )
            json_ = {
                "ark": {
                    "template_id": 23,
                    "kv": [
                        {"key": "#DESC#", "value": self.__desc},
                        {"key": "#PROMPT#", "value": self.__prompt},
                        {"key": "#LIST#", "obj": []},
                    ],
                },
                "msg_id": message_id,
                "event_id": event_id,
            }
            for _link, _content in zip(self.__link, self.__content):
                if _content is not None and not isinstance(_content, str):
                    _content = str(_content)
                if _link is not None and not isinstance(_link, str):
                    _link = str(_link)
                json_["ark"]["kv"][2]["obj"].append(
                    {
                        "obj_kv": [
                            {"key": "desc", "value": _content},
                            {"key": "link", "value": _link},
                        ]
                    }
                )
            return _MessageConstructRet(result=True, kwargs={"json": json_})

    class MessageArk24(BaseMessage):
        def __init__(
            self,
            title: Optional[str] = None,
            content: Optional[str] = None,
            subtitile: Optional[str] = None,
            link: Optional[str] = None,
            image: Optional[str] = None,
            desc: Optional[str] = None,
            prompt: Optional[str] = None,
        ):
            """
            构建一个ark24消息对象，用于发送消息

            :param title: 标题文本（选填）
            :param content: 详情描述文本（选填）
            :param subtitile: 子标题文本（选填）
            :param link: 跳转的链接url（选填）
            :param image: 略缩图url，不可发送本地图片（选填）
            :param desc: 描述文本内容（选填）
            :param prompt: 消息弹窗通知的文本内容（选填）
            """
            super().__init__()
            self.__title = title
            self.__content = content
            self.__subtitile = subtitile
            self.__link = link
            self.__image = image
            self.__desc = desc
            self.__prompt = prompt

        def __repr__(self):
            return (
                f"<MessageArk24 title={self.__title}, content={self.__content}, subtitile={self.__subtitile}, "
                f"link={self.__link}, image={self.__image}, desc={self.__desc}, prompt={self.__prompt}>"
            )

        def construct(self, message_id, event_id) -> _MessageConstructRet:
            """
            internal construct method

            :return: kwargs for http api request
            """
            json_ = {
                "ark": {
                    "template_id": 24,
                    "kv": [
                        {"key": "#DESC#", "value": self.__desc},
                        {"key": "#PROMPT#", "value": self.__prompt},
                        {"key": "#TITLE#", "value": self.__title},
                        {"key": "#METADESC#", "value": self.__content},
                        {"key": "#IMG#", "value": self.__image},
                        {"key": "#LINK#", "value": self.__link},
                        {"key": "#SUBTITLE#", "value": self.__subtitile},
                    ],
                },
                "msg_id": message_id,
                "event_id": event_id,
            }
            return _MessageConstructRet(result=True, kwargs={"json": json_})

    class MessageArk37(BaseMessage):
        def __init__(
            self,
            title: Optional[str] = None,
            content: Optional[str] = None,
            link: Optional[str] = None,
            image: Optional[str] = None,
            prompt: Optional[str] = None,
        ):
            """
            构建一个ark37消息对象，用于发送消息

            :param title: 标题文本（选填）
            :param content: 内容文本（选填）
            :param link: 跳转的链接url（选填）
            :param image: 略缩图url，不可发送本地图片（选填）
            :param prompt: 消息弹窗通知的文本内容（选填）
            """
            super().__init__()
            self.__title = title
            self.__content = content
            self.__link = link
            self.__image = image
            self.__prompt = prompt

        def __repr__(self):
            return (
                f"<MessageArk37 title={self.__title}, content={self.__content}, link={self.__link}, "
                f"image={self.__image}, prompt={self.__prompt}>"
            )

        def construct(self, message_id, event_id) -> _MessageConstructRet:
            json_ = {
                "ark": {
                    "template_id": 37,
                    "kv": [
                        {"key": "#PROMPT#", "value": self.__prompt},
                        {"key": "#METATITLE#", "value": self.__title},
                        {"key": "#METASUBTITLE#", "value": self.__content},
                        {"key": "#METACOVER#", "value": self.__image},
                        {"key": "#METAURL#", "value": self.__link},
                    ],
                },
                "msg_id": message_id,
                "event_id": event_id,
            }
            return _MessageConstructRet(result=True, kwargs={"json": json_})

    class MessageMarkdown(BaseMessage):
        def __init__(
            self,
            template_id: Optional[str] = None,
            key_values: Optional[
                Union[
                    List[Dict[str, Union[str, List[str]]]],
                    Dict[str, Union[str, List[str]]],
                ]
            ] = None,
            content: Optional[str] = None,
            keyboard_id: Optional[str] = None,
            keyboard_content: Optional[Dict] = None,
        ):
            """
            构建一个markdown消息对象，用于发送消息

            :param template_id: markdown 模板 id（选填，与content不可同时存在）
            :param key_values: markdown 模版 key values列表，格式为：{key1: value1, key2: value2}（选填，与content不可同时存在）
            :param content: 原生 markdown 内容（选填，与template_id, key, values不可同时存在）
            :param keyboard_id: keyboard 模板 id（选填，与keyboard_content不可同时存在）
            :param keyboard_content: 原生 keyboard 内容（选填，与keyboard_id不可同时存在）
            """
            super().__init__()
            self.__template_id = template_id
            self.__key_values = key_values
            self.__content = content
            self.__keyboard_id = keyboard_id
            self.__keyboard_content = keyboard_content

        def __repr__(self):
            return (
                f"<MessageMarkdown template_id={self.__template_id}, key_values={self.__key_values}, "
                f"content={self.__content}, keyboard_id={self.__keyboard_id}, "
                f"keyboard_content={self.__keyboard_content}>"
            )

        def construct(self, message_id, event_id) -> _MessageConstructRet:
            """
            internal construct method

            :return: kwargs for http api request
            """
            logger_msg = None
            if self.__keyboard_content:
                if self.__keyboard_id:
                    logger_msg = "注意keyboard_id与keyboard_content不可同时存在，注意系统已根据优先级仅保留keyboard_content"
                keyboard = {"content": self.__keyboard_content}
            elif self.__keyboard_id:
                keyboard = {"id": self.__keyboard_id}
            else:
                keyboard = None
            if self.__content:
                if self.__template_id:
                    logger_msg = "注意content与template_id不可同时存在，注意系统已根据优先级仅保留content"
                json_ = {
                    "markdown": {"content": self.__content},
                    "msg_id": message_id,
                    "event_id": event_id,
                    "keyboard": keyboard,
                }
            else:
                if not self.__template_id or not self.__key_values:
                    return _MessageConstructRet(
                        result=False,
                        error_ret=sdk_error_temp(
                            "注意content与template_id必须存在任意一个，否则消息无法下发！"
                        ),
                    )
                if isinstance(self.__key_values, dict):
                    params = []
                    for k, v in self.__key_values.items():
                        if isinstance(v, list) or isinstance(v, tuple):
                            v = list(v)
                        else:
                            v = [str(v)]
                        params.append({"key": k, "values": v})
                else:
                    try:
                        params = list(self.__key_values)
                        for items in params:
                            for k, v in items.items():
                                if isinstance(v, list) or isinstance(v, tuple):
                                    items[k] = [str(v[0])]
                                else:
                                    items[k] = [str(v)]
                    except Exception:
                        return _MessageConstructRet(
                            result=False,
                            error_ret=sdk_error_temp(
                                "发送markdown消息的key_values仅可以是dict或list[dict]类型！"
                            ),
                        )
                json_ = {
                    "markdown": {
                        "custom_template_id": self.__template_id,
                        "params": params,
                    },
                    "msg_id": message_id,
                    "event_id": event_id,
                    "keyboard": keyboard,
                }
            return _MessageConstructRet(
                result=True, logger_msg=logger_msg, kwargs={"json": json_}
            )
