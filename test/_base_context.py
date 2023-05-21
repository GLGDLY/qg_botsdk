#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from io import StringIO
from os import getcwd, getenv
from threading import Thread

import pytest

import qg_botsdk

if getcwd().endswith("test"):
    read_path = "./config/config.yaml"
    plugin_path = "./_testing_plugin.py"
else:
    read_path = "./test/config/config.yaml"
    plugin_path = "./test/_testing_plugin.py"

try:
    config: dict
    raw_config = getenv("TEST_CONFIG", None)
    if raw_config:
        config = qg_botsdk.utils.read_yaml(StringIO(raw_config))
    else:
        config = qg_botsdk.utils.read_yaml(read_path)
except FileNotFoundError:
    raise FileNotFoundError(
        "请先参考test/config/config.example.yaml，创建test/config/config.yaml文件进行单元测试"
    )


@pytest.fixture()
def bot():
    return qg_botsdk.BOT(
        bot_id=config["bot_id"],
        bot_token=config["bot_token"],
        is_private=True,
        is_sandbox=True,
    )


@pytest.fixture()
def bot_async():
    return qg_botsdk.BOT(
        bot_id=config["bot_id"],
        bot_token=config["bot_token"],
        is_private=True,
        is_async=True,
        is_sandbox=True,
    )


@pytest.fixture(scope="class")
def bg_bot() -> qg_botsdk.BOT:
    bot = qg_botsdk.BOT(
        bot_id=config["bot_id"],
        bot_token=config["bot_token"],
        is_sandbox=True,
        api_timeout=3,
    )
    Thread(target=bot.start, daemon=True).start()
    bot.security_setup(config["mini_id"], config["mini_token"])
    return bot


def _callback(data):
    data.reply("test")


async def _async_callback(data):
    await data.reply("test")
