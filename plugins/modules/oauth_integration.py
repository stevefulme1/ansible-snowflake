#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oauth_integration
short_description: Manage Snowflake OAuth security integrations
description:
  - Create, alter, or drop an OAuth security integration.
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
  oauth_client:
    description: OAuth client type.
    type: str
    choices: [CUSTOM, LOOKER, TABLEAU_DESKTOP, TABLEAU_SERVER]
    default: CUSTOM
  oauth_client_type:
    description: OAuth client type for custom integrations.
    type: str
    choices: [PUBLIC, CONFIDENTIAL]
    default: CONFIDENTIAL
  oauth_redirect_uri:
    description: OAuth redirect URI.
    type: str
  oauth_issue_refresh_tokens:
    description: Whether to issue refresh tokens.
    type: bool
    default: true
  oauth_refresh_token_validity:
    description: Refresh token validity in seconds.
    type: int
    default: 7776000
  enabled:
    description: Whether the integration is enabled.
    type: bool
    default: true
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create custom OAuth integration
  stevefulme1.snowflake.oauth_integration:
    name: MY_OAUTH_APP
    oauth_client: CUSTOM
    oauth_client_type: CONFIDENTIAL
    oauth_redirect_uri: "https://myapp.example.com/callback"
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.snowflake.plugins.module_utils.snowflake_client import (
    SnowflakeClient,
    SnowflakeError,
    snowflake_argument_spec,
    escape_sql_string,
)


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        oauth_client=dict(
            type="str",
            default="CUSTOM",
            choices=["CUSTOM", "LOOKER", "TABLEAU_DESKTOP", "TABLEAU_SERVER"],
        ),
        oauth_client_type=dict(
            type="str", default="CONFIDENTIAL", choices=["PUBLIC", "CONFIDENTIAL"]
        ),
        oauth_redirect_uri=dict(type="str"),
        oauth_issue_refresh_tokens=dict(type="bool", default=True),
        oauth_refresh_token_validity=dict(type="int", default=7776000, no_log=False),
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
        parts = [
            "CREATE OR REPLACE SECURITY INTEGRATION {0}".format(
                SnowflakeClient.quote_identifier(name)
            )
        ]
        parts.append("TYPE = OAUTH")
        parts.append("OAUTH_CLIENT = '{0}'".format(escape_sql_string(module.params["oauth_client"])))
        if module.params["oauth_client"] == "CUSTOM":
            parts.append(
                "OAUTH_CLIENT_TYPE = '{0}'".format(escape_sql_string(module.params["oauth_client_type"]))
            )
        if module.params.get("oauth_redirect_uri"):
            parts.append(
                "OAUTH_REDIRECT_URI = '{0}'".format(escape_sql_string(module.params["oauth_redirect_uri"]))
            )
        parts.append(
            "OAUTH_ISSUE_REFRESH_TOKENS = {0}".format(
                str(module.params["oauth_issue_refresh_tokens"]).upper()
            )
        )
        parts.append(
            "OAUTH_REFRESH_TOKEN_VALIDITY = {0}".format(
                module.params["oauth_refresh_token_validity"]
            )
        )
        parts.append("ENABLED = {0}".format(str(module.params["enabled"]).upper()))
        sql = " ".join(parts)

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
