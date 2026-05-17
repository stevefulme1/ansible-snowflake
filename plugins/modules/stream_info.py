#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: stream_info
short_description: List Snowflake streams
description:
  - Retrieve information about streams using SHOW STREAMS.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Filter to a specific stream name pattern.
    type: str
  schema_name:
    description: Schema to list streams from.
    type: str
  database_name:
    description: Database to list streams from.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: List streams
  stevefulme1.snowflake.stream_info:
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
streams:
  description: List of stream records.
  type: list
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
    escape_sql_string,
)


def run_module():
    argument_spec = dict(
        name=dict(type="str"),
        schema_name=dict(type="str"),
        database_name=dict(type="str"),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    try:
        client = SnowflakeClient(module)
        sql = "SHOW STREAMS"
        if module.params.get("database_name") and module.params.get("schema_name"):
            sql += " IN SCHEMA {0}.{1}".format(
                module.params["database_name"].upper(),
                module.params["schema_name"].upper(),
            )
        elif module.params.get("database_name"):
            sql += " IN DATABASE {0}".format(module.params["database_name"].upper())
        if module.params.get("name"):
            sql += " LIKE '{0}'".format(escape_sql_string(module.params["name"]))
        rows = client.query(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=False, streams=rows)


def main():
    run_module()


if __name__ == "__main__":
    main()
