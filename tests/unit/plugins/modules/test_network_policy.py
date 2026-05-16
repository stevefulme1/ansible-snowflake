# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the network_policy module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.stevefulme1.snowflake.plugins.modules import network_policy


class TestNetworkPolicyDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert hasattr(network_policy, "DOCUMENTATION")
        assert len(network_policy.DOCUMENTATION) > 0

    def test_documentation_has_module_name(self):
        assert "network_policy" in network_policy.DOCUMENTATION

    def test_examples_exist(self):
        assert hasattr(network_policy, "EXAMPLES")
        assert len(network_policy.EXAMPLES) > 0

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.snowflake" in network_policy.EXAMPLES
