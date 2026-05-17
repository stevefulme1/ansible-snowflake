#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: saml_integration
short_description: Manage Snowflake SAML2 security integrations
description:
  - Create, alter, or drop a SAML2 security integration for SSO.
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
  saml2_issuer:
    description: SAML2 IdP issuer URL.
    type: str
  saml2_sso_url:
    description: SAML2 SSO endpoint URL.
    type: str
  saml2_provider:
    description: SAML2 provider name.
    type: str
    choices: [CUSTOM, OKTA, ADFS]
    default: CUSTOM
  saml2_x509_cert:
    description: Base64-encoded X.509 certificate from the IdP.
    type: str
  enabled:
    description: Whether the integration is enabled.
    type: bool
    default: true
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create SAML integration
  stevefulme1.snowflake.saml_integration:
    name: OKTA_SSO
    saml2_issuer: "http://www.okta.com/exk..."
    saml2_sso_url: "https://myorg.okta.com/app/.../sso/saml"
    saml2_provider: OKTA
    saml2_x509_cert: "{{ okta_cert }}"
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
        saml2_issuer=dict(type="str"),
        saml2_sso_url=dict(type="str"),
        saml2_provider=dict(type="str", default="CUSTOM", choices=["CUSTOM", "OKTA", "ADFS"]),
        saml2_x509_cert=dict(type="str", no_log=True),
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
        sql = "DROP SECURITY INTEGRATION IF EXISTS {0}".format(SnowflakeClient.quote_identifier(name))
    else:
        parts = ["CREATE OR REPLACE SECURITY INTEGRATION {0}".format(SnowflakeClient.quote_identifier(name))]
        parts.append("TYPE = SAML2")
        parts.append("ENABLED = {0}".format(str(module.params["enabled"]).upper()))
        if module.params.get("saml2_issuer"):
            parts.append("SAML2_ISSUER = '{0}'".format(escape_sql_string(module.params["saml2_issuer"])))
        if module.params.get("saml2_sso_url"):
            parts.append("SAML2_SSO_URL = '{0}'".format(escape_sql_string(module.params["saml2_sso_url"])))
        parts.append("SAML2_PROVIDER = '{0}'".format(escape_sql_string(module.params["saml2_provider"])))
        if module.params.get("saml2_x509_cert"):
            parts.append("SAML2_X509_CERT = '{0}'".format(escape_sql_string(module.params["saml2_x509_cert"])))
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
