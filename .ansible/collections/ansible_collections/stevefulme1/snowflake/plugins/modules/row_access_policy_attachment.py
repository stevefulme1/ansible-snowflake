#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: row_access_policy_attachment
short_description: Attach a row access policy to a table
description:
  - Add or drop a row access policy on a table.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  table:
    description: Fully qualified table name.
    type: str
    required: true
  policy:
    description: Fully qualified row access policy name.
    type: str
    required: true
  on_columns:
    description: Columns the policy maps to.
    type: list
    elements: str
    required: true
  state:
    description: Whether to add or drop.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Add row access policy to table
  stevefulme1.snowflake.row_access_policy_attachment:
    table: MYDB.PUBLIC.ORDERS
    policy: MYDB.GOVERNANCE.REGION_FILTER
    on_columns: [REGION]
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
        table=dict(type="str", required=True),
        policy=dict(type="str", required=True),
        on_columns=dict(type="list", elements="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    table = module.params["table"]
    policy = module.params["policy"]
    columns = ", ".join(module.params["on_columns"])
    state = module.params["state"]

    if state == "present":
        sql = "ALTER TABLE {0} ADD ROW ACCESS POLICY {1} ON ({2})".format(
            table, policy, columns
        )
    else:
        sql = "ALTER TABLE {0} DROP ROW ACCESS POLICY {1}".format(table, policy)

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
