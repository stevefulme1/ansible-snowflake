#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: storage_integration
short_description: Manage Snowflake storage integrations
description:
  - Create, alter, or drop a storage integration for S3, GCS, or Azure Blob.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the storage integration.
    type: str
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  storage_provider:
    description: Cloud storage provider.
    type: str
    choices: [S3, GCS, AZURE]
  storage_allowed_locations:
    description: List of allowed cloud storage locations.
    type: list
    elements: str
  storage_blocked_locations:
    description: List of blocked cloud storage locations.
    type: list
    elements: str
  storage_aws_role_arn:
    description: AWS IAM role ARN (S3 only).
    type: str
  azure_tenant_id:
    description: Azure tenant ID (Azure only).
    type: str
  enabled:
    description: Whether the integration is enabled.
    type: bool
    default: true
  comment:
    description: Comment for the integration.
    type: str
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create S3 storage integration
  stevefulme1.snowflake.storage_integration:
    name: S3_INT
    storage_provider: S3
    storage_allowed_locations:
      - s3://mybucket/path/
    storage_aws_role_arn: "arn:aws:iam::123456789012:role/myrole"
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
        storage_provider=dict(type="str", choices=["S3", "GCS", "AZURE"]),
        storage_allowed_locations=dict(type="list", elements="str"),
        storage_blocked_locations=dict(type="list", elements="str"),
        storage_aws_role_arn=dict(type="str"),
        azure_tenant_id=dict(type="str"),
        enabled=dict(type="bool", default=True),
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

    if state == "absent":
        sql = "DROP STORAGE INTEGRATION IF EXISTS {0}".format(
            SnowflakeClient.quote_identifier(name)
        )
    else:
        parts = [
            "CREATE OR REPLACE STORAGE INTEGRATION {0}".format(
                SnowflakeClient.quote_identifier(name)
            )
        ]
        parts.append("TYPE = EXTERNAL_STAGE")
        if module.params.get("storage_provider"):
            parts.append(
                "STORAGE_PROVIDER = '{0}'".format(escape_sql_string(module.params["storage_provider"]))
            )
        if module.params.get("storage_allowed_locations"):
            locs = ", ".join(
                "'{0}'".format(escape_sql_string(loc))
                for loc in module.params["storage_allowed_locations"]
            )
            parts.append("STORAGE_ALLOWED_LOCATIONS = ({0})".format(locs))
        if module.params.get("storage_blocked_locations"):
            locs = ", ".join(
                "'{0}'".format(escape_sql_string(loc))
                for loc in module.params["storage_blocked_locations"]
            )
            parts.append("STORAGE_BLOCKED_LOCATIONS = ({0})".format(locs))
        if module.params.get("storage_aws_role_arn"):
            parts.append(
                "STORAGE_AWS_ROLE_ARN = '{0}'".format(
                    escape_sql_string(module.params["storage_aws_role_arn"])
                )
            )
        if module.params.get("azure_tenant_id"):
            parts.append(
                "AZURE_TENANT_ID = '{0}'".format(escape_sql_string(module.params["azure_tenant_id"]))
            )
        parts.append("ENABLED = {0}".format(str(module.params["enabled"]).upper()))
        if module.params.get("comment"):
            parts.append("COMMENT = '{0}'".format(escape_sql_string(module.params["comment"])))
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
