#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: task_graph_info
short_description: Show Snowflake task dependency graph
description:
  - Retrieve the task dependency graph for a root task.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  root_task:
    description: Fully qualified name of the root task.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Show task graph
  stevefulme1.snowflake.task_graph_info:
    root_task: ANALYTICS_DB.PUBLIC.ROOT_TASK
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
task_graph:
  description: List of tasks in the dependency graph.
  type: list
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
        root_task=dict(type="str", required=True),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    try:
        client = SnowflakeClient(module)
        sql = "SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_DEPENDENTS(TASK_NAME => '{0}', RECURSIVE => TRUE))".format(
            escape_sql_string(module.params["root_task"].upper())
        )
        rows = client.query(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=False, task_graph=rows)


def main():
    run_module()


if __name__ == "__main__":
    main()
