#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: database_replica
short_description: Enable replication on a Snowflake database
description:
  - Enable or disable replication on a database to target accounts.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the database.
    type: str
    required: true
  target_accounts:
    description: Target accounts for replication.
    type: list
    elements: str
    required: true
  enabled:
    description: Whether replication is enabled or disabled.
    type: bool
    default: true
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Enable replication
  stevefulme1.snowflake.database_replica:
    name: ANALYTICS_DB
    target_accounts: [ORG1.ACCT2]
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
    argument_spec = dict(
        name=dict(type="str", required=True),
        target_accounts=dict(type="list", elements="str", required=True),
        enabled=dict(type="bool", default=True),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    name = module.params["name"].upper()
    accounts = ", ".join(module.params["target_accounts"])

    if module.params["enabled"]:
        sql = "ALTER DATABASE {0} ENABLE REPLICATION TO ACCOUNTS {1}".format(name, accounts)
    else:
        sql = "ALTER DATABASE {0} DISABLE REPLICATION TO ACCOUNTS {1}".format(name, accounts)

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
