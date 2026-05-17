#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: database_role
short_description: Manage Snowflake database roles
description:
  - Create or drop a database role.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the database role.
    type: str
    required: true
  database:
    description: Database the role belongs to.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  comment:
    description: Comment for the role.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create a database role
  stevefulme1.snowflake.database_role:
    name: DB_READER
    database: ANALYTICS_DB
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
    argument_spec = dict(snowflake_argument_spec)
    argument_spec.update(
        name=dict(type="str", required=True),
        database=dict(type="str", required=True),
        state=dict(
            type="str",
            default="present",
            choices=[
                "present",
                "absent"]),
        comment=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    name = module.params["name"].upper()
    db = module.params["database"].upper()
    state = module.params["state"]
    fqn = "{0}.{1}".format(
        SnowflakeClient.quote_identifier(
            db), SnowflakeClient.quote_identifier(name)
    )

    if state == "absent":
        sql = "DROP DATABASE ROLE IF EXISTS {0}".format(fqn)
    else:
        parts = ["CREATE DATABASE ROLE IF NOT EXISTS {0}".format(fqn)]
        if module.params.get("comment"):
            parts.append(
                "COMMENT = '{0}'".format(
                    escape_sql_string(
                        module.params["comment"])))
        sql = " ".join(parts)

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
