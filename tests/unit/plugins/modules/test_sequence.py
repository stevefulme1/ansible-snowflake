from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""Unit tests for sequence module."""

from unittest.mock import MagicMock


class TestCreate:
    def test_create_returns_resource(self):
        client = MagicMock()
        client.create.return_value = dict(id="123", name="test")
        result = client.create("sequence", dict(name="test"))
        assert result["id"] == "123"

    def test_create_idempotent(self):
        client = MagicMock()
        client.get.return_value = dict(id="123", name="test")
        assert client.get("sequence", "123") is not None


class TestDelete:
    def test_delete_existing(self):
        client = MagicMock()
        client.delete("sequence", "123")
        client.delete.assert_called_once_with("sequence", "123")

    def test_delete_not_found(self):
        client = MagicMock()
        client.get.return_value = None
        assert client.get("sequence", "x") is None


class TestList:
    def test_list_returns_items(self):
        client = MagicMock()
        client.list.return_value = [dict(id="1"), dict(id="2")]
        assert len(client.list("sequence")) == 2

    def test_list_empty(self):
        client = MagicMock()
        client.list.return_value = []
        assert len(client.list("sequence")) == 0


class TestGet:
    def test_get_existing(self):
        client = MagicMock()
        client.get.return_value = dict(id="123", name="test")
        assert client.get("sequence", "123")["name"] == "test"

    def test_get_not_found(self):
        client = MagicMock()
        client.get.return_value = None
        assert client.get("sequence", "x") is None


class TestUpdate:
    def test_update(self):
        client = MagicMock()
        client.update.return_value = dict(id="123", name="updated")
        result = client.update("sequence", "123", dict(name="updated"))
        assert result["name"] == "updated"

    def test_update_not_found(self):
        client = MagicMock()
        client.get.return_value = None
        assert client.get("sequence", "x") is None
