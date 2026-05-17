# -*- coding: utf-8 -*-
"""Unit tests for the role module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import role

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.role"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "ANALYST_ROLE", "state": "present", "comment": None,
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None,
        "validate_certs": True}

class TestRoleDocs:
    def test_docs(self):
        assert "role" in role.DOCUMENTATION

class TestRoleCreate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        role.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE ROLE" in r["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create_with_comment(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE, comment="test comment"); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        role.run_module()
        assert "COMMENT" in m.exit_json.call_args[1]["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_check_mode(self, mc, cc):
        m = MagicMock(); m.check_mode = True; m.params = dict(BASE); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        role.run_module()
        c.execute_ddl.assert_not_called()

class TestRoleDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE, state="absent"); mc.return_value = m
        c = MagicMock(); c.query.return_value = [{"name": "ANALYST_ROLE"}]; c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n); cc.return_value = c
        role.run_module()
        assert "DROP ROLE" in m.exit_json.call_args[1]["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop_absent(self, mc, cc):
        m = MagicMock(); m.check_mode = False; m.params = dict(BASE, state="absent"); mc.return_value = m
        c = MagicMock(); c.query.return_value = []; cc.return_value = c
        role.run_module()
        assert m.exit_json.call_args[1]["changed"] is False
