#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import typing
from asyncio import Queue as AsyncQueue
from io import StringIO
from logging import FileHandler, Formatter, StreamHandler, getLogger
from os import PathLike, getcwd, makedirs, sep
from os.path import exists, isdir, join
from re import split as re_split
from time import localtime, strftime

try:
    from colorama import init as color_init

    color_init(strip=False)
except (ImportError, ModuleNotFoundError):
    from os import system

    system("")


class Logger:
    __instances = {}

    def __new__(cls, *args, **kwargs):
        bot_app_id = kwargs.get("bot_app_id", None) or args[0]
        instance = cls.__instances.get(bot_app_id, None)
        if instance:
            return instance
        else:
            instance = super().__new__(cls)
            cls.__instances[bot_app_id] = instance
            return instance

    def __init__(
        self,
        bot_app_id: str,
        file_path: typing.Union[str, PathLike] = None,
        disable_logger: typing.List[str] = None,
    ):
        """
        用作logging输出的类，支持不同level的颜色log输出，可自定义格式

        :param bot_app_id: 机器人ID
        :param file_path: 可选填，自定义log文件输出路径，不填默认为：当前目录/log/[bot_app_id]/
        :param disable_logger: 可选填，需要disable的logger名称列表，不填默认无
        """
        getLogger("asyncio").disabled = True
        if disable_logger:
            for items in disable_logger:
                getLogger(items).disabled = True
        self.bot_app_id = str(bot_app_id)
        self._logger = getLogger(self.bot_app_id)
        self._logger.handlers.clear()
        self._logger.setLevel("DEBUG")
        self._format = "[%(asctime)s] [%(levelname)s] %(message)s"
        self._date_format = "%Y-%m-%d %H:%M:%S"
        self._cmdh = StreamHandler()
        self._cmdh.setFormatter(self._Stream_Formatter())
        self._cmdh.setLevel("INFO")
        self.file_path = file_path
        if file_path is not None:
            file_path = re_split(r"[\\|/]", file_path)
            if file_path[0] == ".":
                self.file_path = join(*file_path)
            else:
                file_path[0] += sep
                self.file_path = join(sep, *file_path)
        else:
            self.file_path = join(getcwd(), "log", self.bot_app_id)
        if not exists(self.file_path):
            makedirs(self.file_path)
        assert isdir(self.file_path), "自定义Log输出路径必须为一个directory资料夹"
        self._logh = None
        self._new_logh(strftime("%Y-%m-%d", localtime()))
        self._logger.addHandler(self._cmdh)
        self._previous_time = strftime("%Y-%m-%d", localtime())
        # self._previous_time = "12-16"
        self.event_queue = AsyncQueue()

    class _Stream_Formatter(Formatter):
        FORMATS = {
            20: "\033[1;32m[%(asctime)s] [%(levelname)s]\033[0m %(message)s",
            30: "\033[1;33m[%(asctime)s] [%(levelname)s]\033[0m %(message)s",
            40: "\033[1;31m[%(asctime)s] [%(levelname)s]\033[0m %(message)s",
        }

        def __init__(self, formats: typing.Dict = None, date_format: str = None):
            super().__init__()
            if formats is not None:
                self.FORMATS[20] = formats.get(20, None) or self.FORMATS[20]
                self.FORMATS[30] = formats.get(30, None) or self.FORMATS[30]
                self.FORMATS[40] = formats.get(40, None) or self.FORMATS[40]
            self._date_format = date_format or "%Y-%m-%d %H:%M:%S"

        def format(self, record) -> str:
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = Formatter(log_fmt, self._date_format)
            return formatter.format(record)

    def setLevel(
        self,
        level: typing.Union[int, str],
        logger: typing.Literal["console", "file"] = "console",
    ):
        """
        用于设置logger的level，同logging.logger.setLevel()

        `在docs.python.org查阅更多资讯
        <https://docs.python.org/zh-cn/3.10/library/logging.html#logging.Logger.setLevel>`_

        :param level: level必须是int或str
        :param logger: 需要设置level的logger，允许传值为'console'或'file'，默认为'console'
        """
        self._logger.setLevel(level)

    def set_formatter(
        self,
        debug_format: str = None,
        info_format: str = None,
        warning_format: str = None,
        error_format: str = None,
        date_format: str = None,
    ):
        """
        用于更改logger日志的输出格式

        - 更多关于格式的相关信息可参阅：
        - https://docs.python.org/zh-cn/3/library/logging.html#logging.Formatter
        - https://docs.python.org/zh-cn/3.6/library/logging.html#logrecord-attributes

        :param debug_format: debug层级的格式，此格式会输出到保存的日志文件中
        :param info_format: info层级StreamHandler的格式，此格式会输出到python console中显示
        :param warning_format: warning层级StreamHandler的格式，此格式会输出到python console中显示
        :param error_format: error层级StreamHandler的格式，此格式会输出到python console中显示
        :param date_format: 全局所有层级的日期格式
        """
        self._date_format = date_format or self._date_format
        self._format = debug_format or self._format
        formats = {20: info_format, 30: warning_format, 40: error_format}
        self._cmdh.setFormatter(self._Stream_Formatter(formats, date_format))
        self._logh.setFormatter(Formatter(self._format, self._date_format))

    @staticmethod
    def disable_logger(loggers: typing.Union[str, typing.List[str]]):
        """
        用于disable禁用logger

        :param loggers: 需要禁用的logger名称或名称列
        """
        if isinstance(loggers, typing.List):
            for items in loggers:
                getLogger(items).disabled = True
        else:
            getLogger(loggers).disabled = True

    def _new_logh(self, str_time):
        self._logh = FileHandler(
            join(self.file_path, f"{str_time}.log"), encoding="utf-8"
        )
        self._logh.setFormatter(Formatter(self._format, self._date_format))
        self._logger.addHandler(self._logh)

    @staticmethod
    def __print_args_to_str(*args, **kwargs):
        buf = StringIO()
        kwargs["end"] = kwargs.get("end", "")
        kwargs["file"] = buf
        print(*args, **kwargs)
        ret = buf.getvalue()
        buf.close()
        return ret

    async def start(self):
        while True:
            func, args, kwargs = await self.event_queue.get()
            str_time = strftime("%Y-%m-%d", localtime())
            if str_time != self._previous_time:
                self._previous_time = str_time
                self._logger.removeHandler(self._logh)
                self._new_logh(str_time)
            try:
                getattr(self._logger, func)(*args, **kwargs)
                while (
                    not self.event_queue.empty()
                ):  # no need check logh update again before all queued tasks are done
                    func, args, kwargs = self.event_queue.get_nowait()
                    getattr(self._logger, func)(*args, **kwargs)
            except UnicodeDecodeError:
                pass

    def __queue_task(self, func: str, *args, **kwargs):
        self.event_queue.put_nowait((func, args, kwargs))

    def debug(self, *args, **kwargs):
        self.__queue_task("debug", self.__print_args_to_str(*args, **kwargs))

    def info(self, *args, **kwargs):
        self.__queue_task("info", self.__print_args_to_str(*args, **kwargs))

    def warning(self, *args, **kwargs):
        self.__queue_task("warning", self.__print_args_to_str(*args, **kwargs))

    def error(self, *args, **kwargs):
        self.__queue_task("error", self.__print_args_to_str(*args, **kwargs))
