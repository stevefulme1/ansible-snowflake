#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: warehouse_parameter
short_description: Set a parameter on a Snowflake warehouse
description:
  - Alter a warehouse parameter using ALTER WAREHOUSE SET.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the warehouse.
    type: str
    required: true
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
- name: Set statement timeout on warehouse
  stevefulme1.snowflake.warehouse_parameter:
    name: ANALYTICS_WH
    parameter: STATEMENT_TIMEOUT_IN_SECONDS
    value: "3600"
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
        name=dict(type="str", required=True),
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

    name = module.params["name"].upper()
    param = module.params["parameter"].upper()
    value = module.params["value"]
    sql = "ALTER WAREHOUSE {0} SET {1} = {2}".format(SnowflakeClient.quote_identifier(name), param, value)

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
