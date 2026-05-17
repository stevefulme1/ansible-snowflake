#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: database_role_grant
short_description: Grant a Snowflake database role
description:
  - Grant or revoke a database role to/from a role or user.
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
  to_role:
    description: Account role to grant the database role to.
    type: str
  to_database_role:
    description: Another database role to grant to.
    type: str
  state:
    description: Whether to grant or revoke.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Grant database role to account role
  stevefulme1.snowflake.database_role_grant:
    name: DB_READER
    database: ANALYTICS_DB
    to_role: ANALYST_ROLE
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
    argument_spec = dict(snowflake_argument_spec)
    argument_spec.update(
        name=dict(type="str", required=True),
        database=dict(type="str", required=True),
        to_role=dict(type="str"),
        to_database_role=dict(type="str"),
        state=dict(type="str", default="present", choices=["present", "absent"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ("private_key", "password"),
            ("to_role", "to_database_role"),
        ],
        required_one_of=[("private_key", "password"), ("to_role", "to_database_role")],
        supports_check_mode=True,
    )

    db = module.params["database"].upper()
    role_name = module.params["name"].upper()
    state = module.params["state"]
    fqn = "{0}.{1}".format(
        SnowflakeClient.quote_identifier(db),
        SnowflakeClient.quote_identifier(role_name),
    )

    action = "GRANT" if state == "present" else "REVOKE"
    prep = "TO" if state == "present" else "FROM"

    if module.params.get("to_role"):
        target = "ROLE {0}".format(SnowflakeClient.quote_identifier(module.params["to_role"].upper()))
    else:
        tdb_role = module.params["to_database_role"].upper()
        target = "DATABASE ROLE {0}.{1}".format(
            SnowflakeClient.quote_identifier(db),
            SnowflakeClient.quote_identifier(tdb_role),
        )

    sql = "{0} DATABASE ROLE {1} {2} {3}".format(action, fqn, prep, target)

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
