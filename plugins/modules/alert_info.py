#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: alert_info
short_description: List Snowflake alerts
description:
  - Retrieve information about alerts using SHOW ALERTS.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Filter to a specific alert name pattern.
    type: str
  schema_name:
    description: Schema to list alerts from.
    type: str
  database_name:
    description: Database to list alerts from.
    type: str
  limit:
    description:
      - Maximum number of rows to return (maps to SQL LIMIT clause).
    type: int
    default: 100
  offset:
    description:
      - Number of rows to skip (maps to SQL OFFSET clause).
    type: int
    default: 0
  max_results:
    description:
      - Maximum total results to return.
    type: int
    default: 1000
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: List alerts
  stevefulme1.snowflake.alert_info:
    schema_name: PUBLIC
    database_name: ADMIN_DB
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
alerts:
  description: List of alert records.
  type: list
  returned: always
"""

from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
    escape_sql_string,
)
from ansible.module_utils.basic import AnsibleModule


def run_module():
    argument_spec = dict(
        name=dict(type="str"),
        schema_name=dict(type="str"),
        database_name=dict(type="str"),
    )
    argument_spec.update(snowflake_argument_spec)
    argument_spec["limit"] = dict(type="int", default=100)
    argument_spec["offset"] = dict(type="int", default=0)
    argument_spec["max_results"] = dict(type="int", default=1000)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    try:
        client = SnowflakeClient(module)
        sql = "SHOW ALERTS"
        if module.params.get(
                "database_name") and module.params.get("schema_name"):
            sql += " IN SCHEMA {0}.{1}".format(
                module.params["database_name"].upper(),
                module.params["schema_name"].upper(),
            )
        elif module.params.get("database_name"):
            sql += " IN DATABASE {0}".format(
                module.params["database_name"].upper())
        if module.params.get("name"):
            sql += " LIKE '{0}'".format(
                escape_sql_string(
                    module.params["name"]))
        rows = client.query(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    # Apply pagination
    _limit = module.params.get("limit") or 100
    _offset = module.params.get("offset") or 0
    if isinstance(rows, list):
        rows = rows[_offset:_offset + _limit]
    module.exit_json(changed=False, alerts=rows)


def main():
    run_module()


if __name__ == "__main__":
    main()
