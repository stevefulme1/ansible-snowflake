#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: authentication_policy
short_description: Manage Snowflake authentication policies
description:
  - Create, alter, or drop an authentication policy.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the authentication policy.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  authentication_methods:
    description: Allowed authentication methods.
    type: list
    elements: str
  mfa_authentication_methods:
    description: MFA methods for the policy.
    type: list
    elements: str
  client_types:
    description: Allowed client types.
    type: list
    elements: str
  security_integrations:
    description: Security integrations allowed.
    type: list
    elements: str
  comment:
    description: Comment for the policy.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create authentication policy
  stevefulme1.snowflake.authentication_policy:
    name: MFA_REQUIRED
    authentication_methods: [PASSWORD]
    mfa_authentication_methods: [TOTP]
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


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        authentication_methods=dict(type="list", elements="str"),
        mfa_authentication_methods=dict(type="list", elements="str"),
        client_types=dict(type="list", elements="str"),
        security_integrations=dict(type="list", elements="str"),
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
    changed = False
    sql = ""

    props = []
    if module.params.get("authentication_methods"):
        vals = ",".join("'{0}'".format(escape_sql_string(m)) for m in module.params["authentication_methods"])
        props.append("AUTHENTICATION_METHODS = ({0})".format(vals))
    if module.params.get("mfa_authentication_methods"):
        vals = ",".join("'{0}'".format(escape_sql_string(m)) for m in module.params["mfa_authentication_methods"])
        props.append("MFA_AUTHENTICATION_METHODS = ({0})".format(vals))
    if module.params.get("client_types"):
        vals = ",".join("'{0}'".format(escape_sql_string(c)) for c in module.params["client_types"])
        props.append("CLIENT_TYPES = ({0})".format(vals))
    if module.params.get("security_integrations"):
        vals = ",".join("'{0}'".format(escape_sql_string(s)) for s in module.params["security_integrations"])
        props.append("SECURITY_INTEGRATIONS = ({0})".format(vals))
    if module.params.get("comment"):
        props.append("COMMENT = '{0}'".format(escape_sql_string(module.params["comment"])))

    try:
        client = SnowflakeClient(module)
        if state == "absent":
            sql = "DROP AUTHENTICATION POLICY IF EXISTS {0}".format(client.quote_identifier(name))
            changed = True
        else:
            sql = "CREATE OR REPLACE AUTHENTICATION POLICY {0} {1}".format(
                client.quote_identifier(name), " ".join(props)
            )
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
