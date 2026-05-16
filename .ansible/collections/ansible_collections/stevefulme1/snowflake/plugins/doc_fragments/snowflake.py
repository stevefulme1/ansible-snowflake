# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  account:
    description:
      - The Snowflake account identifier (e.g. C(xy12345) or C(myorg-myaccount)).
      - Can also be set via the C(SNOWFLAKE_ACCOUNT) environment variable.
    type: str
    required: true
  user:
    description:
      - The Snowflake user name for authentication.
      - Can also be set via the C(SNOWFLAKE_USER) environment variable.
    type: str
    required: true
  private_key:
    description:
      - PEM-encoded private key for key-pair authentication.
      - Mutually exclusive with I(password).
      - Can also be set via the C(SNOWFLAKE_PRIVATE_KEY) environment variable.
    type: str
  password:
    description:
      - Password for username/password authentication.
      - Mutually exclusive with I(private_key).
      - Can also be set via the C(SNOWFLAKE_PASSWORD) environment variable.
    type: str
  role:
    description:
      - The Snowflake role to use for the session.
      - Can also be set via the C(SNOWFLAKE_ROLE) environment variable.
    type: str
  warehouse:
    description:
      - The Snowflake warehouse to use for the session.
      - Can also be set via the C(SNOWFLAKE_WAREHOUSE) environment variable.
    type: str
  database:
    description:
      - The default database for the session.
      - Can also be set via the C(SNOWFLAKE_DATABASE) environment variable.
    type: str
  schema:
    description:
      - The default schema for the session.
      - Can also be set via the C(SNOWFLAKE_SCHEMA) environment variable.
    type: str
  validate_certs:
    description:
      - Whether to validate SSL certificates.
    type: bool
    default: true
requirements:
  - python >= 3.10
  - PyJWT (for key-pair authentication)
  - cryptography (for key-pair authentication)
notes:
  - Authentication requires either I(private_key) or I(password).
  - All operations use the Snowflake SQL REST API at C(/api/v2/statements).
"""
