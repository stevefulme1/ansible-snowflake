#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: task
short_description: Manage Snowflake tasks
description:
  - Create, alter, or drop a Snowflake task for scheduled SQL execution.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the task.
    type: str
    required: true
  schema_name:
    description: Schema for the task.
    type: str
    required: true
  database_name:
    description: Database for the task.
    type: str
    required: true
  warehouse_name:
    description: Warehouse to execute the task.
    type: str
  schedule:
    description: Schedule (e.g. "1 MINUTE", "USING CRON 0 9 * * * UTC").
    type: str
  sql_statement:
    description: SQL statement to execute.
    type: str
  after:
    description: Predecessor task name (for DAG chaining).
    type: str
  when_condition:
    description: WHEN condition for the task.
    type: str
  comment:
    description: Comment for the task.
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
- name: Create a scheduled task
  stevefulme1.snowflake.task:
    name: HOURLY_LOAD
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    warehouse_name: COMPUTE_WH
    schedule: "60 MINUTE"
    sql_statement: "INSERT INTO agg SELECT * FROM raw"
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


def task_exists(client, db, schema, name):
    fqn = "{0}.{1}".format(db, schema)
    rows = client.query(
        "SHOW TASKS LIKE '{0}' IN SCHEMA {1}".format(
            name, fqn))
    return len(rows) > 0


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        warehouse_name=dict(type="str"),
        schedule=dict(type="str"),
        sql_statement=dict(type="str"),
        after=dict(type="str"),
        when_condition=dict(type="str"),
        comment=dict(type="str"),
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

    name = module.params["name"].upper()
    schema = module.params["schema_name"].upper()
    db = module.params["database_name"].upper()
    state = module.params["state"]
    fqn = "{0}.{1}.{2}".format(db, schema, name)
    changed = False
    sql = ""

    try:
        client = SnowflakeClient(module)
        exists = task_exists(client, db, schema, name)

        if state == "absent":
            if exists:
                sql = "DROP TASK IF EXISTS {0}".format(fqn)
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
        else:
            if not exists:
                stmt = module.params.get("sql_statement")
                if not stmt:
                    module.fail_json(msg="sql_statement required for new task")
                parts = ["CREATE TASK {0}".format(fqn)]
                if module.params.get("warehouse_name"):
                    parts.append(
                        "WAREHOUSE = {0}".format(
                            module.params["warehouse_name"])
                    )
                if module.params.get("schedule"):
                    parts.append(
                        "SCHEDULE = '{0}'".format(
                            escape_sql_string(
                                module.params["schedule"])))
                if module.params.get("after"):
                    parts.append(
                        "AFTER {0}.{1}.{2}".format(
                            db, schema, module.params["after"].upper()
                        )
                    )
                if module.params.get("comment"):
                    parts.append(
                        "COMMENT = '{0}'".format(
                            escape_sql_string(
                                module.params["comment"])))
                if module.params.get("when_condition"):
                    parts.append(
                        "WHEN {0}".format(
                            module.params["when_condition"]))
                parts.append("AS {0}".format(stmt))
                sql = " ".join(parts)
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)

    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed, task=name, sql=sql)


def main():
    run_module()


if __name__ == "__main__":
    main()
