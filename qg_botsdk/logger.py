import logging
from os import mkdir
from os.path import exists
from time import strftime, localtime


class Logger:
    def __init__(self, bot_app_id: str):
        self.bot_app_id = bot_app_id
        self.logger = logging.getLogger()
        logging.getLogger("websockets.server").disabled = True
        logging.getLogger("websockets.protocol").disabled = True
        logging.getLogger("websockets.client").disabled = True
        logging.getLogger("asyncio").disabled = True
        self.logger.setLevel('DEBUG')
        self.formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s', '%m-%d %H:%M:%S')
        cmdh = logging.StreamHandler()
        cmdh.setFormatter(self.formatter)
        cmdh.setLevel('INFO')
        if not exists('./log'):
            mkdir('./log')
        if not exists(f'./log/{self.bot_app_id}'):
            mkdir(f'./log/{self.bot_app_id}')
        self.logh = logging.FileHandler('./log/{}/{}.log'.format(self.bot_app_id, strftime('%m-%d', localtime())),
                                        encoding='utf-8')
        self.logh.setFormatter(self.formatter)
        self.logger.addHandler(cmdh)
        self.logger.addHandler(self.logh)
        self.previous_time = strftime('%m-%d', localtime())

    def new_logh(self):
        if strftime('%m-%d', localtime()) != self.previous_time:
            self.logger.removeHandler(self.logh)
            self.logh = logging.FileHandler('./log/{}/{}.log'.format(self.bot_app_id, strftime('%m-%d', localtime())),
                                            encoding='utf-8')
            self.logh.setFormatter(self.formatter)
            self.logger.addHandler(self.logh)

    def info(self, msg):
        try:
            self.logger.info(msg)
        except UnicodeDecodeError:
            pass

    def debug(self, msg):
        try:
            self.logger.debug(msg)
        except UnicodeDecodeError:
            pass

    def warning(self, msg):
        try:
            self.logger.warning(msg)
        except UnicodeDecodeError:
            pass

    def error(self, msg):
        try:
            self.logger.error(msg)
        except UnicodeDecodeError:
            pass
