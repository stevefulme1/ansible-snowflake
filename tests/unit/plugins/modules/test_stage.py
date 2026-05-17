# -*- coding: utf-8 -*-
"""Unit tests for the stage module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from unittest.mock import patch, MagicMock
from ansible_collections.stevefulme1.snowflake.plugins.modules import stage

MP = "ansible_collections.stevefulme1.snowflake.plugins.modules.stage"
CP = "ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client"
BASE = {"name": "MYDB.PUBLIC.MY_STAGE", "state": "present", "stage_type": "internal",
        "url": None, "storage_integration": None, "file_format": None,
        "copy_options": None, "comment": None,
        "account": "t", "user": "a", "private_key": "k", "password": None,
        "role": None, "warehouse": None, "database": None, "schema": None, "validate_certs": True}


class TestStageDocs:
    def test_docs(self):
        assert "stage" in stage.DOCUMENTATION


class TestStageCreate:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create_internal(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        stage.run_module()
        r = m.exit_json.call_args[1]
        assert r["changed"] is True and "CREATE OR REPLACE STAGE" in r["sql"]

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_create_external(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, stage_type="external",
                        url="s3://bucket/path/", storage_integration="S3_INT")
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        stage.run_module()
        sql = m.exit_json.call_args[1]["sql"]
        assert "s3://bucket/path/" in sql and "STORAGE_INTEGRATION" in sql

    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_check_mode(self, mc, cc):
        m = MagicMock()
        m.check_mode = True
        m.params = dict(BASE)
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        stage.run_module()
        c.execute_ddl.assert_not_called()


class TestStageDelete:
    @patch(CP + ".SnowflakeClient")
    @patch(MP + ".AnsibleModule")
    def test_drop(self, mc, cc):
        m = MagicMock()
        m.check_mode = False
        m.params = dict(BASE, state="absent")
        mc.return_value = m
        c = MagicMock()
        cc.return_value = c
        stage.run_module()
        assert "DROP STAGE" in m.exit_json.call_args[1]["sql"]
