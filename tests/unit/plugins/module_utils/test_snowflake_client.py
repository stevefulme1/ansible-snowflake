# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for snowflake_client module_utils."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
)


class TestSnowflakeArgumentSpec:
    """Tests for the snowflake_argument_spec dict."""

    def test_has_account_key(self):
        assert "account" in snowflake_argument_spec

    def test_has_user_key(self):
        assert "user" in snowflake_argument_spec

    def test_has_role_key(self):
        assert "role" in snowflake_argument_spec

    def test_has_warehouse_key(self):
        assert "warehouse" in snowflake_argument_spec

    def test_password_is_no_log(self):
        assert snowflake_argument_spec["password"].get("no_log") is True

    def test_private_key_is_no_log(self):
        assert snowflake_argument_spec["private_key"].get("no_log") is True

    def test_account_is_required(self):
        assert snowflake_argument_spec["account"].get("required") is True

    def test_user_is_required(self):
        assert snowflake_argument_spec["user"].get("required") is True


class TestSnowflakeClient:
    """Tests for SnowflakeClient initialisation."""

    @patch.object(SnowflakeClient, "_authenticate", return_value="fake-token")
    def test_init_sets_account(self, _mock_auth):
        module = MagicMock()
        module.params = {
            "account": "myaccount",
            "user": "myuser",
            "private_key": "fake-key",
            "password": None,
            "role": "SYSADMIN",
            "warehouse": "COMPUTE_WH",
            "database": "MYDB",
            "schema": "PUBLIC",
            "validate_certs": True,
        }
        client = SnowflakeClient(module)
        assert client.account == "myaccount"
        assert client.user == "myuser"
        assert client.role == "SYSADMIN"

    @patch.object(SnowflakeClient, "_authenticate", return_value="fake-token")
    def test_init_builds_base_url(self, _mock_auth):
        module = MagicMock()
        module.params = {
            "account": "testacct",
            "user": "testuser",
            "private_key": "key",
            "password": None,
            "role": None,
            "warehouse": None,
            "database": None,
            "schema": None,
            "validate_certs": True,
        }
        client = SnowflakeClient(module)
        assert client.base_url == "https://testacct.snowflakecomputing.com"


class TestSnowflakeError:
    """Tests for the SnowflakeError exception."""

    def test_message(self):
        err = SnowflakeError("something went wrong")
        assert str(err) == "something went wrong"

    def test_code_attribute(self):
        err = SnowflakeError("fail", code="390001")
        assert err.code == "390001"

    def test_sql_state_attribute(self):
        err = SnowflakeError("fail", sql_state="22000")
        assert err.sql_state == "22000"

    def test_defaults_to_none(self):
        err = SnowflakeError("msg")
        assert err.code is None
        assert err.sql_state is None
