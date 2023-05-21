#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from unittest import mock

import pytest

import qg_botsdk

from ._base_context import (
    _async_callback,
    _callback,
    bot,
    bot_async,
    config,
    plugin_path,
)

MockMsg = (
    '{"op":0,"s":2,"t":"MESSAGE_CREATE","id":"MESSAGE_CREATE:xxx",'
    '"d":{"author":{"avatar":"xxx","bot":false,"id":"xxx","username":"xxx"},'
    '"channel_id":"channel_id","content":"plugins_test","guild_id":"xxx","id":"id",'
    '"member":{"joined_at":"xxx","nick":"xxx","roles":[]},'
    '"mentions":[],"seq":9555,"seq_in_channel":"9555","timestamp":"xxx"}}'
)

MockMsgAdmin = (
    '{"op":0,"s":2,"t":"MESSAGE_CREATE","id":"MESSAGE_CREATE:xxx",'
    '"d":{"author":{"avatar":"xxx","bot":false,"id":"xxx","username":"xxx"},'
    '"channel_id":"channel_id","content":"plugins_test","guild_id":"xxx","id":"id",'
    '"member":{"joined_at":"xxx","nick":"xxx","roles":["2"]},'
    '"mentions":[],"seq":9555,"seq_in_channel":"9555","timestamp":"xxx"}}'
)

MockOp10Msg = '{"op": 10,"d": {"heartbeat_interval": 45000}}'


