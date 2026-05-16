#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: warehouse_resize
short_description: Resize a Snowflake warehouse
description:
  - Change the size of a warehouse using ALTER WAREHOUSE SET WAREHOUSE_SIZE.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the warehouse.
    type: str
    required: true
  size:
    description: New warehouse size.
    type: str
    required: true
    choices: [XSMALL, SMALL, MEDIUM, LARGE, XLARGE, XXLARGE, XXXLARGE, X4LARGE, X5LARGE, X6LARGE]
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
'''

EXAMPLES = r'''
- name: Resize warehouse to LARGE
  stevefulme1.snowflake.warehouse_resize:
    name: ANALYTICS_WH
    size: LARGE
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
'''

RETURN = r'''
sql:
  description: The SQL statement executed.
  type: str
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient, SnowflakeError, snowflake_argument_spec,
)


def run_module():
    argument_spec = dict(
        name=dict(type='str', required=True),
        size=dict(type='str', required=True,
                  choices=['XSMALL', 'SMALL', 'MEDIUM', 'LARGE', 'XLARGE',
                           'XXLARGE', 'XXXLARGE', 'X4LARGE', 'X5LARGE', 'X6LARGE']),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[('private_key', 'password')],
        required_one_of=[('private_key', 'password')],
        supports_check_mode=True,
    )

    name = module.params['name'].upper()
    size = module.params['size']
    sql = "ALTER WAREHOUSE {0} SET WAREHOUSE_SIZE = '{1}'".format(
        SnowflakeClient.quote_identifier(name), size)

    try:
        client = SnowflakeClient(module)
        if not module.check_mode:
            client.execute_ddl(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=True, sql=sql)


def main():
    run_module()


if __name__ == '__main__':
    main()
