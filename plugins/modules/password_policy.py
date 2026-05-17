#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: password_policy
short_description: Manage Snowflake password policies
description:
  - Create, alter, or drop a password policy.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the password policy.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  password_min_length:
    description: Minimum password length.
    type: int
    default: 8
  password_max_length:
    description: Maximum password length.
    type: int
    default: 256
  password_min_upper_case_chars:
    description: Minimum uppercase characters.
    type: int
    default: 1
  password_min_lower_case_chars:
    description: Minimum lowercase characters.
    type: int
    default: 1
  password_min_numeric_chars:
    description: Minimum numeric characters.
    type: int
    default: 1
  password_min_special_chars:
    description: Minimum special characters.
    type: int
    default: 0
  password_max_age_days:
    description: Maximum password age in days (0 disables expiry).
    type: int
    default: 90
  password_max_retries:
    description: Maximum login retries before lockout.
    type: int
    default: 5
  password_lockout_time_mins:
    description: Lockout duration in minutes.
    type: int
    default: 15
  comment:
    description: Comment for the policy.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create a password policy
  stevefulme1.snowflake.password_policy:
    name: STRICT_PW_POLICY
    password_min_length: 14
    password_max_age_days: 60
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
        name=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        password_min_length=dict(type="int", default=8, no_log=False),
        password_max_length=dict(type="int", default=256, no_log=False),
        password_min_upper_case_chars=dict(type="int", default=1, no_log=False),
        password_min_lower_case_chars=dict(type="int", default=1, no_log=False),
        password_min_numeric_chars=dict(type="int", default=1, no_log=False),
        password_min_special_chars=dict(type="int", default=0, no_log=False),
        password_max_age_days=dict(type="int", default=90, no_log=False),
        password_max_retries=dict(type="int", default=5, no_log=False),
        password_lockout_time_mins=dict(type="int", default=15, no_log=False),
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

    props = [
        "PASSWORD_MIN_LENGTH = {0}".format(module.params["password_min_length"]),
        "PASSWORD_MAX_LENGTH = {0}".format(module.params["password_max_length"]),
        "PASSWORD_MIN_UPPER_CASE_CHARS = {0}".format(module.params["password_min_upper_case_chars"]),
        "PASSWORD_MIN_LOWER_CASE_CHARS = {0}".format(module.params["password_min_lower_case_chars"]),
        "PASSWORD_MIN_NUMERIC_CHARS = {0}".format(module.params["password_min_numeric_chars"]),
        "PASSWORD_MIN_SPECIAL_CHARS = {0}".format(module.params["password_min_special_chars"]),
        "PASSWORD_MAX_AGE_DAYS = {0}".format(module.params["password_max_age_days"]),
        "PASSWORD_MAX_RETRIES = {0}".format(module.params["password_max_retries"]),
        "PASSWORD_LOCKOUT_TIME_MINS = {0}".format(module.params["password_lockout_time_mins"]),
    ]
    if module.params.get("comment"):
        props.append("COMMENT = '{0}'".format(escape_sql_string(module.params["comment"])))

    try:
        client = SnowflakeClient(module)

        if state == "absent":
            sql = "DROP PASSWORD POLICY IF EXISTS {0}".format(client.quote_identifier(name))
            changed = True
            if not module.check_mode:
                client.execute_ddl(sql)
        else:
            # Try create, fall back to alter
            sql = "CREATE PASSWORD POLICY IF NOT EXISTS {0} {1}".format(client.quote_identifier(name), " ".join(props))
            changed = True
            if not module.check_mode:
                try:
                    client.execute_ddl(sql)
                except SnowflakeError:
                    sql = "ALTER PASSWORD POLICY {0} SET {1}".format(client.quote_identifier(name), " ".join(props))
                    client.execute_ddl(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed, sql=sql)


def main():
    run_module()


if __name__ == "__main__":
    main()