@pytest.mark.run_order(2)
class TestRunning:
    bot: qg_botsdk.BOT
    _called_counter: int = 0
    _last_called: float = 0

    async def _start_assertions(self, is_stop=True):
        await asyncio.sleep(1)
        while self.bot._bot_class.disable_reconnect:
            await asyncio.sleep(1)

        assert self.bot.running
        assert self.bot._bot_class is not None
        assert self.bot._bot_class.running
        assert self.bot._bot_class.session_id
        assert self.bot._bot_class.heartbeat
        assert (
            self.bot._bot_class.auth == f'Bot {config["bot_id"]}.{config["bot_token"]}'
        )
        assert self.bot.robot == self.bot._bot_class.robot

        if is_stop:
            self.bot.loop.stop()

    @pytest.mark.timeout(10)
    def test_start(self, bot):
        self.bot = bot
        assert not self.bot.running
        self.bot.loop.create_task(self._start_assertions())
        with pytest.raises(RuntimeError):
            self.bot.start()

    @pytest.mark.timeout(10)
    def test_start_async(self, bot_async):
        self.bot = bot_async
        assert not self.bot.running
        self.bot.loop.create_task(self._start_assertions())
        with pytest.raises(RuntimeError):
            self.bot.start()

    async def _close_assertion(self):
        await self._start_assertions(is_stop=False)

        await self.bot.close()
        assert not self.bot.running
        assert not self.bot._bot_class.running
        assert not self.bot._bot_class.session_id
        assert not self.bot._bot_class.heartbeat
        assert not self.bot._bot_class.auth
        assert not self.bot.robot

    @pytest.mark.timeout(10)
    def test_close(self, bot):
        self.bot = bot
        assert not self.bot.running
        with mock.patch.object(self.bot.logger, "error") as mock_logger:
            self.bot.close()
            mock_logger.assert_called_once()
            assert mock_logger.call_args == mock.call("当前机器人没有运行！")
        self.bot.loop.create_task(self._close_assertion())
        self.bot.start()

    async def _start_assertions_with_proper_close(self):
        await self._start_assertions(is_stop=False)
        self.bot.close()

    @pytest.mark.timeout(10)
    def test_non_blocking_start(self, bot):
        self.bot = bot
        self.bot.start(is_blocking=False)
        self.bot.loop.run_until_complete(asyncio.sleep(0.5))
        self.bot.loop.create_task(self._start_assertions_with_proper_close())
        self.bot.block()

    @pytest.mark.timeout(10)
    def test_start_more_than_once(self, bot):
        self.bot = bot

        with mock.patch.object(self.bot.logger, "error") as mock_logger:
            self.bot.block()
            mock_logger.assert_called_once()
            assert mock_logger.call_args == mock.call("当前机器人没有运行！")

        self.bot.start(is_blocking=False)
        self.bot.loop.run_until_complete(asyncio.sleep(0.5))

        with mock.patch.object(self.bot.logger, "error") as mock_logger:
            self.bot.start()
            mock_logger.assert_called_once()
            assert mock_logger.call_args == mock.call("当前机器人已在运行中！")

        self.bot.close()

    @pytest.mark.timeout(10)
    def test_reconnect(self, bot):
        self.bot = bot
        self.bot.start(is_blocking=False)
        self.bot.loop.run_until_complete(asyncio.sleep(0.5))
        while self.bot._bot_class.heartbeat not in asyncio.all_tasks(self.bot.loop):
            self.bot.loop.run_until_complete(asyncio.sleep(0.1))
        with mock.patch.object(self.bot._bot_class, "ws_send") as mock_ws_send:
            self.bot._bot_class.disable_reconnect = True
            self.bot.loop.create_task(self.bot._bot_class.dispatch_events(MockOp10Msg))
            self.bot.loop.run_until_complete(asyncio.sleep(0.5))
            mock_ws_send.assert_called_once()
            assert '"op": 2' in mock_ws_send.call_args.args[0]
            self.bot._bot_class.disable_reconnect = False
            self.bot._bot_class.is_reconnect = True
            self.bot.loop.create_task(self.bot._bot_class.dispatch_events(MockOp10Msg))
            self.bot.loop.run_until_complete(asyncio.sleep(0.5))
            assert mock_ws_send.call_count == 2
            assert '"op": 6' in mock_ws_send.call_args.args[0]

    @pytest.mark.timeout(10)
    def test_exception_on_ws(self, bot):
        self.bot = bot
        self.bot.start(is_blocking=False)
        self.bot.loop.run_until_complete(asyncio.sleep(0.5))
        while self.bot._bot_class.heartbeat not in asyncio.all_tasks(self.bot.loop):
            self.bot.loop.run_until_complete(asyncio.sleep(0.1))
        with mock.patch.object(self.bot.logger, "error") as mock_logger:
            with mock.patch.object(self.bot._bot_class.ws, "receive") as mock_ws_recv:
                mock_ws_recv.side_effect = ValueError("testing error")
                self.bot._bot_class.disable_reconnect = False
                self.bot.loop.create_task(
                    self.bot._bot_class.dispatch_events(MockOp10Msg)
                )
                while mock_logger.call_count < 2:
                    self.bot.loop.run_until_complete(asyncio.sleep(0.1))
                assert (
                    mock.call(repr(ValueError("testing error")))
                    in mock_logger.call_args_list
                )

    @pytest.mark.timeout(10)
    def test_bind_callback_and_plugins(self, bot):
        self.bot = bot
        self.bot._retrieve_new_plugins()
        self.bot.clear_current_plugins()
        self.bot.bind_msg(_callback)
        self.bot.load_plugins(plugin_path)
        self.bot.load_default_msg_logger()
        self.bot.start(is_blocking=False)
        self.bot.loop.run_until_complete(asyncio.sleep(0.5))
        while self.bot._bot_class.heartbeat not in asyncio.all_tasks(self.bot.loop):
            self.bot.loop.run_until_complete(asyncio.sleep(0.1))
        assert len(self.bot.get_current_preprocessors) == 2
        with mock.patch.object(self.bot.logger, "info") as mock_logger:
            with mock.patch.object(self.bot.api, "send_msg") as mock_send_msg:
                mock_send_msg.return_value = None
                self.bot.loop.create_task(self.bot._bot_class.dispatch_events(MockMsg))
                while not mock_send_msg.called:
                    self.bot.loop.run_until_complete(asyncio.sleep(0.1))
                self.bot.loop.run_until_complete(asyncio.sleep(0.5))
                assert (
                    mock.call("before_command_test", "plugins_test")
                    in mock_logger.call_args_list
                    and mock.call("收到频道 xxx 用户 xxx(xxx) 的消息：plugins_test")
                    in mock_logger.call_args_list
                )
                call_hist = mock_send_msg.call_args_list
                assert len(call_hist) == 2
                assert (
                    mock.call(
                        content="plugins_test",
                        image=None,
                        file_image=None,
                        message_reference_id=None,
                        ignore_message_reference_error=None,
                        message_id="id",
                        channel_id="channel_id",
                    )
                    in call_hist
                )
                assert (
                    mock.call(
                        content="test",
                        image=None,
                        file_image=None,
                        message_reference_id=None,
                        ignore_message_reference_error=None,
                        message_id="id",
                        channel_id="channel_id",
                    )
                    in call_hist
                )

    @pytest.mark.timeout(10)
    def test_async_bind_callback_and_plugins(self, bot_async):
        self.bot = bot_async
        self.bot._retrieve_new_plugins()
        self.bot.clear_current_plugins()
        self.bot.bind_msg(_async_callback)
        self.bot.start(is_blocking=False)
        self.bot.loop.run_until_complete(asyncio.sleep(0.5))
        while self.bot._bot_class.heartbeat not in asyncio.all_tasks(self.bot.loop):
            self.bot.loop.run_until_complete(asyncio.sleep(0.1))
        with mock.patch.object(self.bot.api, "send_msg") as mock_send_msg:
            mock_send_msg.return_value = None
            self.bot.loop.create_task(self.bot._bot_class.dispatch_events(MockMsg))
            while not mock_send_msg.called:
                self.bot.loop.run_until_complete(asyncio.sleep(0.1))
            self.bot.loop.run_until_complete(asyncio.sleep(0.5))
            mock_send_msg.assert_called_once()
            assert mock_send_msg.call_args == mock.call(
                content="test",
                image=None,
                file_image=None,
                message_reference_id=None,
                ignore_message_reference_error=None,
                message_id="id",
                channel_id="channel_id",
            )

    @pytest.mark.timeout(10)
    def test_regex_with_admin(self, bot):
        self.bot = bot
        self.bot._retrieve_new_plugins()
        self.bot.clear_current_plugins()
        self.bot.on_command(
            regex="(.+?)test", is_require_admin=True, admin_error_msg="err"
        )(_callback)
        self.bot.start(is_blocking=False)
        bot.loop.run_until_complete(asyncio.sleep(0.5))
        while self.bot._bot_class.heartbeat not in asyncio.all_tasks(self.bot.loop):
            self.bot.loop.run_until_complete(asyncio.sleep(0.1))
        with mock.patch.object(self.bot.api, "send_msg") as mock_send_msg:
            mock_send_msg.return_value = None
            for i, (mock_msg, ret_msg) in enumerate(
                ((MockMsg, "err"), (MockMsgAdmin, "test"))
            ):
                self.bot.loop.create_task(self.bot._bot_class.dispatch_events(mock_msg))
                while mock_send_msg.call_count <= i:
                    self.bot.loop.run_until_complete(asyncio.sleep(0.1))
                assert mock_send_msg.call_args == mock.call(
                    content=ret_msg,
                    image=None,
                    file_image=None,
                    message_reference_id=None,
                    ignore_message_reference_error=None,
                    message_id="id",
                    channel_id="channel_id",
                )

    def _callback_with_create_dynamic_command(self, data: qg_botsdk.Model.MESSAGE):
        data.reply("dynamic_command_test")
        self.bot.on_command(
            regex="(.+?)test", is_require_admin=True, admin_error_msg="err"
        )(_callback)
        return True

    @pytest.mark.timeout(10)
    def test_dynamic_created_command_on_runtime(self, bot):
        self.bot = bot
        self.bot._retrieve_new_plugins()
        self.bot.clear_current_plugins()
        self.bot.on_command("plugins_test", is_custom_short_circuit=True)(
            self._callback_with_create_dynamic_command
        )
        self.bot.start(is_blocking=False)
        bot.loop.run_until_complete(asyncio.sleep(0.5))
        while self.bot._bot_class.heartbeat not in asyncio.all_tasks(self.bot.loop):
            self.bot.loop.run_until_complete(asyncio.sleep(0.1))
        with mock.patch.object(self.bot.api, "send_msg") as mock_send_msg:
            mock_send_msg.return_value = None
            self.bot.loop.create_task(self.bot._bot_class.dispatch_events(MockMsg))
            while not mock_send_msg.called:
                self.bot.loop.run_until_complete(asyncio.sleep(0.1))
            self.bot.loop.run_until_complete(asyncio.sleep(0.5))
            assert mock_send_msg.call_count == 1
            assert mock_send_msg.call_args == mock.call(
                content="dynamic_command_test",
                image=None,
                file_image=None,
                message_reference_id=None,
                ignore_message_reference_error=None,
                message_id="id",
                channel_id="channel_id",
            )
            assert len(self.bot.get_current_commands) == 2

    async def _test_wait_for_msg_binder(self, data):
        command_obj = qg_botsdk.BotCommandObject(["plugins_test"], treat=False)
        _data = await self.bot.api.wait_for(
            qg_botsdk.Scope.USER, command_obj, timeout=3
        )
        assert _data.content == "plugins_test"
        self._called_counter = 1

    async def _test_wait_for_content(self):
        self._called_counter = 0
        for i in range(2):
            self.bot.loop.create_task(self.bot._bot_class.dispatch_events(MockMsg))
            while not self._called_counter < 1:
                self.bot.loop.run_until_complete(asyncio.sleep(0.1))
            self._called_counter = 0

    @pytest.mark.timeout(10)
    def test_wait_for(self, bot_async):
        self.bot = bot_async
        self.bot.bind_msg(self._test_wait_for_msg_binder)
        self.bot.start(is_blocking=False)
        self.bot.loop.run_until_complete(asyncio.sleep(0.5))
        while self.bot._bot_class.heartbeat not in asyncio.all_tasks(self.bot.loop):
            self.bot.loop.run_until_complete(asyncio.sleep(0.1))
        self.bot.loop.run_until_complete(self._test_wait_for_content())

    def _loop_event(self):
        self.bot.api.send_msg("channel_id", "content test")
        self._called_counter += 1
        time_now = self.bot.loop.time()
        assert time_now - self._last_called >= 1
        self._last_called = time_now

    @pytest.mark.timeout(15)
    def test_loop_event(self, bot):
        self.bot = bot
        bot.register_repeat_event(self._loop_event, 1)
        bot.start(is_blocking=False)
        bot.loop.run_until_complete(asyncio.sleep(0.5))
        while self.bot._bot_class.heartbeat not in asyncio.all_tasks(self.bot.loop):
            self.bot.loop.run_until_complete(asyncio.sleep(0.1))
        with mock.patch.object(self.bot.api, "send_msg") as mock_send_msg:
            mock_send_msg.return_value = None
            while self._called_counter < 2:
                self.bot.loop.run_until_complete(asyncio.sleep(0.1))
            self._called_counter = 0
            assert mock_send_msg.call_count == 2
            assert mock_send_msg.call_args_list[0] == mock.call(
                "channel_id", "content test"
            )
            assert mock_send_msg.call_args_list[1] == mock.call(
                "channel_id", "content test"
            )

    def _start_event(self):
        self._called_counter += 1
        assert self.bot.api.get_bot_info().result

    @pytest.mark.timeout(10)
    def test_start_event(self, bot):
        self.bot = bot
        bot.register_start_event(self._start_event)
        bot.start(is_blocking=False)
        bot.loop.run_until_complete(asyncio.sleep(0.5))
        while self.bot._bot_class.heartbeat not in asyncio.all_tasks(self.bot.loop):
            self.bot.loop.run_until_complete(asyncio.sleep(0.1))
        assert self._called_counter == 1
