# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the user module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.stevefulme1.snowflake.plugins.modules import user


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
