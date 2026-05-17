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
module: table_column
short_description: Manage columns on a Snowflake table
description:
  - Add, drop, or rename columns on an existing Snowflake table.
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
  column_name:
    description: Column name to manage.
    type: str
    required: true
  column_type:
    description: Data type for the column (required when adding).
    type: str
  new_name:
    description: New name when renaming a column.
    type: str
  action:
    description: Action to perform on the column.
    type: str
    choices: [add, drop, rename]
    required: true
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Add a column
  stevefulme1.snowflake.table_column:
    table_name: EVENTS
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    column_name: STATUS
    column_type: VARCHAR
    action: add
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


def run_module():
    argument_spec = dict(
        table_name=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        column_name=dict(type="str", required=True),
        column_type=dict(type="str"),
        new_name=dict(type="str"),
        action=dict(
            type="str",
            required=True,
            choices=[
                "add",
                "drop",
                "rename"]),
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
    col = module.params["column_name"].upper()
    action = module.params["action"]

    if action == "add":
        ctype = module.params.get("column_type")
        if not ctype:
            module.fail_json(msg="column_type is required when action=add")
        sql = "ALTER TABLE {0} ADD COLUMN {1} {2}".format(
            fqn, col, ctype.upper())
    elif action == "drop":
        sql = "ALTER TABLE {0} DROP COLUMN {1}".format(fqn, col)
    else:
        new = module.params.get("new_name")
        if not new:
            module.fail_json(msg="new_name is required when action=rename")
        sql = "ALTER TABLE {0} RENAME COLUMN {1} TO {2}".format(
            fqn, col, new.upper())

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
