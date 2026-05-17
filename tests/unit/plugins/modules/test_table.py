# -*- coding: utf-8 -*-
"""Unit tests for the table module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import table

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.table"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "EVENTS", "schema_name": "PUBLIC", "database_name": "ANALYTICS_DB",
        "columns": [{"name": "ID", "type": "NUMBER"}, {"name": "TS", "type": "TIMESTAMP_NTZ"}],
        "transient": False, "data_retention_time_in_days": None, "comment": None, "state": "present",
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None, "validate_certs": True}


class TestTableDocs:
    def test_docs(self):
        assert "table" in table.DOCUMENTATION


class TestTableCreate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = []
        cc.return_value = c
        table.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE" in r["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_check_mode(self, mc, cc):
        m = MagicMock()
        m.check_mode = True
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = []
        cc.return_value = c
        table.run_module()
        c.execute_ddl.assert_not_called()


class TestTableUpdate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_alter_comment(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, comment="updated")
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = [{"name": "EVENTS"}]
        cc.return_value = c
        table.run_module()
        assert "ALTER TABLE" in m.exit_json.call_args[1]["sql"]


class TestTableDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, state="absent")
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = [{"name": "EVENTS"}]
        cc.return_value = c
        table.run_module()
        assert "DROP TABLE" in m.exit_json.call_args[1]["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop_absent(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, state="absent")
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = []
        cc.return_value = c
        table.run_module()
        assert m.exit_json.call_args[1]["changed"] is False
