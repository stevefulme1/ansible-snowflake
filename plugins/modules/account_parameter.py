#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: account_parameter
short_description: Set an account-level parameter in Snowflake
description:
  - Alter an account parameter using ALTER ACCOUNT SET.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  parameter:
    description: Parameter name to set.
    type: str
    required: true
  value:
    description: Value to set the parameter to.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Set account timezone
  stevefulme1.snowflake.account_parameter:
    parameter: TIMEZONE
    value: "'America/New_York'"
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
        parameter=dict(type="str", required=True),
        value=dict(type="str", required=True),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    param = module.params["parameter"].upper()
    value = module.params["value"]
    sql = "ALTER ACCOUNT SET {0} = {1}".format(param, value)

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
