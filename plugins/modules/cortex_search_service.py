#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: cortex_search_service
short_description: Manage Snowflake Cortex Search services
description:
  - Create or drop a Cortex Search service for AI-powered search.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the search service.
    type: str
    required: true
  schema_name:
    description: Schema for the service.
    type: str
    required: true
  database_name:
    description: Database for the service.
    type: str
    required: true
  warehouse_name:
    description: Warehouse for building the index.
    type: str
  target_lag:
    description: Target lag for index refresh.
    type: str
  "on":
    description: Column to index for search.
    type: str
  query:
    description: Source query for the search index.
    type: str
  comment:
    description: Comment for the service.
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
- name: Create Cortex Search service
  stevefulme1.snowflake.cortex_search_service:
    name: DOC_SEARCH
    schema_name: PUBLIC
    database_name: AI_DB
    warehouse_name: COMPUTE_WH
    target_lag: "1 hour"
    "on": CONTENT
    query: "SELECT id, content FROM documents"
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
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        warehouse_name=dict(type="str"),
        target_lag=dict(type="str"),
        on=dict(type="str"),
        query=dict(type="str"),
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

    fqn = "{0}.{1}.{2}".format(
        module.params["database_name"].upper(),
        module.params["schema_name"].upper(),
        module.params["name"].upper(),
    )
    state = module.params["state"]

    if state == "absent":
        sql = "DROP CORTEX SEARCH SERVICE IF EXISTS {0}".format(fqn)
    else:
        parts = ["CREATE OR REPLACE CORTEX SEARCH SERVICE {0}".format(fqn)]
        if module.params.get("on"):
            parts.append("ON {0}".format(module.params["on"].upper()))
        if module.params.get("warehouse_name"):
            parts.append("WAREHOUSE = {0}".format(module.params["warehouse_name"]))
        if module.params.get("target_lag"):
            parts.append("TARGET_LAG = '{0}'".format(escape_sql_string(module.params["target_lag"])))
        if module.params.get("comment"):
            parts.append("COMMENT = '{0}'".format(escape_sql_string(module.params["comment"])))
        if module.params.get("query"):
            parts.append("AS ({0})".format(module.params["query"]))
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
