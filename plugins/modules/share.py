#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: share
short_description: Manage Snowflake shares
description:
  - Create, alter, or drop a Snowflake share for secure data sharing.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the share.
    type: str
    required: true
  accounts:
    description: List of consumer account identifiers.
    type: list
    elements: str
  comment:
    description: Comment for the share.
    type: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create a share
  stevefulme1.snowflake.share:
    name: ANALYTICS_SHARE
    accounts: [ORG1.CONSUMER_ACCT]
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
    escape_sql_string,
)


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        accounts=dict(type="list", elements="str"),
        comment=dict(type="str"),
        state=dict(type="str", default="present", choices=["present", "absent"]),
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

    if state == "absent":
        sql = "DROP SHARE IF EXISTS {0}".format(name)
    else:
        parts = ["CREATE SHARE IF NOT EXISTS {0}".format(name)]
        if module.params.get("comment"):
            parts.append("COMMENT = '{0}'".format(escape_sql_string(module.params["comment"])))
        sql = " ".join(parts)

    try:
        client = SnowflakeClient(module)
        if not module.check_mode:
            client.execute_ddl(sql)
        if state == "present" and module.params.get("accounts"):
            add_sql = "ALTER SHARE {0} ADD ACCOUNTS = {1}".format(
                name, ", ".join(module.params["accounts"])
            )
            if not module.check_mode:
                client.execute_ddl(add_sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=True, sql=sql)


def main():
    run_module()


if __name__ == "__main__":
    main()
