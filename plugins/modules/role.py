#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: role
short_description: Manage Snowflake roles
description:
  - Create or drop a Snowflake role.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the role.
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
- name: Create a role
  stevefulme1.snowflake.role:
    name: ANALYST_ROLE
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
role:
  description: Name of the role managed.
  type: str
  returned: always
sql:
  description: The SQL statement executed.
  type: str
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
    escape_sql_string,
)


def role_exists(client, name):
    rows = client.query("SHOW ROLES LIKE '{0}'".format(escape_sql_string(name)))
    return len(rows) > 0


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        comment=dict(type="str"),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    name = module.params["name"].upper()
    state = module.params["state"]
    changed = False
    sql = ""

    try:
        client = SnowflakeClient(module)
        exists = role_exists(client, name)

        if state == "absent":
            if exists:
                sql = "DROP ROLE IF EXISTS {0}".format(client.quote_identifier(name))
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
        else:
            if not exists:
                parts = [
                    "CREATE ROLE IF NOT EXISTS {0}".format(
                        client.quote_identifier(name)
                    )
                ]
                if module.params.get("comment"):
                    parts.append("COMMENT = '{0}'".format(escape_sql_string(module.params["comment"])))
                sql = " ".join(parts)
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed, role=name, sql=sql)


def main():
    run_module()


if __name__ == "__main__":
    main()
