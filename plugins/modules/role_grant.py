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
module: role_grant
short_description: Grant a Snowflake role to a user or another role
description:
  - Grant or revoke a role assignment using GRANT ROLE / REVOKE ROLE.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the role to grant.
    type: str
    required: true
  to_user:
    description: User to grant the role to.
    type: str
  to_role:
    description: Parent role to grant the role to.
    type: str
  state:
    description: Whether to grant or revoke.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Grant role to user
  stevefulme1.snowflake.role_grant:
    name: ANALYST_ROLE
    to_user: JDOE
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
        name=dict(type="str", required=True),
        to_user=dict(type="str"),
        to_role=dict(type="str"),
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
        mutually_exclusive=[("private_key", "password"),
                            ("to_user", "to_role")],
        required_one_of=[("private_key", "password"), ("to_user", "to_role")],
        supports_check_mode=True,
    )

    role_name = module.params["name"].upper()
    state = module.params["state"]
    action = "GRANT" if state == "present" else "REVOKE"
    prep = "TO" if state == "present" else "FROM"

    if module.params.get("to_user"):
        target = "USER {0}".format(
            SnowflakeClient.quote_identifier(module.params["to_user"].upper())
        )
    else:
        target = "ROLE {0}".format(
            SnowflakeClient.quote_identifier(module.params["to_role"].upper())
        )

    sql = "{0} ROLE {1} {2} {3}".format(
        action, SnowflakeClient.quote_identifier(role_name), prep, target
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
