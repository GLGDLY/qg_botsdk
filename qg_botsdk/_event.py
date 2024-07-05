from json import JSONDecodeError, dumps
from typing import Callable, Dict

from ._statics import EventIDEvents, MsgIDEvents

v1_reply_args = (
    "content",
    "image",
    "file_image",
    "message_reference_id",
    "ignore_message_reference_error",
)
v1_reply_args_len = len(v1_reply_args)
v2_reply_args = (
    "content",
    "media_file_info",
    "message_reference_id",
    "ignore_message_reference_error",
    "msg_seq",
)
v2_reply_args_len = len(v2_reply_args)


class object_class:
    def __init__(self, _static_copy, _data):
        self.__dict__.update(_data)
        self._static_copy = _static_copy

    def __doc__(self):
        return self._static_copy

    def __repr__(self):
        return self._static_copy

    @property
    def dict(self):
        return self._static_copy


def _event_class_reply_get_api(
    obj: object_class, args: tuple, kwargs: Dict
) -> Callable:
    t = getattr(obj, "t", None)

    if t in MsgIDEvents:
        kwargs["message_id"] = getattr(obj, "id", None)
    elif t in EventIDEvents:
        kwargs["message_id"] = getattr(obj, "event_id", None)

    if "DIRECT_MESSAGE" in t:
        if len(args) > v1_reply_args_len:
            raise TypeError(
                f"reply() takes {v1_reply_args_len} positional arguments but {len(args)} were given"
            )
        kwargs.update(zip(v1_reply_args, args))
        kwargs["guild_id"] = getattr(obj, "guild_id", None)
        return obj.api.send_dm
    elif "C2C_MESSAGE" in t:
        if len(args) > v2_reply_args_len:
            raise TypeError(
                f"reply() takes {v2_reply_args_len} positional arguments but {len(args)} were given"
            )
        kwargs.update(zip(v2_reply_args, args))
        kwargs["user_openid"] = getattr(
            getattr(obj, "author", object()), "user_openid", None
        )
        return obj.api.send_qq_dm
    elif "GROUP_AT_MESSAGE" in t:
        if len(args) > v2_reply_args_len:
            raise TypeError(
                f"reply() takes {v2_reply_args_len} positional arguments but {len(args)} were given"
            )
        kwargs.update(zip(v2_reply_args, args))
        kwargs["group_openid"] = getattr(obj, "group_openid", None)
        return obj.api.send_group_msg
    else:  # EVENTS.MESSAGE_CREATE
        if len(args) > v1_reply_args_len:
            raise TypeError(
                f"reply() takes {v1_reply_args_len} positional arguments but {len(args)} were given"
            )
        kwargs.update(zip(v1_reply_args, args))
        kwargs["channel_id"] = (
            obj.channel_id if hasattr(obj, "channel_id") else getattr(obj, "id", None)
        )
        return obj.api.send_msg


class event_class(object_class):
    def reply(self, *args, **kwargs):
        try:
            api = _event_class_reply_get_api(self, args, kwargs)
        except AttributeError:
            raise AttributeError("无法获取回复消息的相应API")
        return api(**kwargs)


class async_event_class(object_class):
    async def reply(self, *args, **kwargs):
        try:
            api = _event_class_reply_get_api(self, args, kwargs)
        except AttributeError:
            raise AttributeError("无法获取回复消息的相应API")
        return await api(**kwargs)


def objectize(
    data, api=None, is_async=False
):  # if api is not None, the event is a resp class
    if isinstance(data, dict):
        try:
            _static_copy = dumps(data)
        except (TypeError, JSONDecodeError):
            _static_copy = str(data)
        # main func to process data
        for keys, values in data.items():
            if keys.isnumeric():
                return data
            if isinstance(values, dict):
                data[keys] = objectize(values)
            elif isinstance(values, list):
                for i, items in enumerate(values):
                    if isinstance(items, dict):
                        data[keys][i] = objectize(items)
        if api:
            data["api"] = api
            object_data = (
                async_event_class(_static_copy, data)
                if is_async
                else event_class(_static_copy, data)
            )
        else:
            object_data = object_class(_static_copy, data)
        return object_data
    else:
        return data
