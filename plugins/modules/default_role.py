#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
    escape_sql_string,
)
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r"""
---
module: default_role
short_description: Set a user default role in Snowflake
description:
  - Alter a user to set their DEFAULT_ROLE.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  user_name:
    description: User whose default role to set.
    type: str
    required: true
  default_role:
    description: Role to set as default.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Set default role for user
  stevefulme1.snowflake.default_role:
    user_name: JDOE
    default_role: ANALYST_ROLE
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
        user_name=dict(type="str", required=True),
        default_role=dict(type="str", required=True),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    user_name = module.params["user_name"].upper()
    role_name = module.params["default_role"].upper()
    sql = "ALTER USER {0} SET DEFAULT_ROLE = '{1}'".format(
        SnowflakeClient.quote_identifier(
            user_name), escape_sql_string(role_name)
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
