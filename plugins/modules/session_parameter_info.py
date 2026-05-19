#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: session_parameter_info
short_description: List Snowflake session parameters
description:
  - Retrieve information about session parameters in Snowflake.
  - This module is read-only and does not modify any resources.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Filter to a specific session parameter name or pattern.
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
- name: List all session parameters
  stevefulme1.snowflake.session_parameter_info:
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"

- name: Get a specific session parameter
  stevefulme1.snowflake.session_parameter_info:
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
    name: my_session parameter
"""

RETURN = r"""
session_parameters:
  description: List of session parameter records.
  type: list
  returned: always
  elements: dict
"""

from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
    escape_sql_string,
)
from ansible.module_utils.basic import AnsibleModule


def run_module():
    argument_spec = dict(name=dict(type="str"))
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
        sql = "SHOW PARAMETERS IN SESSION"
        if module.params.get("name"):
            sql += " LIKE '{0}'".format(escape_sql_string(module.params["name"]))
        rows = client.query(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    _limit = module.params.get("limit") or 100
    _offset = module.params.get("offset") or 0
    if isinstance(rows, list):
        rows = rows[_offset : _offset + _limit]
    module.exit_json(changed=False, session_parameters=rows)


def main():
    run_module()


if __name__ == "__main__":
    main()
