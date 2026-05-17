#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: user_grant
short_description: Grant privileges to a Snowflake user
description:
  - Grant or revoke global privileges on account objects to a user.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  privilege:
    description: Privilege to grant.
    type: str
    required: true
  "on":
    description: Object type and name (e.g. C(DATABASE MYDB)).
    type: str
    required: true
  to_role:
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
- name: Grant SELECT on all tables
  stevefulme1.snowflake.user_grant:
    privilege: SELECT
    "on": "ALL TABLES IN SCHEMA MYDB.PUBLIC"
    to_role: ANALYST_ROLE
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
        privilege=dict(type="str", required=True),
        on=dict(type="str", required=True),
        to_role=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    privilege = module.params["privilege"].upper()
    on = module.params["on"]
    to_role = module.params["to_role"].upper()
    state = module.params["state"]

    action = "GRANT" if state == "present" else "REVOKE"
    prep = "TO" if state == "present" else "FROM"
    sql = "{0} {1} ON {2} {3} ROLE {4}".format(action, privilege, on, prep, SnowflakeClient.quote_identifier(to_role))

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
