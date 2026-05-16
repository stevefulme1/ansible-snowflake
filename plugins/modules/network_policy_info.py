#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: network_policy_info
short_description: List Snowflake network policies
description:
  - Retrieve network policies using SHOW NETWORK POLICIES.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
'''

EXAMPLES = r'''
- name: List network policies
  stevefulme1.snowflake.network_policy_info:
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
'''

RETURN = r'''
network_policies:
  description: List of network policy records.
  type: list
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient, SnowflakeError, snowflake_argument_spec,
)


def run_module():
    argument_spec = dict()
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[('private_key', 'password')],
        required_one_of=[('private_key', 'password')],
        supports_check_mode=True,
    )

    try:
        client = SnowflakeClient(module)
        rows = client.query("SHOW NETWORK POLICIES")
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=False, network_policies=rows)


def main():
    run_module()


if __name__ == '__main__':
    main()
