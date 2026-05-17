# -*- coding: utf-8 -*-
"""Unit tests for the network_policy module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import network_policy

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.network_policy"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "OFFICE_POLICY", "state": "present",
        "allowed_ip_list": ["203.0.113.0/24", "198.51.100.0/24"],
        "blocked_ip_list": [], "comment": None,
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None, "validate_certs": True}


class TestNetworkPolicyDocs:
    def test_docs(self):
        assert "network_policy" in network_policy.DOCUMENTATION


class TestNetworkPolicyCreate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = []
        c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        cc.return_value = c
        network_policy.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE NETWORK POLICY" in r["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_check_mode(self, mc, cc):
        m = MagicMock()
        m.check_mode = True
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = []
        c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        cc.return_value = c
        network_policy.run_module()
        c.execute_ddl.assert_not_called()


class TestNetworkPolicyUpdate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_alter(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = [{"name": "OFFICE_POLICY"}]
        c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        cc.return_value = c
        network_policy.run_module()
        assert "ALTER NETWORK POLICY" in m.exit_json.call_args[1]["sql"]


class TestNetworkPolicyDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, state="absent")
        mc.return_value = m
        c = MagicMock()
        c.query.return_value = [{"name": "OFFICE_POLICY"}]
        c.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        cc.return_value = c
        network_policy.run_module()
        assert "DROP NETWORK POLICY" in m.exit_json.call_args[1]["sql"]

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
        network_policy.run_module()
        assert m.exit_json.call_args[1]["changed"] is False
