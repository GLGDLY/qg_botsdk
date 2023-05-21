#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from asyncio import sleep

import pytest

from qg_botsdk._session import SessionManager
from qg_botsdk._utils import objectize
from qg_botsdk.logger import Logger
from qg_botsdk.model import Scope, SessionStatus

from ._base_context import bot_async, config

MockObj = objectize(
    {
        "author": {"avatar": "xxx", "bot": False, "id": "111", "username": "xxx"},
        "channel_id": "222",
        "content": "plugins_test",
        "treated_msg": "plugins_test",
        "guild_id": "333",
        "id": "444",
        "member": {"joined_at": "xxx", "nick": "xxx", "roles": []},
        "mentions": [],
        "seq": 9555,
        "seq_in_channel": "9555",
        "timestamp": "xxx",
        "t": "MESSAGE_CREATE",
    }
)


@pytest.fixture()
def session(bot_async):
    _session = SessionManager(Logger(config["bot_id"]))
    _session.api = bot_async.api
    _session.start(bot_async.loop)
    return _session


@pytest.mark.run_order(1)
class TestSession:
    @pytest.mark.timeout(10)
    def test_session_base(self, session):
        session.remove()
        for _scope in (_all_data := session.get_all()):
            assert _all_data[_scope] == {}
        assert session.get(MockObj, Scope.USER, "test") is None
        session.new(MockObj, Scope.USER, "test", data={"test": "test"})
        session.new(MockObj, Scope.USER, "test", data={"test": "test"})
        session.new(MockObj, Scope.GUILD, "test", data={"test": "test"})
        with pytest.raises(KeyError):
            session.new(
                MockObj, Scope.USER, "test", data={"test": "test"}, is_replace=False
            )
        session.new(MockObj, Scope.USER, "test1", data={"test1": "test1"})
        session.new(MockObj, Scope.CHANNEL, "test", data={"test": "test"})
        session.new(MockObj, Scope.GLOBAL, "test", data={"test": "test"})
        _all_data = session.get_all()
        assert len(_all_data[Scope.USER.value]["111"]) == 2
        assert len(_all_data[Scope.GUILD.value]["333"]) == 1
        assert len(_all_data[Scope.CHANNEL.value]["222"]) == 1
        assert len(_all_data[Scope.GLOBAL.value]) == 1
        assert _all_data[Scope.USER.value]["111"]["test"].data == {"test": "test"}
        assert _all_data[Scope.USER.value]["111"]["test1"].data == {"test1": "test1"}
        assert _all_data[Scope.GUILD.value]["333"]["test"].data == {"test": "test"}
        assert _all_data[Scope.CHANNEL.value]["222"]["test"].data == {"test": "test"}
        assert _all_data[Scope.GLOBAL.value]["test"].data == {"test": "test"}
        session.remove(Scope.GUILD, "333", "test")
        assert session.get(MockObj, Scope.GUILD, "test") is None
        _all_data = session.get_all()
        assert len(_all_data[Scope.USER.value]["111"]) == 2
        assert len(_all_data[Scope.GUILD.value]["333"]) == 0
        assert len(_all_data[Scope.CHANNEL.value]["222"]) == 1
        assert len(_all_data[Scope.GLOBAL.value]) == 1
        session.remove(Scope.USER)
        print(_all_data[Scope.USER.value])
        assert len(session.get_all()[Scope.USER.value]) == 0
        session.remove()
        for _scope in (_all_data := session.get_all()):
            assert _all_data[_scope] == {}

    @pytest.mark.timeout(10)
    def test_internal(self, session):
        with pytest.raises(ValueError):
            session._SessionManager__check_path("test.db")
        with pytest.raises(ValueError):
            session._SessionManager__check_path("__init__.py")
        assert session._SessionManager__valid_scope(Scope.USER) == "USER"
        assert session._SessionManager__valid_scope(Scope.USER.value) == "USER"
        with pytest.raises(ValueError):
            session._SessionManager__valid_scope("abc")

    @pytest.mark.timeout(10)
    def test_get_data(self, session):
        session_data_from_new = session.new(
            MockObj, Scope.USER, "test", data={"test": "test"}
        )
        session_data_from_get = session.get(MockObj, Scope.USER, "test")
        assert session_data_from_new.data == session_data_from_get.data
        assert session_data_from_new.scope == session_data_from_get.scope
        assert session_data_from_new.key == session_data_from_get.key
        assert session_data_from_new.status == session_data_from_get.status
        assert session_data_from_new.identify == session_data_from_get.identify
        assert session_data_from_get.scope == Scope.USER.value
        assert session_data_from_get.key == "test"
        assert session_data_from_get.status == SessionStatus.ACTIVE
        assert session_data_from_get.data == {"test": "test"}

    @pytest.mark.timeout(10)
    def test_timeout(self, bot_async, session):
        session.remove()
        session.new(MockObj, Scope.USER, "test", data={"test": "test"})
        assert (
            session.get_all()[Scope.USER.value]["111"]["test"].status
            == SessionStatus.ACTIVE
        )
        session.end(MockObj, Scope.USER, "test")
        assert (
            session.get_all()[Scope.USER.value]["111"]["test"].status
            == SessionStatus.INACTIVE
        )
        bot_async.loop.run_until_complete(sleep(0.2))
        assert "111" not in session.get_all()[Scope.USER.value]
        session.new(MockObj, Scope.USER, "test", data={"test": "test"}, timeout=0.1)
        assert (
            session.get_all()[Scope.USER.value]["111"]["test"].status
            == SessionStatus.ACTIVE
        )
        bot_async.loop.run_until_complete(sleep(0.2))
        assert "111" not in session.get_all()[Scope.USER.value]
        session.new(MockObj, Scope.USER, "test", data={"test": "test"})
        session.end(MockObj, Scope.USER, "test", inactive_gc_timeout=0.5)
        assert (
            session.get_all()[Scope.USER.value]["111"]["test"].status
            == SessionStatus.INACTIVE
        )
        bot_async.loop.run_until_complete(sleep(0.2))
        assert (
            session.get_all()[Scope.USER.value]["111"]["test"].status
            == SessionStatus.INACTIVE
        )
        bot_async.loop.run_until_complete(sleep(0.5))
        assert "111" not in session.get_all()[Scope.USER.value]

    @pytest.mark.timeout(10)
    def test_set_get_status(self, bot_async, session):
        session.remove()
        session.new(MockObj, Scope.USER, "test", data={"test": "test"})
        session.set_status(MockObj, Scope.USER, "test", SessionStatus.HANGING)
        assert session.get_status(MockObj, Scope.USER, "test") == SessionStatus.HANGING
        assert (
            session.get_all()[Scope.USER.value]["111"]["test"].status
            == SessionStatus.HANGING
        )
        assert session.get(MockObj, Scope.USER, "test").status == SessionStatus.ACTIVE
        assert session.get(MockObj, Scope.USER, "test").status == SessionStatus.ACTIVE
        session.set_status(MockObj, Scope.USER, "test", SessionStatus.INACTIVE)
        assert (
            session.get_all()[Scope.USER.value]["111"]["test"].status
            == SessionStatus.INACTIVE
        )
        bot_async.loop.run_until_complete(sleep(0.2))
        assert session.get(MockObj, Scope.USER, "test") is None

    @pytest.mark.timeout(10)
    def test_set_auto_commit(self, session):
        session.remove()
        assert session._SessionManager__is_auto_commit
        session.set_auto_commit(False)
        assert not session._SessionManager__is_auto_commit

    @pytest.mark.timeout(10)
    def test_commit(self, session):
        session.remove()
        _data = session.get_all()
        session.commit_data()
        session.fetch_data()
        assert session.get_all() == _data
        default_path = os.path.join(os.getcwd(), "session_data")
        assert os.path.exists(
            os.path.join(default_path, f"session_{config['bot_id']}.db")
        )
        new_path = os.path.join(default_path, "session_data")
        session.set_commit_path(new_path)
        session.commit_data()
        assert os.path.exists(os.path.join(new_path, f"session_{config['bot_id']}.db"))
