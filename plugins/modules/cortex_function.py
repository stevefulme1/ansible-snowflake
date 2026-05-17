#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: cortex_function
short_description: Manage Cortex AI functions
description:
  - Create or drop Cortex AI functions for ML inference in Snowflake.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the Cortex function.
    type: str
    required: true
  schema_name:
    description: Schema for the function.
    type: str
    required: true
  database_name:
    description: Database for the function.
    type: str
    required: true
  function_type:
    description: Type of Cortex function.
    type: str
    choices: [COMPLETE, EXTRACT_ANSWER, SENTIMENT, SUMMARIZE, TRANSLATE, CLASSIFY_TEXT]
  model:
    description: Model to use for the function (e.g. llama3.1-8b, mistral-large).
    type: str
  arguments:
    description: Function argument definitions.
    type: list
    elements: dict
  returns:
    description: Return type of the function.
    type: str
  body:
    description: Function body SQL expression.
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
- name: Create a Cortex summarize function
  stevefulme1.snowflake.cortex_function:
    name: SUMMARIZE_NOTES
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    function_type: SUMMARIZE
    model: mistral-large
    arguments:
      - name: input_text
        type: VARCHAR
    returns: VARCHAR
    body: "SELECT SNOWFLAKE.CORTEX.SUMMARIZE(input_text)"
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"

- name: Drop a Cortex function
  stevefulme1.snowflake.cortex_function:
    name: SUMMARIZE_NOTES
    schema_name: PUBLIC
    database_name: ANALYTICS_DB
    state: absent
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
)
from ansible.module_utils.basic import AnsibleModule


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
        database_name=dict(type="str", required=True),
        function_type=dict(
            type="str",
            choices=[
                "COMPLETE",
                "EXTRACT_ANSWER",
                "SENTIMENT",
                "SUMMARIZE",
                "TRANSLATE",
                "CLASSIFY_TEXT"],
        ),
        model=dict(type="str"),
        arguments=dict(type="list", elements="dict"),
        returns=dict(type="str"),
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
    state = module.params["state"]

    if state == "absent":
        # Build argument signature for DROP
        args = module.params.get("arguments") or []
        if args:
            arg_sig = ", ".join(a.get("type", "VARCHAR") for a in args)
            sql = "DROP FUNCTION IF EXISTS {0}({1})".format(fqn, arg_sig)
        else:
            sql = "DROP FUNCTION IF EXISTS {0}".format(fqn)
    else:
        body = module.params.get("body")
        if not body:
            module.fail_json(msg="body is required when state=present")
        args = module.params.get("arguments") or []
        arg_parts = []
        for a in args:
            arg_parts.append(
                "{0} {1}".format(
                    a["name"], a.get(
                        "type", "VARCHAR")))
        arg_str = ", ".join(arg_parts)
        ret = module.params.get("returns", "VARCHAR")
        parts = [
            "CREATE OR REPLACE FUNCTION {0}({1})".format(fqn, arg_str),
            "RETURNS {0}".format(ret),
            "AS $$ {0} $$".format(body),
        ]
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
