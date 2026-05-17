#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: object_parameter
short_description: Set parameters on Snowflake objects
description:
  - Set or unset parameters on tables, warehouses, or other objects.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  object_type:
    description: Type of object (TABLE, WAREHOUSE, DATABASE, SCHEMA).
    type: str
    required: true
  object_name:
    description: Fully qualified object name.
    type: str
    required: true
  parameter_name:
    description: Parameter name to set.
    type: str
    required: true
  parameter_value:
    description: Value to set (omit to unset).
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Set table parameter
  stevefulme1.snowflake.object_parameter:
    object_type: TABLE
    object_name: ANALYTICS_DB.PUBLIC.EVENTS
    parameter_name: DATA_RETENTION_TIME_IN_DAYS
    parameter_value: "14"
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
    escape_sql_string,
)
from ansible.module_utils.basic import AnsibleModule


def run_module():
    argument_spec = dict(
        object_type=dict(type="str", required=True),
        object_name=dict(type="str", required=True),
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

    obj_type = module.params["object_type"].upper()
    obj_name = module.params["object_name"].upper()
    param = module.params["parameter_name"].upper()
    value = module.params.get("parameter_value")

    if value is not None:
        sql = "ALTER {0} {1} SET {2} = '{3}'".format(obj_type, obj_name, param, escape_sql_string(value))
    else:
        sql = "ALTER {0} {1} UNSET {2}".format(obj_type, obj_name, param)

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
