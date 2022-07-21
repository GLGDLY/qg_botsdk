# !/usr/bin/env python3
# encoding: utf-8
from logging import getLogger, Formatter, StreamHandler, FileHandler
from os import mkdir
from os.path import exists
from time import strftime, localtime
from inspect import stack
from functools import wraps
from colorama import init as color_init

color_init(strip=False)


def __getattr__(identifier: str) -> object:
    if stack()[1].filename.split('\\')[-1] != 'qg_bot.py':
        raise AssertionError("此为SDK内部使用文件，无法使用，使用log请使用from qg_bot.py import BOT，实例化BOT后使用BOT().logger")

    return globals()[identifier.__path__]


def _check_date(func):
    @wraps(func)
    def wrap(self, msg):
        str_time = strftime('%m-%d', localtime())
        if str_time != self._previous_time:
            self._logger.removeHandler(self._logh)
            self._new_logh(str_time)
        try:
            func(self, msg)
        except UnicodeDecodeError:
            pass

    return wrap


class Logger:
    def __init__(self, bot_app_id: str):
        for items in ["websockets.server", "websockets.protocol", "websockets.client", "asyncio"]:
            getLogger(items).disabled = True
        self._bot_app_id = bot_app_id
        self._logger = getLogger(__name__)
        self._logger.setLevel('DEBUG')
        self._format = '[%(asctime)s] [%(levelname)s] %(message)s'
        self._date_format = '%m-%d %H:%M:%S'
        self._cmdh = StreamHandler()
        self._cmdh.setFormatter(self._Stream_Formatter())
        self._cmdh.setLevel('INFO')
        if not exists('./log'):
            mkdir('./log')
        if not exists(f'./log/{self._bot_app_id}'):
            mkdir(f'./log/{self._bot_app_id}')
        self._logh = None
        self._new_logh(strftime('%m-%d', localtime()))
        self._logger.addHandler(self._cmdh)
        self._previous_time = strftime('%m-%d', localtime())

    class _Stream_Formatter(Formatter):
        FORMATS = {20: '\033[1;32m[%(asctime)s] [%(levelname)s]\033[0m %(message)s',
                   30: '\033[1;33m[%(asctime)s] [%(levelname)s]\033[0m %(message)s',
                   40: '\033[1;31m[%(asctime)s] [%(levelname)s]\033[0m %(message)s'}

        def __init__(self, formats: dict = None, date_format: str = None):
            super().__init__()
            if formats is not None:
                self.FORMATS[20] = formats.get(20, None) or self.FORMATS[20]
                self.FORMATS[30] = formats.get(30, None) or self.FORMATS[30]
                self.FORMATS[40] = formats.get(40, None) or self.FORMATS[40]
            self._date_format = date_format or '%m-%d %H:%M:%S'

        def format(self, record) -> str:
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = Formatter(log_fmt, self._date_format)
            return formatter.format(record)

    def set_formatter(self, debug_format: str = None, info_format: str = None, warning_format: str = None,
                      error_format: str = None, date_format: str = None):
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

    def _new_logh(self, str_time):
        self._logh = FileHandler('./log/{}/{}.log'.format(self._bot_app_id, str_time), encoding='utf-8')
        self._logh.setFormatter(Formatter(self._format, self._date_format))
        self._logger.addHandler(self._logh)

    @_check_date
    def debug(self, msg):
        self._logger.debug(msg)

    @_check_date
    def info(self, msg):
        self._logger.info(msg)

    @_check_date
    def warning(self, msg):
        self._logger.warning(msg)

    @_check_date
    def error(self, msg):
        self._logger.error(msg)
