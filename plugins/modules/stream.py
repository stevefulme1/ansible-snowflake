#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: stream
short_description: Manage Snowflake streams
description:
  - Create or drop a stream for change data capture (CDC).
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the stream.
    type: str
    required: true
  schema_name:
    description: Schema for the stream.
    type: str
    required: true
  database_name:
    description: Database for the stream.
    type: str
    required: true
  source_table:
    description: Source table to track changes on.
    type: str
  append_only:
    description: Track only inserts (no deletes/updates).
    type: bool
    default: false
  show_initial_rows:
    description: Include existing rows at stream creation.
    type: bool
    default: false
  comment:
    description: Comment for the stream.
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
- name: Create a stream
  stevefulme1.snowflake.stream:
    name: EVENTS_STREAM
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    source_table: ANALYTICS_DB.PUBLIC.EVENTS
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
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        source_table=dict(type="str"),
        append_only=dict(type="bool", default=False),
        show_initial_rows=dict(type="bool", default=False),
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
        sql = "DROP STREAM IF EXISTS {0}".format(fqn)
    else:
        src = module.params.get("source_table")
        if not src:
            module.fail_json(msg="source_table required when state=present")
        parts = ["CREATE STREAM IF NOT EXISTS {0} ON TABLE {1}".format(fqn, src)]
        if module.params["append_only"]:
            parts.append("APPEND_ONLY = TRUE")
        if module.params["show_initial_rows"]:
            parts.append("SHOW_INITIAL_ROWS = TRUE")
        if module.params.get("comment"):
            parts.append("COMMENT = '{0}'".format(module.params["comment"]))
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
