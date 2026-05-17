#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: table_clone
short_description: Clone a Snowflake table
description:
  - Create a zero-copy clone of a Snowflake table.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the new cloned table.
    type: str
    required: true
  source_table:
    description: Fully qualified source table name.
    type: str
    required: true
  schema_name:
    description: Schema for the new table.
    type: str
    required: true
  database_name:
    description: Database for the new table.
    type: str
    required: true
  at_timestamp:
    description: Clone from a point in time (Time Travel).
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Clone a table
  stevefulme1.snowflake.table_clone:
    name: EVENTS_COPY
    source_table: ANALYTICS_DB.PUBLIC.EVENTS
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
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
    escape_sql_string,
)


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        source_table=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        at_timestamp=dict(type="str"),
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
    source = module.params["source_table"].upper()
    sql = "CREATE TABLE {0} CLONE {1}".format(fqn, source)
    if module.params.get("at_timestamp"):
        sql += " AT (TIMESTAMP => '{0}')".format(escape_sql_string(module.params["at_timestamp"]))

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
