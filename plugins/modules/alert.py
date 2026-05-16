#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: alert
short_description: Manage Snowflake alerts
description:
  - Create, alter, or drop a Snowflake alert.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the alert.
    type: str
    required: true
  schema_name:
    description: Schema for the alert.
    type: str
    required: true
  database_name:
    description: Database for the alert.
    type: str
    required: true
  warehouse_name:
    description: Warehouse for alert evaluation.
    type: str
  schedule:
    description: Schedule (e.g. "1 MINUTE").
    type: str
  condition:
    description: SQL condition that triggers the alert.
    type: str
  action:
    description: SQL action to run when triggered.
    type: str
  comment:
    description: Comment for the alert.
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
- name: Create an alert
  stevefulme1.snowflake.alert:
    name: HIGH_CREDIT_ALERT
    schema_name: PUBLIC
    database_name: ADMIN_DB
    warehouse_name: COMPUTE_WH
    schedule: "60 MINUTE"
    condition: "SELECT COUNT(*) FROM credit_usage WHERE credits > 100"
    action: "CALL SYSTEM$SEND_EMAIL('ops@co.com', 'High credit', 'Check usage')"
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
)


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        warehouse_name=dict(type="str"),
        schedule=dict(type="str"),
        condition=dict(type="str"),
        action=dict(type="str"),
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
        sql = "DROP ALERT IF EXISTS {0}".format(fqn)
    else:
        cond = module.params.get("condition")
        act = module.params.get("action")
        if not cond or not act:
            module.fail_json(msg="condition and action required when state=present")
        parts = ["CREATE OR REPLACE ALERT {0}".format(fqn)]
        if module.params.get("warehouse_name"):
            parts.append("WAREHOUSE = {0}".format(module.params["warehouse_name"]))
        if module.params.get("schedule"):
            parts.append("SCHEDULE = '{0}'".format(module.params["schedule"]))
        if module.params.get("comment"):
            parts.append("COMMENT = '{0}'".format(module.params["comment"]))
        parts.append("IF (EXISTS ({0}))".format(cond))
        parts.append("THEN {0}".format(act))
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
