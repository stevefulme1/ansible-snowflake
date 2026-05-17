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
)
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type
DOCUMENTATION = r"""
---
module: cortex_function_info
short_description: Get Cortex function info
description:
  - Retrieve information about user-defined functions including Cortex AI functions.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Filter to a specific function name pattern.
    type: str
  database_name:
    description: Database to scope the query.
    type: str
  schema_name:
    description: Schema to scope the query.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: List all functions
  stevefulme1.snowflake.cortex_function_info:
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"

- name: Get functions in a specific schema
  stevefulme1.snowflake.cortex_function_info:
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
    database_name: ANALYTICS_DB
    schema_name: PUBLIC
"""

RETURN = r"""
functions:
  description: List of function records.
  type: list
  returned: always
"""


def run_module():
    argument_spec = dict(
        name=dict(type="str"),
        database_name=dict(type="str"),
        schema_name=dict(type="str"),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    try:
        client = SnowflakeClient(module)
        sql = "SHOW USER FUNCTIONS"
        if module.params.get("name"):
            sql += " LIKE '{0}'".format(module.params["name"])
        if module.params.get(
                "database_name") and module.params.get("schema_name"):
            sql += " IN SCHEMA {0}.{1}".format(
                module.params["database_name"].upper(),
                module.params["schema_name"].upper(),
            )
        elif module.params.get("database_name"):
            sql += " IN DATABASE {0}".format(
                module.params["database_name"].upper())
        rows = client.query(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=False, functions=rows)


def main():
    run_module()


if __name__ == "__main__":
    main()
