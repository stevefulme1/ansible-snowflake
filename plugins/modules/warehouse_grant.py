#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: warehouse_grant
short_description: Manage grants on a Snowflake warehouse
description:
  - Grant or revoke privileges on a warehouse.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the warehouse.
    type: str
    required: true
  privilege:
    description: Privilege to grant.
    type: str
    required: true
    choices: [USAGE, OPERATE, MONITOR, MODIFY, ALL PRIVILEGES]
  role:
    description: Role to grant the privilege to.
    type: str
    required: true
  state:
    description: Whether to grant or revoke.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Grant USAGE on warehouse to role
  stevefulme1.snowflake.warehouse_grant:
    name: ANALYTICS_WH
    privilege: USAGE
    role: ANALYST_ROLE
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
        privilege=dict(
            type="str",
            required=True,
            choices=["USAGE", "OPERATE", "MONITOR", "MODIFY", "ALL PRIVILEGES"],
        ),
        role=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
    )
    # Rename the module-level 'role' to avoid conflict with arg_spec 'role'
    spec = dict(snowflake_argument_spec)
    argument_spec.update(spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    wh_name = module.params["name"].upper()
    privilege = module.params["privilege"]
    target_role = module.params["role"]
    state = module.params["state"]

    if state == "present":
        sql = "GRANT {0} ON WAREHOUSE {1} TO ROLE {2}".format(
            privilege,
            SnowflakeClient.quote_identifier(wh_name),
            SnowflakeClient.quote_identifier(target_role),
        )
    else:
        sql = "REVOKE {0} ON WAREHOUSE {1} FROM ROLE {2}".format(
            privilege,
            SnowflakeClient.quote_identifier(wh_name),
            SnowflakeClient.quote_identifier(target_role),
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
