# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Shared pytest fixtures for Snowflake module tests."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import pytest
from unittest.mock import MagicMock, patch

MODULE_UTILS_PATH = (
    "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
)


@pytest.fixture
def mock_module():
    """Return a mock AnsibleModule with sensible defaults."""
    module = MagicMock()
    module.check_mode = False
    module.params = {
        "account": "testaccount",
        "user": "testuser",
        "private_key": "-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----",
        "password": None,
        "role": None,
        "warehouse": None,
        "database": None,
        "schema": None,
        "validate_certs": True,
    }
    return module


@pytest.fixture
def mock_client():
    """Return a mocked SnowflakeClient."""
    client = MagicMock()
    client.query.return_value = []
    client.execute_ddl.return_value = {}
    client.quote_identifier.side_effect = lambda n: '"{0}"'.format(
        n.replace('"', '""')
    )
    return client


@pytest.fixture
def patch_client(mock_client):
    """Patch SnowflakeClient constructor to return mock_client."""
    with patch(
        MODULE_UTILS_PATH + ".SnowflakeClient", return_value=mock_client
    ) as p:
        yield mock_client
