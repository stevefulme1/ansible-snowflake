#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: query_acceleration
short_description: Manage query acceleration on a Snowflake warehouse
description:
  - Enable or disable the query acceleration service on a warehouse.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  warehouse_name:
    description: Name of the warehouse.
    type: str
    required: true
  enabled:
    description: Whether query acceleration is enabled.
    type: bool
    default: true
  scale_factor:
    description: Max scale factor (0-100).
    type: int
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Enable query acceleration
  stevefulme1.snowflake.query_acceleration:
    warehouse_name: COMPUTE_WH
    enabled: true
    scale_factor: 8
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


def run_module():
    argument_spec = dict(
        warehouse_name=dict(type="str", required=True),
        enabled=dict(type="bool", default=True),
        scale_factor=dict(type="int"),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    wh = module.params["warehouse_name"].upper()
    enabled = str(module.params["enabled"]).upper()
    parts = [
        "ALTER WAREHOUSE {0} SET ENABLE_QUERY_ACCELERATION = {1}".format(
            wh, enabled)
    ]
    if module.params.get("scale_factor") is not None:
        parts.append(
            "QUERY_ACCELERATION_MAX_SCALE_FACTOR = {0}".format(
                module.params["scale_factor"]
            )
        )
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
