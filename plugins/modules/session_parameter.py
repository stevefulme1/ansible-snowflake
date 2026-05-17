#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
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
module: session_parameter
short_description: Set Snowflake session parameters
description:
  - Set or unset session-level parameters.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  parameter_name:
    description: Name of the session parameter.
    type: str
    required: true
  parameter_value:
    description: Value to set (omit to unset).
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Set session timezone
  stevefulme1.snowflake.session_parameter:
    parameter_name: TIMEZONE
    parameter_value: America/New_York
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
        parameter_name=dict(type="str", required=True),
        parameter_value=dict(type="str"),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    param = module.params["parameter_name"].upper()
    value = module.params.get("parameter_value")

    if value is not None:
        sql = "ALTER SESSION SET {0} = '{1}'".format(
            param, escape_sql_string(value))
    else:
        sql = "ALTER SESSION UNSET {0}".format(param)

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
