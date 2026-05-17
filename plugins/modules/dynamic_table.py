#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: dynamic_table
short_description: Manage Snowflake dynamic tables
description:
  - Create or drop a dynamic table with declarative data pipelines.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the dynamic table.
    type: str
    required: true
  schema_name:
    description: Schema for the table.
    type: str
    required: true
  database_name:
    description: Database for the table.
    type: str
    required: true
  target_lag:
    description: Target lag for refresh (e.g. 1 minute, downstream).
    type: str
  warehouse_name:
    description: Warehouse to run refreshes.
    type: str
  query:
    description: SELECT statement defining the table.
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
- name: Create dynamic table
  stevefulme1.snowflake.dynamic_table:
    name: DT_HOURLY_AGG
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    target_lag: "1 minute"
    warehouse_name: COMPUTE_WH
    query: "SELECT region, COUNT(*) cnt FROM events GROUP BY region"
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
        target_lag=dict(type="str"),
        warehouse_name=dict(type="str"),
        query=dict(type="str"),
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
        sql = "DROP DYNAMIC TABLE IF EXISTS {0}".format(fqn)
    else:
        q = module.params.get("query")
        if not q:
            module.fail_json(msg="query is required when state=present")
        parts = ["CREATE OR REPLACE DYNAMIC TABLE {0}".format(fqn)]
        if module.params.get("target_lag"):
            parts.append("TARGET_LAG = '{0}'".format(escape_sql_string(module.params["target_lag"])))
        if module.params.get("warehouse_name"):
            parts.append("WAREHOUSE = {0}".format(module.params["warehouse_name"]))
        parts.append("AS {0}".format(q))
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
