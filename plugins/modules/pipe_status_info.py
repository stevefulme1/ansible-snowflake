#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import json as _json
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
    escape_sql_string,
)
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type
DOCUMENTATION = r"""
---
module: pipe_status_info
short_description: Get Snowflake pipe status
description:
  - Retrieve the status of a Snowpipe via SYSTEM$PIPE_STATUS.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Fully qualified pipe name.
    type: str
    required: true
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
- name: Get pipe status
  stevefulme1.snowflake.pipe_status_info:
    name: RAW_DB.PUBLIC.RAW_PIPE
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
pipe_status:
  description: JSON status of the pipe.
  type: dict
  returned: always
"""


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
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
        sql = "SELECT SYSTEM$PIPE_STATUS('{0}') AS STATUS".format(
            escape_sql_string(module.params["name"].upper())
        )
        rows = client.query(sql)
        status = _json.loads(rows[0]["STATUS"]) if rows else {}
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    # Apply pagination
    _limit = module.params.get("limit") or 100
    _offset = module.params.get("offset") or 0
    if isinstance(rows, list):
        rows = rows[_offset:_offset + _limit]
    module.exit_json(changed=False, pipe_status=status)


def main():
    run_module()


if __name__ == "__main__":
    main()
