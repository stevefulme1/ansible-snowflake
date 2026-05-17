# -*- coding: utf-8 -*-
"""Unit tests for the stream module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import stream

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.stream"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "EVENTS_STREAM", "schema_name": "PUBLIC", "database_name": "ANALYTICS_DB",
        "source_table": "ANALYTICS_DB.PUBLIC.EVENTS", "append_only": False,
        "show_initial_rows": False, "comment": None, "state": "present",
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None, "validate_certs": True}


class TestStreamDocs:
    def test_docs(self):
        assert "stream" in stream.DOCUMENTATION


class TestStreamCreate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        stream.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE STREAM" in r["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create_append_only(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, append_only=True)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        stream.run_module()
        assert "APPEND_ONLY = TRUE" in m.exit_json.call_args[1]["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_check_mode(self, mc, cc):
        m = MagicMock()
        m.check_mode = True
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        stream.run_module()
        c.execute_ddl.assert_not_called()

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_missing_source_fails(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, source_table=None)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        stream.run_module()
        m.fail_json.assert_called_once()


class TestStreamDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, state="absent")
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        stream.run_module()
        assert "DROP STREAM" in m.exit_json.call_args[1]["sql"]
