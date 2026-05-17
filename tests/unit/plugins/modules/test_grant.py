# -*- coding: utf-8 -*-
"""Unit tests for the role_grant module (grants)."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import role_grant

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.role_grant"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "ANALYST_ROLE", "to_user": "JDOE", "to_role": None, "state": "present",
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None, "validate_certs": True}


class TestGrantDocs:
    def test_docs(self):
        assert "role_grant" in role_grant.DOCUMENTATION


class TestGrantCreate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_grant_to_user(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        role_grant.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "GRANT ROLE" in r["sql"]
        assert "TO USER" in r["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_grant_to_role(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, to_user=None, to_role="SYSADMIN")
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        role_grant.run_module()
        assert "TO ROLE" in m.exit_json.call_args[1]["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_check_mode(self, mc, cc):
        m = MagicMock()
        m.check_mode = True
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        role_grant.run_module()
        c.execute_ddl.assert_not_called()


class TestGrantRevoke:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_revoke(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, state="absent")
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        role_grant.run_module()
        assert "REVOKE ROLE" in m.exit_json.call_args[1]["sql"]
        assert "FROM USER" in m.exit_json.call_args[1]["sql"]
