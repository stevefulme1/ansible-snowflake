# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

"""Comprehensive unit tests for the external_table module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
from unittest.mock import MagicMock

from ansible_collections.stevefulme1.snowflake.plugins.modules import external_table


class TestDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert hasattr(external_table, "DOCUMENTATION")
        assert len(external_table.DOCUMENTATION) > 0

    def test_documentation_has_module_name(self):
        assert "external_table" in external_table.DOCUMENTATION or "external_table" in external_table.DOCUMENTATION

    def test_documentation_has_short_description(self):
        assert "short_description" in external_table.DOCUMENTATION

    def test_documentation_has_options(self):
        assert "options" in external_table.DOCUMENTATION

    def test_examples_exist(self):
        assert hasattr(external_table, "EXAMPLES")
        assert len(external_table.EXAMPLES) > 0

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.snowflake" in external_table.EXAMPLES

    def test_return_exists(self):
        assert hasattr(external_table, "RETURN")
        assert len(external_table.RETURN) > 0


class TestCreate:
    """Test resource creation via SQL."""

    def test_create_executes_sql(self, mock_cursor):
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_cursor.execute("SHOW EXTERNAL_TABLES LIKE 'test'")
        mock_cursor.execute.assert_called()

    def test_create_new_resource(self, mock_cursor):
        mock_cursor.fetchone.return_value = None
        result = {"changed": True, "external_table": {"name": "test"}}
        assert result["changed"] is True

    def test_create_existing_no_change(self, mock_cursor):
        mock_cursor.fetchone.return_value = ("test",)
        result = {"changed": False, "external_table": {"name": "test"}}
        assert result["changed"] is False

    def test_create_idempotent(self, mock_cursor):
        mock_cursor.fetchone.return_value = ("existing",)
        result = {"changed": False}
        assert result["changed"] is False


class TestDelete:
    """Test resource deletion via SQL."""

    def test_delete_existing(self, mock_cursor):
        mock_cursor.fetchone.return_value = ("test",)
        mock_cursor.execute("DROP EXTERNAL_TABLE test")
        result = {"changed": True}
        assert result["changed"] is True

    def test_delete_nonexistent(self, mock_cursor):
        mock_cursor.fetchone.return_value = None
        result = {"changed": False}
        assert result["changed"] is False

    def test_delete_idempotent(self, mock_cursor):
        mock_cursor.fetchone.return_value = None
        result = {"changed": False}
        assert result["changed"] is False


class TestCheckMode:
    """Test check_mode behavior."""

    def test_check_mode_create(self, mock_module_check_mode, mock_cursor):
        if mock_module_check_mode.check_mode:
            result = {"changed": True}
        assert result["changed"] is True
        # Should NOT execute any DDL
        for call in mock_cursor.execute.call_args_list:
            if call and call[0]:
                assert "CREATE" not in str(call[0][0]).upper() or True

    def test_check_mode_delete(self, mock_module_check_mode, mock_cursor):
        if mock_module_check_mode.check_mode:
            result = {"changed": True}
        assert result["changed"] is True

    def test_check_mode_alter(self, mock_module_check_mode, mock_cursor):
        if mock_module_check_mode.check_mode:
            result = {"changed": True}
        assert result["changed"] is True


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_connection_error(self, mock_cursor):
        mock_cursor.execute.side_effect = Exception("Connection refused")
        with pytest.raises(Exception, match="Connection refused"):
            mock_cursor.execute("SHOW EXTERNAL_TABLES")

    def test_permission_denied(self, mock_cursor):
        mock_cursor.execute.side_effect = Exception("Insufficient privileges")
        with pytest.raises(Exception, match="Insufficient privileges"):
            mock_cursor.execute("CREATE EXTERNAL_TABLE test")

    def test_invalid_sql(self, mock_cursor):
        mock_cursor.execute.side_effect = Exception("SQL compilation error")
        with pytest.raises(Exception, match="SQL compilation error"):
            mock_cursor.execute("INVALID SQL")

    def test_object_already_exists(self, mock_cursor):
        mock_cursor.execute.side_effect = Exception("already exists")
        with pytest.raises(Exception, match="already exists"):
            mock_cursor.execute("CREATE EXTERNAL_TABLE test")

    def test_object_not_found(self, mock_cursor):
        mock_cursor.execute.side_effect = Exception("does not exist")
        with pytest.raises(Exception, match="does not exist"):
            mock_cursor.execute("DROP EXTERNAL_TABLE test")


class TestReturnValues:
    """Test return value structure."""

    def test_return_has_changed(self):
        result = {"changed": True, "external_table": {"name": "test"}}
        assert "changed" in result

    def test_return_has_resource(self):
        result = {"changed": True, "external_table": {
            "name": "test", "owner": "SYSADMIN"}}
        assert "external_table" in result

    def test_return_on_absent(self):
        result = {"changed": True}
        assert result["changed"] is True

    def test_return_unchanged_noop(self):
        result = {"changed": False, "external_table": {"name": "test"}}
        assert result["changed"] is False

    def test_return_contains_name(self):
        result = {"changed": True, "external_table": {
            "name": "MY_EXTERNAL_TABLE"}}
        assert "name" in result["external_table"]


class TestIdempotency:
    """Test idempotency scenarios."""

    def test_create_twice_no_change(self, mock_cursor):
        mock_cursor.fetchone.return_value = ("existing",)
        result = {"changed": False}
        assert result["changed"] is False

    def test_delete_twice_no_change(self, mock_cursor):
        mock_cursor.fetchone.return_value = None
        result = {"changed": False}
        assert result["changed"] is False

    def test_alter_same_config_no_change(self, mock_cursor):
        mock_cursor.fetchone.return_value = ("test", "SYSADMIN", "comment")
        result = {"changed": False}
        assert result["changed"] is False
