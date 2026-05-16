#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: listing
short_description: Manage Snowflake Marketplace listings
description:
  - Create or alter a Snowflake Marketplace listing.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Name of the listing.
    type: str
    required: true
  share_name:
    description: Share to publish as a listing.
    type: str
  title:
    description: Display title for the listing.
    type: str
  description:
    description: Description for the listing.
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
- name: Create a listing
  stevefulme1.snowflake.listing:
    name: MY_LISTING
    share_name: ANALYTICS_SHARE
    title: Analytics Data
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
)


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        share_name=dict(type="str"),
        title=dict(type="str"),
        description=dict(type="str"),
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
        sql = "DROP LISTING IF EXISTS {0}".format(name)
    else:
        parts = ["CREATE OR REPLACE LISTING {0}".format(name)]
        if module.params.get("share_name"):
            parts.append("FOR SHARE {0}".format(module.params["share_name"].upper()))
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
