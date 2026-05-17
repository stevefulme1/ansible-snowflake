# -*- coding: utf-8 -*-
"""Unit tests for the database module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import database

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.database"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "ANALYTICS_DB", "state": "present", "transient": False,
        "data_retention_time_in_days": 7, "comment": None,
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None,
        "validate_certs": True}

class TestDatabaseDocs:
    def test_docs(self):
        assert "database" in database.DOCUMENTATION
    def test_return(self):
        assert "database" in database.RETURN

class TestDatabaseCreate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        database.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE" in r["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create_transient(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE, transient=True); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        database.run_module()
        assert "TRANSIENT" in m.exit_json.call_args[1]["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_check_mode(self, mc, cc):
        m = MagicMock(); m.check_mode = True; m.params = dict(BASE); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        database.run_module()
        assert m.exit_json.call_args[1]["changed"] is True
        c.execute_ddl.assert_not_called()

class TestDatabaseUpdate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_alter(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE); mc.return_value = m
        c = MagicMock(); c.query.return_value = [{"name": "ANALYTICS_DB"}]; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        database.run_module()
        assert "ALTER DATABASE" in m.exit_json.call_args[1]["sql"]

class TestDatabaseDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE, state="absent"); mc.return_value = m
        c = MagicMock(); c.query.return_value = [{"name": "X"}]; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        database.run_module()
        assert "DROP DATABASE" in m.exit_json.call_args[1]["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop_absent(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE, state="absent"); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; cc.return_value = c
        database.run_module()
        assert m.exit_json.call_args[1]["changed"] is False
