#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
)
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type
DOCUMENTATION = r"""
---
module: result_cache
short_description: Manage Snowflake result caching
description:
  - Enable or disable persisted query result caching at account level.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  enabled:
    description: Whether result caching is enabled.
    type: bool
    default: true
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Enable result cache
  stevefulme1.snowflake.result_cache:
    enabled: true
    account: myaccount
    user: myuser
    private_key: "{{ private_key }}"
"""

RETURN = r"""
sql:
  description: The SQL statement executed.
  type: str
  returned: always
"""


def run_module():
    argument_spec = dict(
        enabled=dict(type="bool", default=True),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    val = str(module.params["enabled"]).upper()
    sql = "ALTER ACCOUNT SET USE_CACHED_RESULT = {0}".format(val)

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
