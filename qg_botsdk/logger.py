# !/usr/bin/env python3
# encoding: utf-8
from logging import getLogger, Formatter, StreamHandler, FileHandler
from os import mkdir
from os.path import exists
from time import strftime, localtime
from inspect import stack


def __getattr__(identifier: str) -> object:
    if stack()[1].filename.split('\\')[-1] != 'qg_bot.py':
        raise AssertionError("此为SDK内部使用文件，无法使用，使用log请使用from qg_bot.py import BOT，实例化BOT后使用BOT().logger")

    return globals()[identifier.__path__]


class Logger:
    def __init__(self, bot_app_id: str):
        for items in ["websockets.server", "websockets.protocol", "websockets.client", "asyncio"]:
            getLogger(items).disabled = True
        self.__bot_app_id = bot_app_id
        self.__logger = getLogger()
        self.__logger.setLevel('DEBUG')
        self.__formatter = Formatter('[%(asctime)s] [%(levelname)s]: %(message)s', '%m-%d %H:%M:%S')
        self.__cmdh = StreamHandler()
        self.__cmdh.setFormatter(self.__formatter)
        self.__cmdh.setLevel('INFO')
        if not exists('./log'):
            mkdir('./log')
        if not exists(f'./log/{self.__bot_app_id}'):
            mkdir(f'./log/{self.__bot_app_id}')
        self.__logh = None
        self.__new_logh(strftime('%m-%d', localtime()))
        self.__logger.addHandler(self.__cmdh)
        self.__previous_time = strftime('%m-%d', localtime())

    def set_formatter(self, str_format: str, date_format: str):
        self.__formatter = Formatter(str_format, date_format)
        self.__cmdh.setFormatter(self.__formatter)
        self.__logh.setFormatter(self.__formatter)

    def __new_logh(self, str_time):
        self.__logh = FileHandler('./log/{}/{}.log'.format(self.__bot_app_id, str_time), encoding='utf-8')
        self.__logh.setFormatter(self.__formatter)
        self.__logger.addHandler(self.__logh)

    def __check_date(self):
        str_time = strftime('%m-%d', localtime())
        if str_time != self.__previous_time:
            self.__logger.removeHandler(self.__logh)
            self.__new_logh(str_time)

    def info(self, msg):
        self.__check_date()
        try:
            self.__logger.info(msg)
        except UnicodeDecodeError:
            pass

    def debug(self, msg):
        self.__check_date()
        try:
            self.__logger.debug(msg)
        except UnicodeDecodeError:
            pass

    def warning(self, msg):
        self.__check_date()
        try:
            self.__logger.warning(msg)
        except UnicodeDecodeError:
            pass

    def error(self, msg):
        self.__check_date()
        try:
            self.__logger.error(msg)
        except UnicodeDecodeError:
            pass
