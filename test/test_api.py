#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

import qg_botsdk

from ._base_context import bg_bot, config


def data_assertion(data):
    assert getattr(data, "result", None)
    assert hasattr(data, "trace_id")
    assert hasattr(data, "data")


@pytest.mark.run_order(3)
class TestAPI:
    _params = {}

    @pytest.mark.timeout(10)
    def test_security_check(self, bg_bot):
        assert bg_bot.api.security_check("abc")
        assert not bg_bot.api.security_check("操你妈")

    @pytest.mark.timeout(10)
    def test_get_bot_id(self, bg_bot):
        with pytest.raises(DeprecationWarning):
            bg_bot.api.get_bot_id()

    @pytest.mark.timeout(10)
    def test_get_bot_info(self, bg_bot):
        ret = bg_bot.api.get_bot_info()
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_get_bot_guilds(self, bg_bot):
        ret = bg_bot.api.get_bot_guilds()
        data_assertion(ret)
        self._params["guild_id"] = ret.data[0].id

    @pytest.mark.timeout(10)
    def test_get_guild_info(self, bg_bot):
        ret = bg_bot.api.get_guild_info(self._params.get("guild_id"))
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_get_guild_channels(self, bg_bot):
        ret = bg_bot.api.get_guild_channels(self._params.get("guild_id"))
        data_assertion(ret)
        for item in ret.data:
            if item.type == 0:
                self._params["channel_id"] = item.id

    @pytest.mark.timeout(10)
    def test_get_channels_info(self, bg_bot):
        ret = bg_bot.api.get_channels_info(self._params.get("channel_id"))
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_create_channels(self, bg_bot):
        ret = bg_bot.api.create_channels(
            self._params.get("guild_id"),
            "test0",
            0,
            0,
        )
        data_assertion(ret)
        self._params["channel_id"] = ret.data.id

    # skipped: patch_channels

    @pytest.mark.timeout(10)
    def test_delete_channels(self, bg_bot):
        ret = bg_bot.api.delete_channels(self._params.get("channel_id"))
        data_assertion(ret)

    # skipped: get_online_nums

    @pytest.mark.timeout(10)
    def test_get_guild_members(self, bg_bot):
        ret = bg_bot.api.get_guild_members(self._params.get("guild_id"))
        data_assertion(ret)
        self._params["user_id"] = ret.data[0].user.id

    @pytest.mark.timeout(10)
    def test_get_role_members(self, bg_bot):
        ret = bg_bot.api.get_role_members(self._params.get("guild_id"), "2")
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_get_member_info(self, bg_bot):
        ret = bg_bot.api.get_member_info(
            self._params.get("guild_id"), self._params.get("user_id")
        )
        data_assertion(ret)

    # skipped: delete_member

    @pytest.mark.timeout(10)
    def test_get_guild_roles(self, bg_bot):
        ret = bg_bot.api.get_guild_roles(self._params.get("guild_id"))
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_create_role(self, bg_bot):
        ret = bg_bot.api.create_role(self._params.get("guild_id"), "test0")
        data_assertion(ret)
        self._params["role_id"] = ret.data.role_id

    @pytest.mark.timeout(10)
    def test_patch_role(self, bg_bot):
        ret = bg_bot.api.patch_role(
            self._params.get("guild_id"), self._params.get("role_id"), "test1"
        )
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_delete_role(self, bg_bot):
        ret = bg_bot.api.delete_role(
            self._params.get("guild_id"), self._params.get("role_id")
        )
        data_assertion(ret)

    # skipped: create_role_member, delete_role_member

    # skipped: get_channel_member_permission, get_channel_role_permission

    # skipped: put_channel_member_permission, put_channel_role_permission

    @pytest.mark.timeout(10)
    def test_send_msg(self, bg_bot):
        ret = bg_bot.api.send_msg(self._params.get("channel_id"), "test")
        data_assertion(ret)
        self._params["message_id"] = ret.data.id

    @pytest.mark.timeout(10)
    def test_get_message_info(self, bg_bot):
        ret = bg_bot.api.get_message_info(
            self._params.get("channel_id"), self._params.get("message_id")
        )
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_send_embed(self, bg_bot):
        ret = bg_bot.api.send_embed(self._params.get("channel_id"), "test", "test")
        data_assertion(ret)
        self._params["message_id"] = ret.data.id

    # skipped: send_ark_23, send_ark_24, send_ark_37, send_markdown

    @pytest.mark.timeout(10)
    def test_get_guild_setting(self, bg_bot):
        ret = bg_bot.api.get_guild_setting(self._params.get("guild_id"))
        data_assertion(ret)

    # skipped: create_dm_guild, send_dm, delete_dm_msg
    # skipped: mute_all_member, mute_member, mute_members

    @pytest.mark.timeout(10)
    def test_create_announce(self, bg_bot):
        ret = bg_bot.api.create_announce(
            self._params.get("guild_id"),
            "test",
            recommend_channels_id=[self._params.get("channel_id")],
            recommend_channels_introduce=["testing"],
        )
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_delete_announce(self, bg_bot):
        ret = bg_bot.api.delete_announce(self._params.get("guild_id"))
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_create_pinmsg(self, bg_bot):
        ret = bg_bot.api.create_pinmsg(
            self._params.get("channel_id"), self._params.get("message_id")
        )
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_delete_pinmsg(self, bg_bot):
        ret = bg_bot.api.delete_pinmsg(
            self._params.get("channel_id"), self._params.get("message_id")
        )
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_get_pinmsg(self, bg_bot):
        ret = bg_bot.api.get_pinmsg(self._params.get("channel_id"))
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_get_schedules(self, bg_bot):
        ret = bg_bot.api.get_schedules(self._params.get("guild_id"))
        data_assertion(ret)

    # skipped: test_create_schedule, create_schedule, patch_schedule, delete_schedule

    @pytest.mark.timeout(10)
    def test_create_reaction(self, bg_bot):
        ret = bg_bot.api.create_reaction(
            self._params.get("channel_id"),
            self._params.get("message_id"),
            "2",
            "128516",
        )
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_get_reaction_users(self, bg_bot):
        ret = bg_bot.api.get_reaction_users(
            self._params.get("channel_id"),
            self._params.get("message_id"),
            "2",
            "128516",
        )
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_delete_reaction(self, bg_bot):
        ret = bg_bot.api.delete_reaction(
            self._params.get("channel_id"),
            self._params.get("message_id"),
            "2",
            "128516",
        )
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_delete_msg(self, bg_bot):
        ret = bg_bot.api.delete_msg(
            self._params.get("channel_id"), self._params.get("message_id")
        )
        data_assertion(ret)

    # skipped: control_audio, bot_on_mic, bot_off_mic, get_threads, get_thread_info, create_thread, delete_thread

    @pytest.mark.timeout(10)
    def test_get_guild_permissions(self, bg_bot):
        ret = bg_bot.api.get_guild_permissions(self._params.get("guild_id"))
        data_assertion(ret)

    @pytest.mark.timeout(10)
    def test_create_permission_demand(self, bg_bot):
        ret = bg_bot.api.create_permission_demand(
            self._params.get("guild_id"), self._params.get("channel_id"), "create_role"
        )
        data_assertion(ret)
