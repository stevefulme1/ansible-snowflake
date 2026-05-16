#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: warehouse
short_description: Manage Snowflake warehouses
description:
  - Create, alter, or drop a Snowflake virtual warehouse.
  - Uses the Snowflake SQL REST API to execute DDL statements.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the warehouse.
    type: str
    required: true
  state:
    description: Desired state of the warehouse.
    type: str
    choices: [present, absent]
    default: present
  size:
    description: Size of the warehouse.
    type: str
    choices: [XSMALL, SMALL, MEDIUM, LARGE, XLARGE, XXLARGE, XXXLARGE, X4LARGE, X5LARGE, X6LARGE]
    default: XSMALL
  auto_suspend:
    description: Seconds of inactivity before auto-suspend (0 disables).
    type: int
    default: 600
  auto_resume:
    description: Whether the warehouse auto-resumes on query.
    type: bool
    default: true
  min_cluster_count:
    description: Minimum number of clusters (multi-cluster warehouses).
    type: int
    default: 1
  max_cluster_count:
    description: Maximum number of clusters (multi-cluster warehouses).
    type: int
    default: 1
  scaling_policy:
    description: Scaling policy for multi-cluster warehouses.
    type: str
    choices: [STANDARD, ECONOMY]
    default: STANDARD
  comment:
    description: Comment for the warehouse.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create a small warehouse
  stevefulme1.snowflake.warehouse:
    name: ANALYTICS_WH
    size: SMALL
    auto_suspend: 300
    auto_resume: true
    account: myaccount
    user: myuser
    private_key: "{{ lookup('file', '~/.ssh/snowflake_key.pem') }}"

- name: Remove a warehouse
  stevefulme1.snowflake.warehouse:
    name: OLD_WH
    state: absent
    account: myaccount
    user: myuser
    password: "{{ snowflake_password }}"
"""

RETURN = r"""
warehouse:
  description: Name of the warehouse managed.
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


def warehouse_exists(client, name):
    rows = client.query("SHOW WAREHOUSES LIKE '{0}'".format(name))
    return len(rows) > 0


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        size=dict(
            type="str",
            default="XSMALL",
            choices=[
                "XSMALL",
                "SMALL",
                "MEDIUM",
                "LARGE",
                "XLARGE",
                "XXLARGE",
                "XXXLARGE",
                "X4LARGE",
                "X5LARGE",
                "X6LARGE",
            ],
        ),
        auto_suspend=dict(type="int", default=600),
        auto_resume=dict(type="bool", default=True),
        min_cluster_count=dict(type="int", default=1),
        max_cluster_count=dict(type="int", default=1),
        scaling_policy=dict(
            type="str", default="STANDARD", choices=["STANDARD", "ECONOMY"]
        ),
        comment=dict(type="str"),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    name = module.params["name"].upper()
    state = module.params["state"]
    changed = False
    sql = ""

    try:
        client = SnowflakeClient(module)
        exists = warehouse_exists(client, name)

        if state == "absent":
            if exists:
                sql = "DROP WAREHOUSE IF EXISTS {0}".format(
                    client.quote_identifier(name)
                )
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
        else:
            if not exists:
                parts = [
                    "CREATE WAREHOUSE IF NOT EXISTS {0}".format(
                        client.quote_identifier(name)
                    )
                ]
                parts.append("WAREHOUSE_SIZE = '{0}'".format(module.params["size"]))
                parts.append("AUTO_SUSPEND = {0}".format(module.params["auto_suspend"]))
                parts.append(
                    "AUTO_RESUME = {0}".format(
                        str(module.params["auto_resume"]).upper()
                    )
                )
                parts.append(
                    "MIN_CLUSTER_COUNT = {0}".format(module.params["min_cluster_count"])
                )
                parts.append(
                    "MAX_CLUSTER_COUNT = {0}".format(module.params["max_cluster_count"])
                )
                parts.append(
                    "SCALING_POLICY = '{0}'".format(module.params["scaling_policy"])
                )
                if module.params.get("comment"):
                    parts.append("COMMENT = '{0}'".format(module.params["comment"]))
                sql = " ".join(parts)
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
            else:
                # ALTER existing warehouse
                alterations = []
                alterations.append(
                    "WAREHOUSE_SIZE = '{0}'".format(module.params["size"])
                )
                alterations.append(
                    "AUTO_SUSPEND = {0}".format(module.params["auto_suspend"])
                )
                alterations.append(
                    "AUTO_RESUME = {0}".format(
                        str(module.params["auto_resume"]).upper()
                    )
                )
                alterations.append(
                    "MIN_CLUSTER_COUNT = {0}".format(module.params["min_cluster_count"])
                )
                alterations.append(
                    "MAX_CLUSTER_COUNT = {0}".format(module.params["max_cluster_count"])
                )
                alterations.append(
                    "SCALING_POLICY = '{0}'".format(module.params["scaling_policy"])
                )
                if module.params.get("comment"):
                    alterations.append(
                        "COMMENT = '{0}'".format(module.params["comment"])
                    )
                sql = "ALTER WAREHOUSE {0} SET {1}".format(
                    client.quote_identifier(name), " ".join(alterations)
                )
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)

    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed, warehouse=name, sql=sql)


def main():
    run_module()


if __name__ == "__main__":
    main()
