# -*- coding: utf-8 -*-
"""Shared fixtures for Snowflake unit tests."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_module():
    """Return a mock AnsibleModule with check_mode disabled."""
    module = MagicMock()
    module.check_mode = False
    module.params = {
        "state": "present",
        "account": "myaccount",
        "user": "admin",
        "private_key": "test-key",
    }
    return module


@pytest.fixture
def mock_module_check_mode():
    """Return a mock AnsibleModule with check_mode enabled."""
    module = MagicMock()
    module.check_mode = True
    module.params = {
        "state": "present",
        "account": "myaccount",
        "user": "admin",
        "private_key": "test-key",
    }
    return module


@pytest.fixture
def mock_cursor():
    """Return a mock Snowflake cursor."""
    cursor = MagicMock()
    cursor.execute.return_value = cursor
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None
    cursor.description = [("name",), ("type",)]
    return cursor


@pytest.fixture
def mock_connection(mock_cursor):
    """Return a mock Snowflake connection."""
    conn = MagicMock()
    conn.cursor.return_value = mock_cursor
    return conn
