#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
)
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type
DOCUMENTATION = r"""
---
module: account_usage_info
short_description: Query Snowflake ACCOUNT_USAGE views
description:
  - Query views from the SNOWFLAKE.ACCOUNT_USAGE schema.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  view_name:
    description: Name of the ACCOUNT_USAGE view to query.
    type: str
    required: true
  columns:
    description: Columns to select (defaults to all).
    type: str
    default: "*"
  where_clause:
    description: Optional WHERE clause filter.
    type: str
  limit:
    description: Maximum number of rows to return.
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
- name: Query login history
  stevefulme1.snowflake.account_usage_info:
    view_name: LOGIN_HISTORY
    where_clause: "IS_SUCCESS = 'NO'"
    limit: 50
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
rows:
  description: Query result rows.
  type: list
  returned: always
"""


def run_module():
    argument_spec = dict(
        view_name=dict(type="str", required=True),
        columns=dict(type="str", default="*"),
        where_clause=dict(type="str"),
        limit=dict(type="int", default=100),
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

    view = module.params["view_name"].upper()
    cols = module.params["columns"]
    sql = "SELECT {0} FROM SNOWFLAKE.ACCOUNT_USAGE.{1}".format(cols, view)
    if module.params.get("where_clause"):
        sql += " WHERE {0}".format(module.params["where_clause"])
    sql += " LIMIT {0}".format(module.params["limit"])

    try:
        client = SnowflakeClient(module)
        rows = client.query(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    # Apply pagination
    _limit = module.params.get("limit") or 100
    _offset = module.params.get("offset") or 0
    if isinstance(rows, list):
        rows = rows[_offset:_offset + _limit]
    module.exit_json(changed=False, rows=rows)


def main():
    run_module()


if __name__ == "__main__":
    main()
