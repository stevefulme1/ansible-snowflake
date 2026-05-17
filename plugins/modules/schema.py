#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: schema
short_description: Manage Snowflake schemas
description:
  - Create, alter, or drop a Snowflake schema.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the schema.
    type: str
    required: true
  database:
    description: Database the schema belongs to. Overrides the session default.
    type: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  transient:
    description: Create as a transient schema.
    type: bool
    default: false
  data_retention_time_in_days:
    description: Time Travel retention period in days.
    type: int
  comment:
    description: Comment for the schema.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create a schema
  stevefulme1.snowflake.schema:
    name: RAW
    database: ANALYTICS_DB
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
schema:
  description: Name of the schema managed.
  type: str
  returned: always
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


def schema_exists(client, db, name):
    sql = "SHOW SCHEMAS LIKE '{0}'".format(escape_sql_string(name))
    if db:
        sql += " IN DATABASE {0}".format(client.quote_identifier(db))
    rows = client.query(sql)
    return len(rows) > 0


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        database=dict(type="str"),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        transient=dict(type="bool", default=False),
        data_retention_time_in_days=dict(type="int"),
        comment=dict(type="str"),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    name = module.params["name"].upper()
    db = module.params.get("database", "").upper() if module.params.get("database") else None
    state = module.params["state"]
    changed = False
    sql = ""

    fqn = "{0}.{1}".format(client_quote(db), client_quote(name)) if db else client_quote(name)

    try:
        client = SnowflakeClient(module)
        fqn = (
            "{0}.{1}".format(client.quote_identifier(db), client.quote_identifier(name))
            if db
            else client.quote_identifier(name)
        )
        exists = schema_exists(client, db, name)

        if state == "absent":
            if exists:
                sql = "DROP SCHEMA IF EXISTS {0}".format(fqn)
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
        else:
            if not exists:
                kind = "TRANSIENT SCHEMA" if module.params["transient"] else "SCHEMA"
                parts = ["CREATE {0} IF NOT EXISTS {1}".format(kind, fqn)]
                if module.params.get("data_retention_time_in_days") is not None:
                    parts.append(
                        "DATA_RETENTION_TIME_IN_DAYS = {0}".format(module.params["data_retention_time_in_days"])
                    )
                if module.params.get("comment"):
                    parts.append("COMMENT = '{0}'".format(escape_sql_string(module.params["comment"])))
                sql = " ".join(parts)
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
            else:
                alterations = []
                if module.params.get("data_retention_time_in_days") is not None:
                    alterations.append(
                        "DATA_RETENTION_TIME_IN_DAYS = {0}".format(module.params["data_retention_time_in_days"])
                    )
                if module.params.get("comment"):
                    alterations.append("COMMENT = '{0}'".format(escape_sql_string(module.params["comment"])))
                if alterations:
                    sql = "ALTER SCHEMA {0} SET {1}".format(fqn, " ".join(alterations))
                    changed = True
                    if not module.check_mode:
                        client.execute_ddl(sql)

    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed, schema=name, sql=sql)


def client_quote(n):
    return '"{0}"'.format(n.replace('"', '""'))


def main():
    run_module()


if __name__ == "__main__":
    main()
