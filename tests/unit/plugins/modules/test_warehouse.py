# -*- coding: utf-8 -*-
"""Unit tests for the warehouse module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
from unittest.mock import patch, MagicMock

from ansible_collections.stevefulme1.snowflake.plugins.modules import warehouse

MODULE_PATH = "ansible_collections.stevefulme1.snowflake.plugins.modules.warehouse"
CLIENT_PATH = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"

BASE_PARAMS = {
    "name": "ANALYTICS_WH", "state": "present", "size": "SMALL",
    "auto_suspend": 300, "auto_resume": True,
    "min_cluster_count": 1, "max_cluster_count": 1,
    "scaling_policy": "STANDARD", "comment": None,
    "account": "t", "user": "a", "private_key": "k", "password": None,
    "role": None, "warehouse": None, "database": None, "schema": None,
    "validate_certs": True,
}


class TestWarehouseDocumentation:
    def test_documentation_exists(self):
        assert "warehouse" in warehouse.DOCUMENTATION

    def test_return_docs(self):
        assert "warehouse" in warehouse.RETURN
        assert "sql" in warehouse.RETURN


class TestWarehouseCreate:
    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_create_warehouse(self, mock_mod_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = False
        mock_mod.params = dict(BASE_PARAMS)
        mock_mod_cls.return_value = mock_mod
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_client.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        mock_client_cls.return_value = mock_client

        warehouse.run_module()

        args = mock_mod.exit_json.call_args[1]
        assert args["changed"] is True
        assert "CREATE WAREHOUSE" in args["sql"]
        assert args["warehouse"] == "ANALYTICS_WH"

    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_create_check_mode(self, mock_mod_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = True
        mock_mod.params = dict(BASE_PARAMS)
        mock_mod_cls.return_value = mock_mod
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_client.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        mock_client_cls.return_value = mock_client

        warehouse.run_module()

        assert mock_mod.exit_json.call_args[1]["changed"] is True
        mock_client.execute_ddl.assert_not_called()


class TestWarehouseUpdate:
    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_alter_existing(self, mock_mod_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = False
        mock_mod.params = dict(BASE_PARAMS)
        mock_mod_cls.return_value = mock_mod
        mock_client = MagicMock()
        mock_client.query.return_value = [{"name": "ANALYTICS_WH"}]
        mock_client.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        mock_client_cls.return_value = mock_client

        warehouse.run_module()

        args = mock_mod.exit_json.call_args[1]
        assert args["changed"] is True
        assert "ALTER WAREHOUSE" in args["sql"]


class TestWarehouseDelete:
    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_drop_existing(self, mock_mod_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = False
        params = dict(BASE_PARAMS, state="absent")
        mock_mod.params = params
        mock_mod_cls.return_value = mock_mod
        mock_client = MagicMock()
        mock_client.query.return_value = [{"name": "ANALYTICS_WH"}]
        mock_client.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        mock_client_cls.return_value = mock_client

        warehouse.run_module()

        args = mock_mod.exit_json.call_args[1]
        assert args["changed"] is True
        assert "DROP WAREHOUSE" in args["sql"]

    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_drop_absent_no_change(self, mock_mod_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = False
        mock_mod.params = dict(BASE_PARAMS, state="absent")
        mock_mod_cls.return_value = mock_mod
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_client_cls.return_value = mock_client

        warehouse.run_module()

        assert mock_mod.exit_json.call_args[1]["changed"] is False


class TestWarehouseIdempotency:
    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_absent_already_absent(self, mock_mod_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = False
        mock_mod.params = dict(BASE_PARAMS, state="absent")
        mock_mod_cls.return_value = mock_mod
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_client_cls.return_value = mock_client

        warehouse.run_module()

        assert mock_mod.exit_json.call_args[1]["changed"] is False
        mock_client.execute_ddl.assert_not_called()
