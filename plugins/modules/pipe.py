#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: pipe
short_description: Manage Snowflake pipes (Snowpipe)
description:
  - Create, alter, or drop a Snowpipe for continuous data loading.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the pipe.
    type: str
    required: true
  schema_name:
    description: Schema for the pipe.
    type: str
    required: true
  database_name:
    description: Database for the pipe.
    type: str
    required: true
  copy_statement:
    description: COPY INTO statement for the pipe.
    type: str
  auto_ingest:
    description: Enable auto-ingest from cloud storage events.
    type: bool
    default: false
  comment:
    description: Comment for the pipe.
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
- name: Create a pipe
  stevefulme1.snowflake.pipe:
    name: RAW_PIPE
    schema_name: PUBLIC
    database_name: RAW_DB
    auto_ingest: true
    copy_statement: "COPY INTO RAW_DB.PUBLIC.RAW_TABLE FROM @STAGE/"
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


def pipe_exists(client, db, schema, name):
    fqn = "{0}.{1}".format(db, schema)
    rows = client.query("SHOW PIPES LIKE '{0}' IN SCHEMA {1}".format(name, fqn))
    return len(rows) > 0


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        copy_statement=dict(type="str"),
        auto_ingest=dict(type="bool", default=False),
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
    schema = module.params["schema_name"].upper()
    db = module.params["database_name"].upper()
    state = module.params["state"]
    fqn = "{0}.{1}.{2}".format(db, schema, name)
    changed = False
    sql = ""

    try:
        client = SnowflakeClient(module)
        exists = pipe_exists(client, db, schema, name)

        if state == "absent":
            if exists:
                sql = "DROP PIPE IF EXISTS {0}".format(fqn)
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
        else:
            if not exists:
                copy = module.params.get("copy_statement")
                if not copy:
                    module.fail_json(msg="copy_statement required for new pipe")
                parts = ["CREATE PIPE {0}".format(fqn)]
                if module.params["auto_ingest"]:
                    parts.append("AUTO_INGEST = TRUE")
                if module.params.get("comment"):
                    parts.append("COMMENT = '{0}'".format(escape_sql_string(module.params["comment"])))
                parts.append("AS {0}".format(copy))
                sql = " ".join(parts)
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)

    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed, pipe=name, sql=sql)


def main():
    run_module()


if __name__ == "__main__":
    main()
