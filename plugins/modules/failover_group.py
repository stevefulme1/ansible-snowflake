#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: failover_group
short_description: Manage Snowflake failover groups
description:
  - Create, alter, or drop a failover group for business continuity.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the failover group.
    type: str
    required: true
  object_types:
    description: Object types to replicate (DATABASES, SHARES, ROLES, etc.).
    type: list
    elements: str
  allowed_databases:
    description: Databases to include in replication.
    type: list
    elements: str
  allowed_accounts:
    description: Target accounts for failover.
    type: list
    elements: str
  replication_schedule:
    description: Replication schedule (e.g. "10 MINUTE").
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
- name: Create failover group
  stevefulme1.snowflake.failover_group:
    name: MY_FG
    object_types: [DATABASES]
    allowed_databases: [ANALYTICS_DB]
    allowed_accounts: [ORG1.ACCT2]
    replication_schedule: "10 MINUTE"
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
)


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        object_types=dict(type="list", elements="str"),
        allowed_databases=dict(type="list", elements="str"),
        allowed_accounts=dict(type="list", elements="str"),
        replication_schedule=dict(type="str"),
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
        sql = "DROP FAILOVER GROUP IF EXISTS {0}".format(name)
    else:
        parts = ["CREATE FAILOVER GROUP IF NOT EXISTS {0}".format(name)]
        if module.params.get("object_types"):
            parts.append(
                "OBJECT_TYPES = {0}".format(
                    ", ".join(t.upper() for t in module.params["object_types"])
                )
            )
        if module.params.get("allowed_databases"):
            parts.append(
                "ALLOWED_DATABASES = {0}".format(
                    ", ".join(module.params["allowed_databases"])
                )
            )
        if module.params.get("allowed_accounts"):
            parts.append(
                "ALLOWED_ACCOUNTS = {0}".format(
                    ", ".join(module.params["allowed_accounts"])
                )
            )
        if module.params.get("replication_schedule"):
            parts.append(
                "REPLICATION_SCHEDULE = '{0}'".format(
                    module.params["replication_schedule"]
                )
            )
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
