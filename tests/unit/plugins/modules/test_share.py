# -*- coding: utf-8 -*-
"""Unit tests for the share module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import share

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.share"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "ANALYTICS_SHARE", "accounts": ["ORG1.CONSUMER_ACCT"], "comment": None,
        "state": "present",
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None, "validate_certs": True}

class TestShareDocs:
    def test_docs(self):
        assert "share" in share.DOCUMENTATION

class TestShareCreate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE); mc.return_value = m
        c = MagicMock(); cc.return_value = c
        share.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE SHARE" in r["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create_with_accounts(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE); mc.return_value = m
        c = MagicMock(); cc.return_value = c
        share.run_module()
        assert c.execute_ddl.call_count == 2  # CREATE + ALTER SHARE ADD ACCOUNTS

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_check_mode(self, mc, cc):
        m = MagicMock(); m.check_mode = True; m.params = dict(BASE); mc.return_value = m
        c = MagicMock(); cc.return_value = c
        share.run_module()
        c.execute_ddl.assert_not_called()

class TestShareDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE, state="absent"); mc.return_value = m
        c = MagicMock(); cc.return_value = c
        share.run_module()
        assert "DROP SHARE" in m.exit_json.call_args[1]["sql"]
