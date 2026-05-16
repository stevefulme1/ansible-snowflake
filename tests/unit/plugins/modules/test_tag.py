# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the tag module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.stevefulme1.snowflake.plugins.modules import tag


class TestTagDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert hasattr(tag, "DOCUMENTATION")
        assert len(tag.DOCUMENTATION) > 0

    def test_documentation_has_module_name(self):
        assert "tag" in tag.DOCUMENTATION

    def test_examples_exist(self):
        assert hasattr(tag, "EXAMPLES")
        assert len(tag.EXAMPLES) > 0

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.snowflake" in tag.EXAMPLES
