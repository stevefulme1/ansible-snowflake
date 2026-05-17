# -*- coding: utf-8 -*-
"""Unit tests for the view module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import view

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.view"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "ACTIVE_USERS", "schema_name": "PUBLIC", "database_name": "ANALYTICS_DB",
        "query": "SELECT * FROM USERS WHERE active = TRUE", "secure": False,
        "comment": None, "state": "present",
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None, "validate_certs": True}


class TestViewDocs:
    def test_docs(self):
        assert "view" in view.DOCUMENTATION


class TestViewCreate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        view.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE OR REPLACE VIEW" in r["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create_secure(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, secure=True)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        view.run_module()
        assert "SECURE VIEW" in m.exit_json.call_args[1]["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_check_mode(self, mc, cc):
        m = MagicMock()
        m.check_mode = True
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        view.run_module()
        c.execute_ddl.assert_not_called()

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_missing_query_fails(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, query=None)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        view.run_module()
        m.fail_json.assert_called_once()


class TestViewDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, state="absent")
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        view.run_module()
        assert "DROP VIEW" in m.exit_json.call_args[1]["sql"]
