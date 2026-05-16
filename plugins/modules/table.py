#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: table
short_description: Manage Snowflake tables
description:
  - Create, alter, or drop a Snowflake table.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the table.
    type: str
    required: true
  schema_name:
    description: Schema where the table resides.
    type: str
    required: true
  database_name:
    description: Database where the table resides.
    type: str
    required: true
  columns:
    description: List of column definitions (name, type, nullable, default).
    type: list
    elements: dict
  transient:
    description: Create as a transient table.
    type: bool
    default: false
  data_retention_time_in_days:
    description: Time Travel retention period in days.
    type: int
  comment:
    description: Comment for the table.
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
- name: Create a table
  stevefulme1.snowflake.table:
    name: EVENTS
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    columns:
      - name: ID
        type: NUMBER
      - name: CREATED_AT
        type: TIMESTAMP_NTZ
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
table:
  description: Name of the table managed.
  type: str
  returned: always
sql:
  description: The SQL statement executed.
  type: str
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
)


def table_exists(client, db, schema, name):
    fqn = "{0}.{1}".format(db, schema)
    rows = client.query("SHOW TABLES LIKE '{0}' IN SCHEMA {1}".format(name, fqn))
    return len(rows) > 0


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        columns=dict(type="list", elements="dict"),
        transient=dict(type="bool", default=False),
        data_retention_time_in_days=dict(type="int"),
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

    name = module.params["name"].upper()
    schema = module.params["schema_name"].upper()
    db = module.params["database_name"].upper()
    state = module.params["state"]
    fqn = "{0}.{1}.{2}".format(db, schema, name)
    changed = False
    sql = ""

    try:
        client = SnowflakeClient(module)
        exists = table_exists(client, db, schema, name)

        if state == "absent":
            if exists:
                sql = "DROP TABLE IF EXISTS {0}".format(fqn)
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
        else:
            if not exists:
                kind = "TRANSIENT TABLE" if module.params["transient"] else "TABLE"
                cols = module.params.get("columns") or []
                col_defs = ", ".join(
                    "{0} {1}".format(c["name"].upper(), c["type"].upper()) for c in cols
                )
                parts = ["CREATE {0} {1} ({2})".format(kind, fqn, col_defs)]
                if module.params.get("data_retention_time_in_days") is not None:
                    parts.append(
                        "DATA_RETENTION_TIME_IN_DAYS = {0}".format(
                            module.params["data_retention_time_in_days"]
                        )
                    )
                if module.params.get("comment"):
                    parts.append("COMMENT = '{0}'".format(module.params["comment"]))
                sql = " ".join(parts)
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
            else:
                alterations = []
                if module.params.get("data_retention_time_in_days") is not None:
                    alterations.append(
                        "DATA_RETENTION_TIME_IN_DAYS = {0}".format(
                            module.params["data_retention_time_in_days"]
                        )
                    )
                if module.params.get("comment"):
                    alterations.append(
                        "COMMENT = '{0}'".format(module.params["comment"])
                    )
                if alterations:
                    sql = "ALTER TABLE {0} SET {1}".format(fqn, " ".join(alterations))
                    changed = True
                    if not module.check_mode:
                        client.execute_ddl(sql)

    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed, table=name, sql=sql)


def main():
    run_module()


if __name__ == "__main__":
    main()
