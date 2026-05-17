#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
)

__metaclass__ = type

DOCUMENTATION = r"""
---
module: warehouse_resume
short_description: Resume a suspended Snowflake warehouse
description:
  - Resume a suspended warehouse using ALTER WAREHOUSE RESUME.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the warehouse to resume.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Resume the analytics warehouse
  stevefulme1.snowflake.warehouse_resume:
    name: ANALYTICS_WH
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""

from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
from ansible.module_utils.basic import AnsibleModule
sql:
  description: The SQL statement executed.
  type: str
  returned: always
"""


def run_module():
    argument_spec = dict(name=dict(type="str", required=True))
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    name = module.params["name"].upper()
    sql = "ALTER WAREHOUSE {0} RESUME".format(
        SnowflakeClient.quote_identifier(name))

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
