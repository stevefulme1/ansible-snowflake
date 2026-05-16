#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: storage_integration_info
short_description: List Snowflake storage integrations
description:
  - Retrieve storage integrations using SHOW or DESCRIBE INTEGRATION.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Specific integration to describe. If omitted, lists all.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: List storage integrations
  stevefulme1.snowflake.storage_integration_info:
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
integrations:
  description: List of integration records.
  type: list
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
)


def run_module():
    argument_spec = dict(name=dict(type="str"))
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    try:
        client = SnowflakeClient(module)
        if module.params.get("name"):
            rows = client.query(
                "DESCRIBE INTEGRATION {0}".format(
                    client.quote_identifier(module.params["name"].upper())
                )
            )
        else:
            rows = client.query("SHOW STORAGE INTEGRATIONS")
    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=False, integrations=rows)


def main():
    run_module()


if __name__ == "__main__":
    main()
