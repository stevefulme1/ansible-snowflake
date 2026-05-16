#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: data_classification
short_description: Run Snowflake data classification
description:
  - Call ASSOCIATE_SEMANTIC_CATEGORY_TAGS to auto-classify columns.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  table:
    description: Fully qualified table name to classify.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Classify a table
  stevefulme1.snowflake.data_classification:
    table: MYDB.PUBLIC.CUSTOMERS
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
sql:
  description: The SQL statement executed.
  type: str
  returned: always
result:
  description: Classification result from Snowflake.
  type: list
  returned: success
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
)


def run_module():
    argument_spec = dict(
        table=dict(type="str", required=True),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    table = module.params["table"]
    sql = "CALL ASSOCIATE_SEMANTIC_CATEGORY_TAGS('{0}', EXTRACT_SEMANTIC_CATEGORIES('{0}'))".format(
        table
    )

    result = []
    try:
        client = SnowflakeClient(module)
        if not module.check_mode:
            result = client.query(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=True, sql=sql, result=result)


def main():
    run_module()


if __name__ == "__main__":
    main()
