#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: table_constraint
short_description: Manage constraints on a Snowflake table
description:
  - Add or drop constraints (PRIMARY KEY, UNIQUE, FOREIGN KEY) on a table.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  table_name:
    description: Name of the table.
    type: str
    required: true
  schema_name:
    description: Schema of the table.
    type: str
    required: true
  database_name:
    description: Database of the table.
    type: str
    required: true
  constraint_name:
    description: Name of the constraint.
    type: str
    required: true
  constraint_type:
    description: Type of constraint.
    type: str
    choices: [primary_key, unique, foreign_key]
  columns:
    description: Columns for the constraint.
    type: list
    elements: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Add a primary key
  stevefulme1.snowflake.table_constraint:
    table_name: EVENTS
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    constraint_name: pk_events
    constraint_type: primary_key
    columns: [ID]
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
)
from ansible.module_utils.basic import AnsibleModule


CONSTRAINT_MAP = {
    "primary_key": "PRIMARY KEY",
    "unique": "UNIQUE",
    "foreign_key": "FOREIGN KEY",
}


def run_module():
    argument_spec = dict(
        table_name=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        constraint_name=dict(type="str", required=True),
        constraint_type=dict(
            type="str", choices=["primary_key", "unique", "foreign_key"]
        ),
        columns=dict(type="list", elements="str"),
        state=dict(
            type="str",
            default="present",
            choices=[
                "present",
                "absent"]),
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
        module.params["table_name"].upper(),
    )
    cname = module.params["constraint_name"].upper()
    state = module.params["state"]

    if state == "present":
        ctype = module.params.get("constraint_type")
        cols = module.params.get("columns")
        if not ctype or not cols:
            module.fail_json(
                msg="constraint_type and columns required when state=present"
            )
        col_list = ", ".join(c.upper() for c in cols)
        sql = "ALTER TABLE {0} ADD CONSTRAINT {1} {2} ({3})".format(
            fqn, cname, CONSTRAINT_MAP[ctype], col_list
        )
    else:
        sql = "ALTER TABLE {0} DROP CONSTRAINT {1}".format(fqn, cname)

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
