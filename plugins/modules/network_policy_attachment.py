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
module: network_policy_attachment
short_description: Attach a network policy to account or user
description:
  - Attach or detach a network policy at the account or user level.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the network policy.
    type: str
    required: true
  target:
    description: Attach to C(account) or a specific C(user).
    type: str
    choices: [account, user]
    default: account
  user_name:
    description: User name when I(target=user).
    type: str
  state:
    description: Whether to attach or detach.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Attach network policy to account
  stevefulme1.snowflake.network_policy_attachment:
    name: OFFICE_POLICY
    target: account
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
        target=dict(
            type="str",
            default="account",
            choices=[
                "account",
                "user"]),
        user_name=dict(type="str"),
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

    name = module.params["name"].upper()
    target = module.params["target"]
    state = module.params["state"]

    if target == "account":
        if state == "present":
            sql = "ALTER ACCOUNT SET NETWORK_POLICY = {0}".format(
                SnowflakeClient.quote_identifier(name)
            )
        else:
            sql = "ALTER ACCOUNT UNSET NETWORK_POLICY"
    else:
        user_name = module.params["user_name"]
        if not user_name:
            module.fail_json(msg="user_name is required when target=user")
        if state == "present":
            sql = "ALTER USER {0} SET NETWORK_POLICY = {1}".format(
                SnowflakeClient.quote_identifier(user_name.upper()),
                SnowflakeClient.quote_identifier(name),
            )
        else:
            sql = "ALTER USER {0} UNSET NETWORK_POLICY".format(
                SnowflakeClient.quote_identifier(user_name.upper())
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
