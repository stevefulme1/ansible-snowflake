#!/usr/bin/python
# -*- coding: utf-8 -*-
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
module: resource_monitor_assignment
short_description: Assign a resource monitor to a warehouse
description:
  - Set or unset a resource monitor on a warehouse.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  warehouse_name:
    description: Name of the warehouse.
    type: str
    required: true
  monitor_name:
    description: Name of the resource monitor.
    type: str
    required: true
  state:
    description: Whether to set or unset.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Assign resource monitor to warehouse
  stevefulme1.snowflake.resource_monitor_assignment:
    warehouse_name: ANALYTICS_WH
    monitor_name: MONTHLY_MONITOR
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
        warehouse_name=dict(type="str", required=True),
        monitor_name=dict(type="str", required=True),
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

    wh = module.params["warehouse_name"].upper()
    monitor = module.params["monitor_name"].upper()
    state = module.params["state"]

    if state == "present":
        sql = "ALTER WAREHOUSE {0} SET RESOURCE_MONITOR = {1}".format(
            SnowflakeClient.quote_identifier(wh),
            SnowflakeClient.quote_identifier(monitor),
        )
    else:
        sql = "ALTER WAREHOUSE {0} UNSET RESOURCE_MONITOR".format(
            SnowflakeClient.quote_identifier(wh)
        )

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
