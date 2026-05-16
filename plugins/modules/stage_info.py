#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: stage_info
short_description: List Snowflake stages
description:
  - Retrieve stages using SHOW STAGES.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  database:
    description: Database to list stages in.
    type: str
  schema_name:
    description: Schema to list stages in.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
'''

EXAMPLES = r'''
- name: List stages
  stevefulme1.snowflake.stage_info:
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
'''

RETURN = r'''
stages:
  description: List of stage records.
  type: list
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient, SnowflakeError, snowflake_argument_spec,
)


def run_module():
    argument_spec = dict(
        database=dict(type='str'),
        schema_name=dict(type='str'),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[('private_key', 'password')],
        required_one_of=[('private_key', 'password')],
        supports_check_mode=True,
    )

    try:
        client = SnowflakeClient(module)
        sql = "SHOW STAGES"
        if module.params.get('database') and module.params.get('schema_name'):
            sql += " IN SCHEMA {0}.{1}".format(
                client.quote_identifier(module.params['database'].upper()),
                client.quote_identifier(module.params['schema_name'].upper()))
        elif module.params.get('database'):
            sql += " IN DATABASE {0}".format(
                client.quote_identifier(module.params['database'].upper()))
        rows = client.query(sql)
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=False, stages=rows)


def main():
    run_module()


if __name__ == '__main__':
    main()
