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
module: materialized_view
short_description: Manage Snowflake materialized views
description:
  - Create or drop a materialized view in Snowflake.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the materialized view.
    type: str
    required: true
  schema_name:
    description: Schema for the view.
    type: str
    required: true
  database_name:
    description: Database for the view.
    type: str
    required: true
  query:
    description: SELECT statement defining the view.
    type: str
  secure:
    description: Create as a secure materialized view.
    type: bool
    default: false
  cluster_by:
    description: Clustering expressions for the materialized view.
    type: list
    elements: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create materialized view
  stevefulme1.snowflake.materialized_view:
    name: MV_DAILY_STATS
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    query: "SELECT region, COUNT(*) cnt FROM events GROUP BY region"
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
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        query=dict(type="str"),
        secure=dict(type="bool", default=False),
        cluster_by=dict(type="list", elements="str"),
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
        module.params["name"].upper(),
    )
    state = module.params["state"]

    if state == "absent":
        sql = "DROP MATERIALIZED VIEW IF EXISTS {0}".format(fqn)
    else:
        q = module.params.get("query")
        if not q:
            module.fail_json(msg="query is required when state=present")
        prefix = (
            "CREATE OR REPLACE SECURE MATERIALIZED VIEW"
            if module.params["secure"]
            else "CREATE OR REPLACE MATERIALIZED VIEW"
        )
        parts = ["{0} {1}".format(prefix, fqn)]
        if module.params.get("cluster_by"):
            parts.append(
                "CLUSTER BY ({0})".format(
                    ", ".join(module.params["cluster_by"]))
            )
        parts.append("AS {0}".format(q))
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
