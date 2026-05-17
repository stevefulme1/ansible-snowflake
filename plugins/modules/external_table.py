#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: external_table
short_description: Manage Snowflake external tables
description:
  - Create or drop an external table backed by external cloud storage.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the external table.
    type: str
    required: true
  schema_name:
    description: Schema for the table.
    type: str
    required: true
  database_name:
    description: Database for the table.
    type: str
    required: true
  columns:
    description: Column definitions with expression mappings.
    type: list
    elements: dict
  location:
    description: External stage location (e.g. @mystage/path/).
    type: str
  file_format:
    description: File format name or inline spec.
    type: str
  auto_refresh:
    description: Enable auto-refresh from cloud events.
    type: bool
    default: false
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create external table
  stevefulme1.snowflake.external_table:
    name: EXT_LOGS
    schema_name: PUBLIC
    database_name: RAW_DB
    columns:
      - name: LOG_LINE
        type: VARCHAR
        expression: "VALUE:c1::VARCHAR"
    location: "@MY_STAGE/logs/"
    file_format: CSV_FORMAT
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
        columns=dict(type="list", elements="dict"),
        location=dict(type="str"),
        file_format=dict(type="str"),
        auto_refresh=dict(type="bool", default=False),
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
        sql = "DROP EXTERNAL TABLE IF EXISTS {0}".format(fqn)
    else:
        cols = module.params.get("columns") or []
        col_defs = ", ".join(
            "{0} {1} AS ({2})".format(
                c["name"].upper(), c["type"].upper(), c.get("expression", "")
            )
            for c in cols
        )
        parts = ["CREATE EXTERNAL TABLE {0} ({1})".format(fqn, col_defs)]
        if module.params.get("location"):
            parts.append("LOCATION = {0}".format(module.params["location"]))
        if module.params.get("file_format"):
            parts.append(
                "FILE_FORMAT = (FORMAT_NAME = '{0}')".format(
                    escape_sql_string(module.params["file_format"])
                )
            )
        if module.params.get("auto_refresh"):
            parts.append("AUTO_REFRESH = TRUE")
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
