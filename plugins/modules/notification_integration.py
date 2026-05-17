#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: notification_integration
short_description: Manage Snowflake notification integrations
description:
  - Create, alter, or drop a notification integration for alerts and pipes.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the notification integration.
    type: str
    required: true
  notification_provider:
    description: Provider (e.g. AWS_SNS, AZURE_EVENT_GRID, GCP_PUBSUB).
    type: str
  enabled:
    description: Whether the integration is enabled.
    type: bool
    default: true
  direction:
    description: Direction of the notification (OUTBOUND).
    type: str
    default: OUTBOUND
  aws_sns_topic_arn:
    description: ARN for AWS SNS topic.
    type: str
  aws_sns_role_arn:
    description: ARN for the IAM role.
    type: str
  comment:
    description: Comment for the integration.
    type: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.snowflake.snowflake
"""

EXAMPLES = r"""
- name: Create SNS notification integration
  stevefulme1.snowflake.notification_integration:
    name: MY_SNS_INT
    notification_provider: AWS_SNS
    aws_sns_topic_arn: "arn:aws:sns:us-east-1:123456789:my-topic"
    aws_sns_role_arn: "arn:aws:iam::123456789:role/my-role"
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
        notification_provider=dict(type="str"),
        enabled=dict(type="bool", default=True),
        direction=dict(type="str", default="OUTBOUND"),
        aws_sns_topic_arn=dict(type="str"),
        aws_sns_role_arn=dict(type="str"),
        comment=dict(type="str"),
        state=dict(type="str", default="present", choices=["present", "absent"]),
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
        sql = "DROP NOTIFICATION INTEGRATION IF EXISTS {0}".format(name)
    else:
        provider = module.params.get("notification_provider")
        if not provider:
            module.fail_json(msg="notification_provider required when state=present")
        parts = [
            "CREATE OR REPLACE NOTIFICATION INTEGRATION {0}".format(name),
            "TYPE = QUEUE",
            "NOTIFICATION_PROVIDER = {0}".format(provider.upper()),
            "ENABLED = {0}".format(str(module.params["enabled"]).upper()),
            "DIRECTION = {0}".format(module.params["direction"].upper()),
        ]
        if module.params.get("aws_sns_topic_arn"):
            parts.append(
                "AWS_SNS_TOPIC_ARN = '{0}'".format(escape_sql_string(module.params["aws_sns_topic_arn"]))
            )
        if module.params.get("aws_sns_role_arn"):
            parts.append(
                "AWS_SNS_ROLE_ARN = '{0}'".format(escape_sql_string(module.params["aws_sns_role_arn"]))
            )
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
