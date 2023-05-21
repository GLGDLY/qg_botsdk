#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from qg_botsdk import Model, Plugins


@Plugins.before_command()
def before_command_test(data: Model.MESSAGE):
    Plugins.logger.info("before_command_test", data.treated_msg)


@Plugins.on_command("plugins_test", is_short_circuit=False)
def plugins_test(data: Model.MESSAGE):
    data.reply("plugins_test")
