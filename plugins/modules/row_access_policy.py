#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: row_access_policy
short_description: Manage Snowflake row access policies
description:
  - Create, alter, or drop a row access policy.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Fully qualified name of the row access policy.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  signature:
    description: Input signature (e.g. C((region STRING, account_id NUMBER))).
    type: str
  returns:
    description: Must be C(BOOLEAN).
    type: str
    default: BOOLEAN
  body:
    description: Policy expression body returning BOOLEAN.
    type: str
  comment:
    description: Comment for the policy.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
'''

EXAMPLES = r'''
- name: Create row access policy
  stevefulme1.snowflake.row_access_policy:
    name: MYDB.GOVERNANCE.REGION_FILTER
    signature: "(region STRING)"
    body: "CURRENT_ROLE() = 'ADMIN' OR region = CURRENT_REGION()"
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
        state=dict(type='str', default='present', choices=['present', 'absent']),
        signature=dict(type='str'),
        returns=dict(type='str', default='BOOLEAN'),
        body=dict(type='str'),
        comment=dict(type='str'),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[('private_key', 'password')],
        required_one_of=[('private_key', 'password')],
        required_if=[('state', 'present', ('signature', 'body'))],
        supports_check_mode=True,
    )

    name = module.params['name']
    state = module.params['state']

    if state == 'absent':
        sql = 'DROP ROW ACCESS POLICY IF EXISTS {0}'.format(name)
    else:
        parts = ['CREATE OR REPLACE ROW ACCESS POLICY {0}'.format(name)]
        parts.append('AS {0}'.format(module.params['signature']))
        parts.append('RETURNS {0} ->'.format(module.params['returns']))
        parts.append(module.params['body'])
        sql = ' '.join(parts)

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
