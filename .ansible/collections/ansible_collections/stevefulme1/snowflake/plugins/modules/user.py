#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: user
short_description: Manage Snowflake users
description:
  - Create, alter, or drop a Snowflake user.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Login name of the user.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  login_name:
    description: Login name (defaults to I(name)).
    type: str
  display_name:
    description: Display name.
    type: str
  email:
    description: Email address.
    type: str
  first_name:
    description: First name.
    type: str
  last_name:
    description: Last name.
    type: str
  default_role:
    description: Default role assigned on login.
    type: str
  default_warehouse:
    description: Default warehouse.
    type: str
  default_namespace:
    description: Default database.schema namespace.
    type: str
  must_change_password:
    description: Whether the user must change password on first login.
    type: bool
    default: false
  disabled:
    description: Whether the user is disabled.
    type: bool
    default: false
  user_password:
    description: Password for the new user.
    type: str
  comment:
    description: Comment for the user.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create a user
  stevefulme1.snowflake.user:
    name: JDOE
    email: jdoe@example.com
    default_role: ANALYST_ROLE
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
user:
  description: Name of the user managed.
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
)


def user_exists(client, name):
    rows = client.query("SHOW USERS LIKE '{0}'".format(name))
    return len(rows) > 0


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        login_name=dict(type="str"),
        display_name=dict(type="str"),
        email=dict(type="str"),
        first_name=dict(type="str"),
        last_name=dict(type="str"),
        default_role=dict(type="str"),
        default_warehouse=dict(type="str"),
        default_namespace=dict(type="str"),
        must_change_password=dict(type="bool", default=False),
        disabled=dict(type="bool", default=False),
        user_password=dict(type="str", no_log=True),
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

    props = []
    for param, sf_prop in [
        ("login_name", "LOGIN_NAME"),
        ("display_name", "DISPLAY_NAME"),
        ("email", "EMAIL"),
        ("first_name", "FIRST_NAME"),
        ("last_name", "LAST_NAME"),
        ("default_role", "DEFAULT_ROLE"),
        ("default_warehouse", "DEFAULT_WAREHOUSE"),
        ("default_namespace", "DEFAULT_NAMESPACE"),
    ]:
        if module.params.get(param):
            props.append("{0} = '{1}'".format(sf_prop, module.params[param]))
    if module.params.get("user_password"):
        props.append("PASSWORD = '{0}'".format(module.params["user_password"]))
    props.append(
        "MUST_CHANGE_PASSWORD = {0}".format(
            str(module.params["must_change_password"]).upper()
        )
    )
    props.append("DISABLED = {0}".format(str(module.params["disabled"]).upper()))
    if module.params.get("comment"):
        props.append("COMMENT = '{0}'".format(module.params["comment"]))

    try:
        client = SnowflakeClient(module)
        exists = user_exists(client, name)

        if state == "absent":
            if exists:
                sql = "DROP USER IF EXISTS {0}".format(client.quote_identifier(name))
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
        else:
            if not exists:
                sql = "CREATE USER IF NOT EXISTS {0} {1}".format(
                    client.quote_identifier(name), " ".join(props)
                )
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
            else:
                sql = "ALTER USER {0} SET {1}".format(
                    client.quote_identifier(name), " ".join(props)
                )
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed, user=name, sql=sql)


def main():
    run_module()


if __name__ == "__main__":
    main()
