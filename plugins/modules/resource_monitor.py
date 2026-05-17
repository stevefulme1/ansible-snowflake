#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: resource_monitor
short_description: Manage Snowflake resource monitors
description:
  - Create, alter, or drop a resource monitor for credit tracking.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the resource monitor.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  credit_quota:
    description: Credit quota for the monitor.
    type: int
  frequency:
    description: Reset frequency.
    type: str
    choices: [MONTHLY, DAILY, WEEKLY, YEARLY, NEVER]
    default: MONTHLY
  start_timestamp:
    description: Start timestamp for the monitor.
    type: str
  end_timestamp:
    description: End timestamp for the monitor.
    type: str
  notify_at:
    description: List of percentage thresholds for notifications.
    type: list
    elements: int
  suspend_at:
    description: Percentage at which to suspend warehouses.
    type: int
  suspend_immediately_at:
    description: Percentage at which to immediately suspend warehouses.
    type: int
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create a resource monitor
  stevefulme1.snowflake.resource_monitor:
    name: MONTHLY_MONITOR
    credit_quota: 1000
    notify_at: [75, 90, 100]
    suspend_at: 100
    suspend_immediately_at: 110
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
        state=dict(type="str", default="present", choices=["present", "absent"]),
        credit_quota=dict(type="int"),
        frequency=dict(
            type="str",
            default="MONTHLY",
            choices=["MONTHLY", "DAILY", "WEEKLY", "YEARLY", "NEVER"],
        ),
        start_timestamp=dict(type="str"),
        end_timestamp=dict(type="str"),
        notify_at=dict(type="list", elements="int"),
        suspend_at=dict(type="int"),
        suspend_immediately_at=dict(type="int"),
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

    if state == "absent":
        sql = "DROP RESOURCE MONITOR IF EXISTS {0}".format(SnowflakeClient.quote_identifier(name))
    else:
        parts = ["CREATE OR REPLACE RESOURCE MONITOR {0}".format(SnowflakeClient.quote_identifier(name))]
        parts.append("WITH CREDIT_QUOTA = {0}".format(module.params.get("credit_quota", 0)))
        parts.append("FREQUENCY = {0}".format(module.params["frequency"]))
        if module.params.get("start_timestamp"):
            parts.append("START_TIMESTAMP = '{0}'".format(escape_sql_string(module.params["start_timestamp"])))
        else:
            parts.append("START_TIMESTAMP = IMMEDIATELY")
        if module.params.get("end_timestamp"):
            parts.append("END_TIMESTAMP = '{0}'".format(escape_sql_string(module.params["end_timestamp"])))

        triggers = []
        if module.params.get("notify_at"):
            for pct in module.params["notify_at"]:
                triggers.append("ON {0} PERCENT DO NOTIFY".format(pct))
        if module.params.get("suspend_at"):
            triggers.append("ON {0} PERCENT DO SUSPEND".format(module.params["suspend_at"]))
        if module.params.get("suspend_immediately_at"):
            triggers.append("ON {0} PERCENT DO SUSPEND_IMMEDIATE".format(module.params["suspend_immediately_at"]))
        if triggers:
            parts.append("TRIGGERS " + " ".join(triggers))
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
