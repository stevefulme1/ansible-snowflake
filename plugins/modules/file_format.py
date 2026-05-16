#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: file_format
short_description: Manage Snowflake file formats
description:
  - Create, alter, or drop a file format (CSV, JSON, Parquet, Avro, ORC).
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Fully qualified file format name.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  format_type:
    description: Type of file format.
    type: str
    choices: [CSV, JSON, PARQUET, AVRO, ORC]
    default: CSV
  options:
    description: >
      Dictionary of format-specific options (e.g. field_delimiter,
      skip_header, compression, strip_outer_array).
    type: dict
    default: {}
  comment:
    description: Comment for the file format.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create a CSV file format
  stevefulme1.snowflake.file_format:
    name: MYDB.PUBLIC.CSV_FMT
    format_type: CSV
    options:
      FIELD_DELIMITER: ","
      SKIP_HEADER: 1
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"

- name: Create a JSON file format
  stevefulme1.snowflake.file_format:
    name: MYDB.PUBLIC.JSON_FMT
    format_type: JSON
    options:
      STRIP_OUTER_ARRAY: "TRUE"
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
        state=dict(type="str", default="present", choices=["present", "absent"]),
        format_type=dict(
            type="str", default="CSV", choices=["CSV", "JSON", "PARQUET", "AVRO", "ORC"]
        ),
        options=dict(type="dict", default={}),
        comment=dict(type="str"),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    name = module.params["name"]
    state = module.params["state"]

    if state == "absent":
        sql = "DROP FILE FORMAT IF EXISTS {0}".format(name)
    else:
        parts = ["CREATE OR REPLACE FILE FORMAT {0}".format(name)]
        parts.append("TYPE = '{0}'".format(module.params["format_type"]))
        for key, val in module.params["options"].items():
            parts.append("{0} = '{1}'".format(key.upper(), val))
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
