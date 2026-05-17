#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: sequence
short_description: Manage Snowflake sequences
description:
  - Create or drop a Snowflake sequence.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the sequence.
    type: str
    required: true
  schema_name:
    description: Schema for the sequence.
    type: str
    required: true
  database_name:
    description: Database for the sequence.
    type: str
    required: true
  start:
    description: Starting value.
    type: int
    default: 1
  increment:
    description: Increment value.
    type: int
    default: 1
  comment:
    description: Comment for the sequence.
    type: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create a sequence
  stevefulme1.snowflake.sequence:
    name: SEQ_ORDER_ID
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    start: 1000
    increment: 1
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
sql:
  description: The SQL statement executed.
  type: str
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
        name=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        start=dict(type="int", default=1),
        increment=dict(type="int", default=1),
        comment=dict(type="str"),
        state=dict(type="str", default="present", choices=["present", "absent"]),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    fqn = "{0}.{1}.{2}".format(
        module.params["database_name"].upper(),
        module.params["schema_name"].upper(),
        module.params["name"].upper(),
    )
    state = module.params["state"]

    if state == "absent":
        sql = "DROP SEQUENCE IF EXISTS {0}".format(fqn)
    else:
        parts = [
            "CREATE SEQUENCE IF NOT EXISTS {0}".format(fqn),
            "START = {0}".format(module.params["start"]),
            "INCREMENT = {0}".format(module.params["increment"]),
        ]
        if module.params.get("comment"):
            parts.append("COMMENT = '{0}'".format(escape_sql_string(module.params["comment"])))
        sql = " ".join(parts)

    try:
        client = SnowflakeClient(module)
        if not module.check_mode:
            client.execute_ddl(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=True, sql=sql)


def main():
    run_module()


if __name__ == "__main__":
    main()
