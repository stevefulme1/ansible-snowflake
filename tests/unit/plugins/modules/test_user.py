# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the user module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import patch, MagicMock, call

from ansible_collections.stevefulme1.snowflake.plugins.modules import user

MODULE_PATH = "ansible_collections.stevefulme1.snowflake.plugins.modules.user"
CLIENT_PATH = (
    "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
)


class TestUserDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert hasattr(user, "DOCUMENTATION")
        assert len(user.DOCUMENTATION) > 0

    def test_documentation_has_module_name(self):
        assert "user" in user.DOCUMENTATION

    def test_examples_exist(self):
        assert hasattr(user, "EXAMPLES")
        assert len(user.EXAMPLES) > 0

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.snowflake" in user.EXAMPLES

    def test_return_docs_exist(self):
        assert hasattr(user, "RETURN")
        assert "user" in user.RETURN
        assert "sql" in user.RETURN


class TestUserCreate:
    """Test user creation paths."""

    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_create_user(self, mock_module_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = False
        mock_mod.params = {
            "name": "jdoe",
            "state": "present",
            "login_name": None,
            "display_name": None,
            "email": "jdoe@example.com",
            "first_name": None,
            "last_name": None,
            "default_role": "ANALYST",
            "default_warehouse": None,
            "default_namespace": None,
            "must_change_password": False,
            "disabled": False,
            "user_password": None,
            "comment": None,
            "account": "test",
            "user": "admin",
            "private_key": "fake",
            "password": None,
            "role": None,
            "warehouse": None,
            "database": None,
            "schema": None,
            "validate_certs": True,
        }
        mock_module_cls.return_value = mock_mod

        mock_client = MagicMock()
        mock_client.query.return_value = []  # user does not exist
        mock_client.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        mock_client_cls.return_value = mock_client

        user.run_module()

        mock_mod.exit_json.assert_called_once()
        args = mock_mod.exit_json.call_args
        assert args[1]["changed"] is True
        assert args[1]["user"] == "JDOE"
        assert "CREATE USER" in args[1]["sql"]
        mock_client.execute_ddl.assert_called_once()

    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_create_user_check_mode(self, mock_module_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = True
        mock_mod.params = {
            "name": "jdoe", "state": "present",
            "login_name": None, "display_name": None, "email": None,
            "first_name": None, "last_name": None, "default_role": None,
            "default_warehouse": None, "default_namespace": None,
            "must_change_password": False, "disabled": False,
            "user_password": None, "comment": None,
            "account": "t", "user": "a", "private_key": "k", "password": None,
            "role": None, "warehouse": None, "database": None, "schema": None,
            "validate_certs": True,
        }
        mock_module_cls.return_value = mock_mod
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_client.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        mock_client_cls.return_value = mock_client

        user.run_module()

        mock_mod.exit_json.assert_called_once()
        assert mock_mod.exit_json.call_args[1]["changed"] is True
        mock_client.execute_ddl.assert_not_called()


class TestUserUpdate:
    """Test user update (alter) path."""

    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_alter_existing_user(self, mock_module_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = False
        mock_mod.params = {
            "name": "jdoe", "state": "present",
            "login_name": None, "display_name": None, "email": "new@example.com",
            "first_name": None, "last_name": None, "default_role": None,
            "default_warehouse": None, "default_namespace": None,
            "must_change_password": False, "disabled": False,
            "user_password": None, "comment": None,
            "account": "t", "user": "a", "private_key": "k", "password": None,
            "role": None, "warehouse": None, "database": None, "schema": None,
            "validate_certs": True,
        }
        mock_module_cls.return_value = mock_mod
        mock_client = MagicMock()
        mock_client.query.return_value = [{"name": "JDOE"}]  # exists
        mock_client.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        mock_client_cls.return_value = mock_client

        user.run_module()

        args = mock_mod.exit_json.call_args[1]
        assert args["changed"] is True
        assert "ALTER USER" in args["sql"]


class TestUserDelete:
    """Test user deletion path."""

    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_drop_existing_user(self, mock_module_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = False
        mock_mod.params = {
            "name": "jdoe", "state": "absent",
            "login_name": None, "display_name": None, "email": None,
            "first_name": None, "last_name": None, "default_role": None,
            "default_warehouse": None, "default_namespace": None,
            "must_change_password": False, "disabled": False,
            "user_password": None, "comment": None,
            "account": "t", "user": "a", "private_key": "k", "password": None,
            "role": None, "warehouse": None, "database": None, "schema": None,
            "validate_certs": True,
        }
        mock_module_cls.return_value = mock_mod
        mock_client = MagicMock()
        mock_client.query.return_value = [{"name": "JDOE"}]
        mock_client.quote_identifier.side_effect = lambda n: '"{0}"'.format(n)
        mock_client_cls.return_value = mock_client

        user.run_module()

        args = mock_mod.exit_json.call_args[1]
        assert args["changed"] is True
        assert "DROP USER" in args["sql"]

    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_drop_absent_user_no_change(
            self, mock_module_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = False
        mock_mod.params = {
            "name": "jdoe", "state": "absent",
            "login_name": None, "display_name": None, "email": None,
            "first_name": None, "last_name": None, "default_role": None,
            "default_warehouse": None, "default_namespace": None,
            "must_change_password": False, "disabled": False,
            "user_password": None, "comment": None,
            "account": "t", "user": "a", "private_key": "k", "password": None,
            "role": None, "warehouse": None, "database": None, "schema": None,
            "validate_certs": True,
        }
        mock_module_cls.return_value = mock_mod
        mock_client = MagicMock()
        mock_client.query.return_value = []  # does not exist
        mock_client_cls.return_value = mock_client

        user.run_module()

        args = mock_mod.exit_json.call_args[1]
        assert args["changed"] is False


class TestUserIdempotency:
    """Test idempotency behavior."""

    @patch(CLIENT_PATH + ".SnowflakeClient")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_absent_user_already_absent(
            self, mock_module_cls, mock_client_cls):
        mock_mod = MagicMock()
        mock_mod.check_mode = False
        mock_mod.params = {
            "name": "ghost", "state": "absent",
            "login_name": None, "display_name": None, "email": None,
            "first_name": None, "last_name": None, "default_role": None,
            "default_warehouse": None, "default_namespace": None,
            "must_change_password": False, "disabled": False,
            "user_password": None, "comment": None,
            "account": "t", "user": "a", "private_key": "k", "password": None,
            "role": None, "warehouse": None, "database": None, "schema": None,
            "validate_certs": True,
        }
        mock_module_cls.return_value = mock_mod
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_client_cls.return_value = mock_client

        user.run_module()

        assert mock_mod.exit_json.call_args[1]["changed"] is False
        mock_client.execute_ddl.assert_not_called()
