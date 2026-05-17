#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: schema_info
short_description: List Snowflake schemas
description:
  - Retrieve information about schemas using SHOW SCHEMAS.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Filter to a specific schema name pattern.
    type: str
  database:
    description: Database to list schemas in.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: List all schemas in a database
  stevefulme1.snowflake.schema_info:
    database: ANALYTICS_DB
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
schemas:
  description: List of schema records.
  type: list
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
    escape_sql_string,
)


def run_module():
    argument_spec = dict(
        name=dict(type="str"),
        database=dict(type="str"),
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
        sql = "SHOW SCHEMAS"
        if module.params.get("database"):
            sql += " IN DATABASE {0}".format(
                client.quote_identifier(module.params["database"].upper())
            )
        if module.params.get("name"):
            sql += " LIKE '{0}'".format(escape_sql_string(module.params["name"]))
        rows = client.query(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=False, schemas=rows)


def main():
    run_module()


if __name__ == "__main__":
    main()
