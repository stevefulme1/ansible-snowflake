#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: network_policy
short_description: Manage Snowflake network policies
description:
  - Create, alter, or drop a network policy with allowed and blocked IP lists.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the network policy.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  allowed_ip_list:
    description: List of allowed IP addresses or CIDR ranges.
    type: list
    elements: str
    default: []
  blocked_ip_list:
    description: List of blocked IP addresses or CIDR ranges.
    type: list
    elements: str
    default: []
  comment:
    description: Comment for the policy.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create a network policy
  stevefulme1.snowflake.network_policy:
    name: OFFICE_POLICY
    allowed_ip_list:
      - 203.0.113.0/24
      - 198.51.100.0/24
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
    escape_sql_string,
)
from ansible.module_utils.basic import AnsibleModule


def policy_exists(client, name):
    rows = client.query("SHOW NETWORK POLICIES LIKE '{0}'".format(escape_sql_string(name)))
    return len(rows) > 0


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        allowed_ip_list=dict(type="list", elements="str", default=[]),
        blocked_ip_list=dict(type="list", elements="str", default=[]),
        comment=dict(type="str"),
    )
    argument_spec.update(snowflake_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("private_key", "password")],
        required_one_of=[("private_key", "password")],
        supports_check_mode=True,
    )

    name = module.params["name"].upper()
    state = module.params["state"]
    allowed = ",".join("'{0}'".format(escape_sql_string(ip)) for ip in module.params["allowed_ip_list"])
    blocked = ",".join("'{0}'".format(escape_sql_string(ip)) for ip in module.params["blocked_ip_list"])
    changed = False
    sql = ""

    try:
        client = SnowflakeClient(module)
        exists = policy_exists(client, name)

        if state == "absent":
            if exists:
                sql = "DROP NETWORK POLICY IF EXISTS {0}".format(client.quote_identifier(name))
                changed = True
                if not module.check_mode:
                    client.execute_ddl(sql)
        else:
            props = []
            if allowed:
                props.append("ALLOWED_IP_LIST = ({0})".format(allowed))
            if blocked:
                props.append("BLOCKED_IP_LIST = ({0})".format(blocked))
            if module.params.get("comment"):
                props.append("COMMENT = '{0}'".format(escape_sql_string(module.params["comment"])))

            if not exists:
                sql = "CREATE NETWORK POLICY {0} {1}".format(client.quote_identifier(name), " ".join(props))
                changed = True
            else:
                sql = "ALTER NETWORK POLICY {0} SET {1}".format(client.quote_identifier(name), " ".join(props))
                changed = True

            if not module.check_mode:
                client.execute_ddl(sql)

    except SnowflakeError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed, sql=sql)


def main():
    run_module()


if __name__ == "__main__":
    main()
