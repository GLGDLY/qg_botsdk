import logging
from os import mkdir
from os.path import exists
from time import strftime, localtime


def new_logh():
    global logh
    if strftime('%m-%d', localtime()) != previous_time:
        logger.removeHandler(logh)
        logh = logging.FileHandler('./log/{}.log'.format(strftime('%m-%d', localtime())), encoding='utf-8')
        logh.setFormatter(formatter)
        logger.addHandler(logh)


def info(msg):
    try:
        logger.info(msg)
    except UnicodeDecodeError:
        pass


def debug(msg):
    try:
        logger.debug(msg)
    except UnicodeDecodeError:
        pass


def warning(msg):
    try:
        logger.warning(msg)
    except UnicodeDecodeError:
        pass


def error(msg):
    try:
        logger.error(msg)
    except UnicodeDecodeError:
        pass


logger = logging.getLogger()
logging.getLogger("websockets.server").disabled = True
logging.getLogger("websockets.protocol").disabled = True
logging.getLogger("websockets.client").disabled = True
logging.getLogger("asyncio").disabled = True
logger.setLevel('DEBUG')
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s', '%m-%d %H:%M:%S')  # %(name)s
cmdh = logging.StreamHandler()
cmdh.setFormatter(formatter)
cmdh.setLevel('INFO')
if not exists('./log'):
    mkdir('./log')
logh = logging.FileHandler('./log/{}.log'.format(strftime('%m-%d', localtime())), encoding='utf-8')
logh.setFormatter(formatter)
logger.addHandler(cmdh)
logger.addHandler(logh)
previous_time = strftime('%m-%d', localtime())
