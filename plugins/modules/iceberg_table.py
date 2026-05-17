#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: iceberg_table
short_description: Manage Snowflake Iceberg tables
description:
  - Create or drop an Apache Iceberg table in Snowflake.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the Iceberg table.
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
  catalog:
    description: External catalog name (e.g. SNOWFLAKE, GLUE).
    type: str
    default: SNOWFLAKE
  external_volume:
    description: External volume for data storage.
    type: str
  base_location:
    description: Base path within the external volume.
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
- name: Create an Iceberg table
  stevefulme1.snowflake.iceberg_table:
    name: ICE_EVENTS
    schema_name: PUBLIC
    database_name: LAKE_DB
    external_volume: MY_VOLUME
    base_location: events/
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
        catalog=dict(type="str", default="SNOWFLAKE"),
        external_volume=dict(type="str"),
        base_location=dict(type="str"),
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
        sql = "DROP ICEBERG TABLE IF EXISTS {0}".format(fqn)
    else:
        parts = [
            "CREATE ICEBERG TABLE IF NOT EXISTS {0}".format(fqn),
            "CATALOG = '{0}'".format(
                escape_sql_string(
                    module.params["catalog"].upper())),
        ]
        if module.params.get("external_volume"):
            parts.append(
                "EXTERNAL_VOLUME = '{0}'".format(
                    escape_sql_string(module.params["external_volume"]))
            )
        if module.params.get("base_location"):
            parts.append(
                "BASE_LOCATION = '{0}'".format(
                    escape_sql_string(
                        module.params["base_location"])))
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
