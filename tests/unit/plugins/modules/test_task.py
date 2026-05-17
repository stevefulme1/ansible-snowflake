# -*- coding: utf-8 -*-
"""Unit tests for the task module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import task

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.task"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "HOURLY_LOAD", "schema_name": "PUBLIC", "database_name": "ANALYTICS_DB",
        "warehouse_name": "COMPUTE_WH", "schedule": "60 MINUTE",
        "sql_statement": "INSERT INTO agg SELECT * FROM raw",
        "after": None, "when_condition": None, "comment": None, "state": "present",
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None, "validate_certs": True}


class TestTaskDocs:
    def test_docs(self):
        assert "task" in task.DOCUMENTATION


class TestTaskCreate:
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
        task.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE TASK" in r["sql"]

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
        task.run_module()
        c.execute_ddl.assert_not_called()

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_missing_sql_fails(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, sql_statement=None)
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = []
        cc.return_value = c
        task.run_module()
        m.fail_json.assert_called_once()


class TestTaskDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, state="absent")
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = [{"name": "HOURLY_LOAD"}]
        cc.return_value = c
        task.run_module()
        assert "DROP TASK" in m.exit_json.call_args[1]["sql"]

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
        task.run_module()
        assert m.exit_json.call_args[1]["changed"] is False
