# -*- coding: utf-8 -*-
"""Unit tests for the tag module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import tag

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.tag"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "COST_CENTER", "state": "present",
        "allowed_values": ["ENGINEERING", "MARKETING"], "comment": None,
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None, "validate_certs": True}


class TestTagDocs:
    def test_docs(self):
        assert "tag" in tag.DOCUMENTATION


class TestTagCreate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        tag.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE OR REPLACE TAG" in r["sql"]
        assert "ALLOWED_VALUES" in r["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_check_mode(self, mc, cc):
        m = MagicMock()
        m.check_mode = True
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        tag.run_module()
        c.execute_ddl.assert_not_called()


class TestTagDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, state="absent")
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        tag.run_module()
        assert "DROP TAG" in m.exit_json.call_args[1]["sql"]
