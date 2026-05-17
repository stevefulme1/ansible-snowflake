# -*- coding: utf-8 -*-
"""Unit tests for the pipe module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import pipe

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.pipe"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "RAW_PIPE", "schema_name": "PUBLIC", "database_name": "RAW_DB",
        "copy_statement": "COPY INTO RAW_DB.PUBLIC.RAW_TABLE FROM @STAGE/",
        "auto_ingest": True, "comment": None, "state": "present",
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None, "validate_certs": True}


class TestPipeDocs:
    def test_docs(self):
        assert "pipe" in pipe.DOCUMENTATION


class TestPipeCreate:
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
        pipe.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE PIPE" in r["sql"]
        assert "AUTO_INGEST = TRUE" in r["sql"]

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
        pipe.run_module()
        c.execute_ddl.assert_not_called()

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_missing_copy_fails(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, copy_statement=None)
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = []
        cc.return_value = c
        pipe.run_module()
        m.fail_json.assert_called_once()


class TestPipeDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, state="absent")
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = [{"name": "RAW_PIPE"}]
        cc.return_value = c
        pipe.run_module()
        assert "DROP PIPE" in m.exit_json.call_args[1]["sql"]

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
        pipe.run_module()
        assert m.exit_json.call_args[1]["changed"] is False
