#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: tag_association
short_description: Set or unset a tag on a Snowflake object
description:
  - Associate a tag value with a table, column, warehouse, or other object.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  object_type:
    description: Type of object to tag.
    type: str
    required: true
    choices: [TABLE, VIEW, COLUMN, DATABASE, SCHEMA, WAREHOUSE, USER, ROLE]
  object_name:
    description: Fully qualified name of the object.
    type: str
    required: true
  tag_name:
    description: Fully qualified tag name.
    type: str
    required: true
  tag_value:
    description: Value to set. Required when I(state=present).
    type: str
  state:
    description: Whether to set or unset the tag.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
'''

EXAMPLES = r'''
- name: Tag a table
  stevefulme1.snowflake.tag_association:
    object_type: TABLE
    object_name: MYDB.PUBLIC.CUSTOMERS
    tag_name: MYDB.GOVERNANCE.COST_CENTER
    tag_value: ENGINEERING
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
        object_type=dict(type='str', required=True,
                         choices=['TABLE', 'VIEW', 'COLUMN', 'DATABASE', 'SCHEMA',
                                  'WAREHOUSE', 'USER', 'ROLE']),
        object_name=dict(type='str', required=True),
        tag_name=dict(type='str', required=True),
        tag_value=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[('private_key', 'password')],
        required_one_of=[('private_key', 'password')],
        supports_check_mode=True,
    )

    obj_type = module.params['object_type']
    obj_name = module.params['object_name']
    tag_name = module.params['tag_name']
    tag_value = module.params.get('tag_value', '')
    state = module.params['state']

    if state == 'present':
        sql = "ALTER {0} {1} SET TAG {2} = '{3}'".format(obj_type, obj_name, tag_name, tag_value)
    else:
        sql = "ALTER {0} {1} UNSET TAG {2}".format(obj_type, obj_name, tag_name)

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
