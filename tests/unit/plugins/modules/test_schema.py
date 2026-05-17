# -*- coding: utf-8 -*-
"""Unit tests for the schema module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import schema

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.schema"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "RAW", "database": "ANALYTICS_DB", "state": "present",
        "transient": False, "data_retention_time_in_days": None, "comment": None,
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "schema": None,
        "validate_certs": True}

class TestSchemaDocs:
    def test_docs(self):
        assert "schema" in schema.DOCUMENTATION

class TestSchemaCreate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        schema.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE" in r["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create_transient(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE, transient=True); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        schema.run_module()
        assert "TRANSIENT SCHEMA" in m.exit_json.call_args[1]["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_check_mode(self, mc, cc):
        m = MagicMock(); m.check_mode = True; m.params = dict(BASE); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        schema.run_module()
        c.execute_ddl.assert_not_called()

class TestSchemaDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE, state="absent"); mc.return_value = m
        c = MagicMock(); c.query.return_value = [{"name": "RAW"}]; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        schema.run_module()
        assert "DROP SCHEMA" in m.exit_json.call_args[1]["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop_absent(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE, state="absent"); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; cc.return_value = c
        schema.run_module()
        assert m.exit_json.call_args[1]["changed"] is False
