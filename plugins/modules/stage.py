#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: stage
short_description: Manage Snowflake stages
description:
  - Create, alter, or drop an internal or external stage.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Fully qualified stage name.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  stage_type:
    description: Type of stage.
    type: str
    choices: [internal, external]
    default: internal
  url:
    description: External stage URL (e.g. C(s3://bucket/path/)).
    type: str
  storage_integration:
    description: Storage integration name for external stages.
    type: str
  file_format:
    description: File format name or inline specification.
    type: str
  copy_options:
    description: Copy options string.
    type: str
  comment:
    description: Comment for the stage.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
'''

EXAMPLES = r'''
- name: Create an internal stage
  stevefulme1.snowflake.stage:
    name: MYDB.PUBLIC.MY_STAGE
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"

- name: Create an external S3 stage
  stevefulme1.snowflake.stage:
    name: MYDB.PUBLIC.S3_STAGE
    stage_type: external
    url: "s3://mybucket/data/"
    storage_integration: S3_INT
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
        stage_type=dict(type='str', default='internal', choices=['internal', 'external']),
        url=dict(type='str'),
        storage_integration=dict(type='str'),
        file_format=dict(type='str'),
        copy_options=dict(type='str'),
        comment=dict(type='str'),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[('private_key', 'password')],
        required_one_of=[('private_key', 'password')],
        supports_check_mode=True,
    )

    name = module.params['name']
    state = module.params['state']

    if state == 'absent':
        sql = 'DROP STAGE IF EXISTS {0}'.format(name)
    else:
        parts = ['CREATE OR REPLACE STAGE {0}'.format(name)]
        if module.params['stage_type'] == 'external' and module.params.get('url'):
            parts.append("URL = '{0}'".format(module.params['url']))
        if module.params.get('storage_integration'):
            parts.append('STORAGE_INTEGRATION = {0}'.format(module.params['storage_integration']))
        if module.params.get('file_format'):
            parts.append('FILE_FORMAT = ({0})'.format(module.params['file_format']))
        if module.params.get('copy_options'):
            parts.append('COPY_OPTIONS = ({0})'.format(module.params['copy_options']))
        if module.params.get('comment'):
            parts.append("COMMENT = '{0}'".format(module.params['comment']))
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
