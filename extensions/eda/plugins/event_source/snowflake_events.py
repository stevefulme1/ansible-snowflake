# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""EDA event source plugin that polls Snowflake ACCOUNT_USAGE views for audit events."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
name: snowflake_events
short_description: Poll Snowflake audit events for EDA
description:
  - Polls SNOWFLAKE.ACCOUNT_USAGE views (LOGIN_HISTORY, QUERY_HISTORY)
    and emits events for login failures, role changes, network policy
    violations, and warehouse credit overages.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  account:
    description: Snowflake account identifier.
    type: str
    required: true
  user:
    description: Snowflake user name.
    type: str
    required: true
  private_key:
    description: PEM private key for key-pair authentication.
    type: str
  password:
    description: Password for authentication.
    type: str
  poll_interval:
    description: Seconds between polling cycles.
    type: int
    default: 60
  event_types:
    description:
      - List of event types to emit.
    type: list
    elements: str
    default:
      - login_failure
      - role_change
      - network_policy_violation
      - warehouse_credit_exceeded
  credit_threshold:
    description: Credit threshold that triggers warehouse_credit_exceeded.
    type: float
    default: 100.0
  role:
    description: Snowflake role for the session.
    type: str
  warehouse:
    description: Snowflake warehouse for queries.
    type: str
"""

import asyncio
import json
import time
from datetime import datetime, timezone

try:
    from urllib.request import Request, urlopen
except ImportError:
    pass

try:
    import jwt as pyjwt
    import hashlib
    import base64
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.backends import default_backend
except ImportError:
    pyjwt = None


def _jwt_token(account, user, private_key_pem):
    """Generate a JWT for Snowflake key-pair authentication."""
    now = int(time.time())
    private_key_obj = load_pem_private_key(
        private_key_pem.encode("utf-8"),
        password=None,
        backend=default_backend(),
    )
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        PublicFormat,
    )

    public_key_der = private_key_obj.public_key().public_bytes(
        encoding=Encoding.DER,
        format=PublicFormat.SubjectPublicKeyInfo,
    )
    sha256_hash = hashlib.sha256(public_key_der).digest()
    fingerprint = base64.b64encode(sha256_hash).decode("utf-8")
    account_upper = account.upper()
    user_upper = user.upper()
    payload = {
        "iss": "{0}.{1}.SHA256:{2}".format(account_upper, user_upper, fingerprint),
        "sub": "{0}.{1}".format(account_upper, user_upper),
        "iat": now,
        "exp": now + 3600,
    }
    token = pyjwt.encode(payload, private_key_obj, algorithm="RS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def _password_token(account, user, password):
    """Authenticate via username/password and return session token."""
    url = "https://{0}.snowflakecomputing.com/session/v1/login-request".format(account)
    body = json.dumps(
        {
            "data": {
                "LOGIN_NAME": user,
                "PASSWORD": password,
                "ACCOUNT_NAME": account,
            }
        }
    ).encode("utf-8")
    req = Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    resp = urlopen(req)
    result = json.loads(resp.read())
    return result["data"]["token"]


def _execute_query(account, token, sql, auth_type, role=None, warehouse=None):
    """Execute a SQL query via the Snowflake SQL REST API."""
    url = "https://{0}.snowflakecomputing.com/api/v2/statements".format(account)
    body_dict = {"statement": sql, "timeout": 60}
    if role:
        body_dict["role"] = role
    if warehouse:
        body_dict["warehouse"] = warehouse
    data = json.dumps(body_dict).encode("utf-8")
    req = Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer {0}".format(token))
    token_type = "KEYPAIR_JWT" if auth_type == "keypair" else "SNOWFLAKE"
    req.add_header("X-Snowflake-Authorization-Token-Type", token_type)
    resp = urlopen(req)
    result = json.loads(resp.read())
    meta = result.get("resultSetMetaData", {})
    columns = [col["name"] for col in meta.get("rowType", [])]
    rows = result.get("data", [])
    return [dict(zip(columns, row)) for row in rows]


async def main(queue, args):
    """Poll Snowflake ACCOUNT_USAGE and emit audit events."""
    account = args["account"]
    user = args["user"]
    private_key = args.get("private_key")
    password = args.get("password")
    poll_interval = int(args.get("poll_interval", 60))
    event_types = args.get(
        "event_types",
        [
            "login_failure",
            "role_change",
            "network_policy_violation",
            "warehouse_credit_exceeded",
        ],
    )
    credit_threshold = float(args.get("credit_threshold", 100.0))
    role = args.get("role")
    warehouse = args.get("warehouse")

    if private_key:
        token = _jwt_token(account, user, private_key)
        auth_type = "keypair"
    else:
        token = _password_token(account, user, password)
        auth_type = "password"

    last_poll = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    while True:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        try:
            if "login_failure" in event_types:
                sql = (
                    "SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY"
                    " WHERE IS_SUCCESS = 'NO'"
                    " AND EVENT_TIMESTAMP >= '{0}'::TIMESTAMP_LTZ"
                    " ORDER BY EVENT_TIMESTAMP DESC LIMIT 100"
                ).format(last_poll)
                rows = _execute_query(account, token, sql, auth_type, role, warehouse)
                for row in rows:
                    await queue.put({"type": "login_failure", "data": row})

            if "role_change" in event_types:
                sql = (
                    "SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY"
                    " WHERE QUERY_TEXT ILIKE '%GRANT ROLE%'"
                    " AND START_TIME >= '{0}'::TIMESTAMP_LTZ"
                    " ORDER BY START_TIME DESC LIMIT 100"
                ).format(last_poll)
                rows = _execute_query(account, token, sql, auth_type, role, warehouse)
                for row in rows:
                    await queue.put({"type": "role_change", "data": row})

            if "network_policy_violation" in event_types:
                sql = (
                    "SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY"
                    " WHERE ERROR_CODE = 390318"
                    " AND EVENT_TIMESTAMP >= '{0}'::TIMESTAMP_LTZ"
                    " ORDER BY EVENT_TIMESTAMP DESC LIMIT 100"
                ).format(last_poll)
                rows = _execute_query(account, token, sql, auth_type, role, warehouse)
                for row in rows:
                    await queue.put({"type": "network_policy_violation", "data": row})

            if "warehouse_credit_exceeded" in event_types:
                sql = (
                    "SELECT WAREHOUSE_NAME, SUM(CREDITS_USED) AS TOTAL_CREDITS"
                    " FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY"
                    " WHERE START_TIME >= '{0}'::TIMESTAMP_LTZ"
                    " GROUP BY WAREHOUSE_NAME"
                    " HAVING SUM(CREDITS_USED) > {1}"
                ).format(last_poll, credit_threshold)
                rows = _execute_query(account, token, sql, auth_type, role, warehouse)
                for row in rows:
                    await queue.put({"type": "warehouse_credit_exceeded", "data": row})

        except Exception as exc:
            await queue.put({"type": "error", "data": {"message": str(exc)}})

        last_poll = now
        await asyncio.sleep(poll_interval)


if __name__ == "__main__":

    class _MockQueue:
        async def put(self, item):
            print(json.dumps(item))

    asyncio.run(
        main(
            _MockQueue(),
            {"account": "test", "user": "test", "password": "test"},
        )
    )
