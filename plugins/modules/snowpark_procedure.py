#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: snowpark_procedure
short_description: Manage Snowflake stored procedures
description:
  - Create or drop a stored procedure (Python, Java, Scala, SQL).
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the procedure.
    type: str
    required: true
  schema_name:
    description: Schema for the procedure.
    type: str
    required: true
  database_name:
    description: Database for the procedure.
    type: str
    required: true
  arguments:
    description: Argument definitions (e.g. "x INT, y VARCHAR").
    type: str
    default: ""
  returns:
    description: Return type.
    type: str
    default: VARCHAR
  language:
    description: Handler language (PYTHON, JAVA, SCALA, SQL).
    type: str
    default: PYTHON
  runtime_version:
    description: Runtime version (e.g. "3.10" for Python).
    type: str
  handler:
    description: Handler function name.
    type: str
  packages:
    description: Required packages.
    type: list
    elements: str
  body:
    description: Inline procedure body.
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
- name: Create Python procedure
  stevefulme1.snowflake.snowpark_procedure:
    name: MY_PROC
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    arguments: "x INT"
    returns: VARCHAR
    language: PYTHON
    runtime_version: "3.10"
    handler: main
    body: |
      def main(session, x):
          return str(x * 2)
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
        arguments=dict(type="str", default=""),
        returns=dict(type="str", default="VARCHAR"),
        language=dict(type="str", default="PYTHON"),
        runtime_version=dict(type="str"),
        handler=dict(type="str"),
        packages=dict(type="list", elements="str"),
        body=dict(type="str"),
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
    args = module.params["arguments"]
    state = module.params["state"]

    if state == "absent":
        sql = "DROP PROCEDURE IF EXISTS {0}({1})".format(fqn, args)
    else:
        lang = module.params["language"].upper()
        parts = [
            "CREATE OR REPLACE PROCEDURE {0}({1})".format(fqn, args),
            "RETURNS {0}".format(module.params["returns"].upper()),
            "LANGUAGE {0}".format(lang),
        ]
        if module.params.get("runtime_version"):
            parts.append(
                "RUNTIME_VERSION = '{0}'".format(
                    escape_sql_string(module.params["runtime_version"]))
            )
        if module.params.get("packages"):
            pkg_list = ", ".join("'{0}'".format(escape_sql_string(p))
                                 for p in module.params["packages"])
            parts.append("PACKAGES = ({0})".format(pkg_list))
        if module.params.get("handler"):
            parts.append(
                "HANDLER = '{0}'".format(
                    escape_sql_string(
                        module.params["handler"])))
        if module.params.get("body"):
            parts.append("AS $$ {0} $$".format(module.params["body"]))
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
