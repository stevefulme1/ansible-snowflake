#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: warehouse_cluster
short_description: Manage Snowflake warehouse clustering
description:
  - Set min/max cluster count on a multi-cluster warehouse.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  warehouse_name:
    description: Name of the warehouse.
    type: str
    required: true
  min_cluster_count:
    description: Minimum number of clusters.
    type: int
  max_cluster_count:
    description: Maximum number of clusters.
    type: int
  scaling_policy:
    description: Scaling policy (STANDARD, ECONOMY).
    type: str
    choices: [STANDARD, ECONOMY]
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Configure multi-cluster warehouse
  stevefulme1.snowflake.warehouse_cluster:
    warehouse_name: COMPUTE_WH
    min_cluster_count: 1
    max_cluster_count: 3
    scaling_policy: STANDARD
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
        warehouse_name=dict(type="str", required=True),
        min_cluster_count=dict(type="int"),
        max_cluster_count=dict(type="int"),
        scaling_policy=dict(type="str", choices=["STANDARD", "ECONOMY"]),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    wh = module.params["warehouse_name"].upper()
    parts = ["ALTER WAREHOUSE {0} SET".format(wh)]
    settings = []
    if module.params.get("min_cluster_count") is not None:
        settings.append(
            "MIN_CLUSTER_COUNT = {0}".format(module.params["min_cluster_count"])
        )
    if module.params.get("max_cluster_count") is not None:
        settings.append(
            "MAX_CLUSTER_COUNT = {0}".format(module.params["max_cluster_count"])
        )
    if module.params.get("scaling_policy"):
        settings.append(
            "SCALING_POLICY = '{0}'".format(module.params["scaling_policy"])
        )
    if not settings:
        module.fail_json(msg="At least one cluster setting is required")
    parts.append(" ".join(settings))
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
