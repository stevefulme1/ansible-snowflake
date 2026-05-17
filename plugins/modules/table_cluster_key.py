#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
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
module: table_cluster_key
short_description: Manage clustering keys on a Snowflake table
description:
  - Set or drop clustering keys on a table for micro-partition optimization.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  table_name:
    description: Name of the table.
    type: str
    required: true
  schema_name:
    description: Schema of the table.
    type: str
    required: true
  database_name:
    description: Database of the table.
    type: str
    required: true
  cluster_keys:
    description: List of columns or expressions to cluster by.
    type: list
    elements: str
  state:
    description: Whether clustering key is present or absent.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Set clustering key
  stevefulme1.snowflake.table_cluster_key:
    table_name: EVENTS
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    cluster_keys: [CREATED_AT, REGION]
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
        table_name=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        cluster_keys=dict(type="list", elements="str", no_log=False),
        state=dict(
            type="str",
            default="present",
            choices=[
                "present",
                "absent"]),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    fqn = "{0}.{1}.{2}".format(
        module.params["database_name"].upper(),
        module.params["schema_name"].upper(),
        module.params["table_name"].upper(),
    )
    state = module.params["state"]

    if state == "present":
        keys = module.params.get("cluster_keys")
        if not keys:
            module.fail_json(msg="cluster_keys required when state=present")
        sql = "ALTER TABLE {0} CLUSTER BY ({1})".format(fqn, ", ".join(keys))
    else:
        sql = "ALTER TABLE {0} DROP CLUSTERING KEY".format(fqn)

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
