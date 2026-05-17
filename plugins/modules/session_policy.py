#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
    escape_sql_string,
)
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r"""
---
module: session_policy
short_description: Manage Snowflake session policies
description:
  - Create, alter, or drop a session policy.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the session policy.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  session_idle_timeout_mins:
    description: Idle timeout in minutes.
    type: int
    default: 240
  session_ui_idle_timeout_mins:
    description: UI idle timeout in minutes.
    type: int
    default: 240
  comment:
    description: Comment for the policy.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create session policy
  stevefulme1.snowflake.session_policy:
    name: SHORT_SESSION
    session_idle_timeout_mins: 30
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
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(
            type="str",
            default="present",
            choices=[
                "present",
                "absent"]),
        session_idle_timeout_mins=dict(type="int", default=240),
        session_ui_idle_timeout_mins=dict(type="int", default=240),
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

    props = [
        "SESSION_IDLE_TIMEOUT_MINS = {0}".format(
            module.params["session_idle_timeout_mins"]
        ),
        "SESSION_UI_IDLE_TIMEOUT_MINS = {0}".format(
            module.params["session_ui_idle_timeout_mins"]
        ),
    ]
    if module.params.get("comment"):
        props.append(
            "COMMENT = '{0}'".format(
                escape_sql_string(
                    module.params["comment"])))

    if state == "absent":
        sql = "DROP SESSION POLICY IF EXISTS {0}".format(
            SnowflakeClient.quote_identifier(name)
        )
    else:
        sql = "CREATE OR REPLACE SESSION POLICY {0} {1}".format(
            SnowflakeClient.quote_identifier(name), " ".join(props)
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
