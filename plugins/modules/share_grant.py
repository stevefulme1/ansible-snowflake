#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: share_grant
short_description: Grant privileges on a Snowflake share
description:
  - Grant or revoke privileges on database objects to/from a share.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  share_name:
    description: Name of the share.
    type: str
    required: true
  privilege:
    description: Privilege to grant (e.g. USAGE, SELECT).
    type: str
    required: true
  on_type:
    description: Object type (DATABASE, SCHEMA, TABLE, VIEW).
    type: str
    required: true
  on_name:
    description: Fully qualified object name.
    type: str
    required: true
  state:
    description: Whether to grant or revoke.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Grant usage on database to share
  stevefulme1.snowflake.share_grant:
    share_name: ANALYTICS_SHARE
    privilege: USAGE
    on_type: DATABASE
    on_name: ANALYTICS_DB
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

from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
)
from ansible.module_utils.basic import AnsibleModule


def run_module():
    argument_spec = dict(
        share_name=dict(type="str", required=True),
        privilege=dict(type="str", required=True),
        on_type=dict(type="str", required=True),
        on_name=dict(type="str", required=True),
        state=dict(
            type="str",
            default="present",
            choices=[
                "present",
                "absent"]),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    share = module.params["share_name"].upper()
    priv = module.params["privilege"].upper()
    on_type = module.params["on_type"].upper()
    on_name = module.params["on_name"].upper()
    state = module.params["state"]

    if state == "present":
        sql = "GRANT {0} ON {1} {2} TO SHARE {3}".format(
            priv, on_type, on_name, share)
    else:
        sql = "REVOKE {0} ON {1} {2} FROM SHARE {3}".format(
            priv, on_type, on_name, share
        )

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
