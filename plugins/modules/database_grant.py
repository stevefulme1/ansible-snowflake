#!/usr/bin/python
# -*- coding: utf-8 -*-
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
module: database_grant
short_description: Manage grants on a Snowflake database
description:
  - Grant or revoke privileges on a database.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the database.
    type: str
    required: true
  privilege:
    description: Privilege to grant.
    type: str
    required: true
    choices: [USAGE, MONITOR, CREATE SCHEMA, MODIFY, ALL PRIVILEGES]
  role:
    description: Role to grant the privilege to.
    type: str
    required: true
  state:
    description: Whether to grant or revoke.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Grant USAGE on database
  stevefulme1.snowflake.database_grant:
    name: ANALYTICS_DB
    privilege: USAGE
    role: ANALYST_ROLE
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
    argument_spec = dict(snowflake_argument_spec)
    argument_spec.update(
        name=dict(type="str", required=True),
        privilege=dict(
            type="str",
            required=True,
            choices=[
                "USAGE",
                "MONITOR",
                "CREATE SCHEMA",
                "MODIFY",
                "ALL PRIVILEGES"],
        ),
        role=dict(type="str", required=True),
        state=dict(
            type="str",
            default="present",
            choices=[
                "present",
                "absent"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    name = module.params["name"].upper()
    privilege = module.params["privilege"]
    target_role = module.params["role"]
    state = module.params["state"]

    action = "GRANT" if state == "present" else "REVOKE"
    prep = "TO" if state == "present" else "FROM"
    sql = "{0} {1} ON DATABASE {2} {3} ROLE {4}".format(
        action,
        privilege,
        SnowflakeClient.quote_identifier(name),
        prep,
        SnowflakeClient.quote_identifier(target_role),
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
