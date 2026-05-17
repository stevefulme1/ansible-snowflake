#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: scim_integration
short_description: Manage Snowflake SCIM security integrations
description:
  - Create, alter, or drop a SCIM security integration for user provisioning.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the integration.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  scim_client:
    description: SCIM client type.
    type: str
    choices: [OKTA, AZURE, GENERIC]
    default: GENERIC
  run_as_role:
    description: Role used by the SCIM client to provision.
    type: str
    default: GENERIC_SCIM_PROVISIONER
  enabled:
    description: Whether the integration is enabled.
    type: bool
    default: true
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create SCIM integration
  stevefulme1.snowflake.scim_integration:
    name: OKTA_SCIM
    scim_client: OKTA
    run_as_role: OKTA_PROVISIONER
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
        name=dict(type="str", required=True),
        state=dict(
            type="str",
            default="present",
            choices=[
                "present",
                "absent"]),
        scim_client=dict(
            type="str", default="GENERIC", choices=["OKTA", "AZURE", "GENERIC"]
        ),
        run_as_role=dict(type="str", default="GENERIC_SCIM_PROVISIONER"),
        enabled=dict(type="bool", default=True),
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

    if state == "absent":
        sql = "DROP SECURITY INTEGRATION IF EXISTS {0}".format(
            SnowflakeClient.quote_identifier(name)
        )
    else:
        sql = (
            "CREATE OR REPLACE SECURITY INTEGRATION {0} "
            "TYPE = SCIM "
            "SCIM_CLIENT = '{1}' "
            "RUN_AS_ROLE = '{2}' "
            "ENABLED = {3}"
        ).format(
            SnowflakeClient.quote_identifier(name),
            module.params["scim_client"],
            module.params["run_as_role"],
            str(module.params["enabled"]).upper(),
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
