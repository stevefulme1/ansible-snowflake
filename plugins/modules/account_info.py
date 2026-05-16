#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: account_info
short_description: List Snowflake account parameters
description:
  - Retrieve account parameters using SHOW PARAMETERS IN ACCOUNT.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Filter to a specific parameter name pattern.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: List all account parameters
  stevefulme1.snowflake.account_info:
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
parameters:
  description: List of account parameter records.
  type: list
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
)


def run_module():
    argument_spec = dict(name=dict(type="str"))
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    try:
        client = SnowflakeClient(module)
        sql = "SHOW PARAMETERS IN ACCOUNT"
        if module.params.get("name"):
            sql += " LIKE '{0}'".format(module.params["name"])
        rows = client.query(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=False, parameters=rows)


def main():
    run_module()


if __name__ == "__main__":
    main()
