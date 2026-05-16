#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: masking_policy_attachment
short_description: Attach a masking policy to a column
description:
  - Set or unset a masking policy on a table column.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  table:
    description: Fully qualified table name.
    type: str
    required: true
  column:
    description: Column name.
    type: str
    required: true
  policy:
    description: Fully qualified masking policy name.
    type: str
    required: true
  state:
    description: Whether to set or unset.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
'''

EXAMPLES = r'''
- name: Attach masking policy to column
  stevefulme1.snowflake.masking_policy_attachment:
    table: MYDB.PUBLIC.CUSTOMERS
    column: EMAIL
    policy: MYDB.GOVERNANCE.EMAIL_MASK
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
        table=dict(type='str', required=True),
        column=dict(type='str', required=True),
        policy=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[('private_key', 'password')],
        required_one_of=[('private_key', 'password')],
        supports_check_mode=True,
    )

    table = module.params['table']
    column = module.params['column'].upper()
    policy = module.params['policy']
    state = module.params['state']

    if state == 'present':
        sql = 'ALTER TABLE {0} MODIFY COLUMN {1} SET MASKING POLICY {2}'.format(
            table, column, policy)
    else:
        sql = 'ALTER TABLE {0} MODIFY COLUMN {1} UNSET MASKING POLICY'.format(table, column)

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
