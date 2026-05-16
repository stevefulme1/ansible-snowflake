# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the warehouse module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.stevefulme1.snowflake.plugins.modules import warehouse


class TestWarehouseDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert hasattr(warehouse, "DOCUMENTATION")
        assert len(warehouse.DOCUMENTATION) > 0

    def test_documentation_has_module_name(self):
        assert "warehouse" in warehouse.DOCUMENTATION

    def test_documentation_has_short_description(self):
        assert "short_description" in warehouse.DOCUMENTATION

    def test_documentation_has_options(self):
        assert "options" in warehouse.DOCUMENTATION

    def test_examples_exist(self):
        assert hasattr(warehouse, "EXAMPLES")
        assert len(warehouse.EXAMPLES) > 0

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.snowflake" in warehouse.EXAMPLES

    def test_return_exists(self):
        assert hasattr(warehouse, "RETURN")
        assert len(warehouse.RETURN) > 0
