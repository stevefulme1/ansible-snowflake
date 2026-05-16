# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Snowflake SQL REST API client for Ansible modules."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import time

from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError


class SnowflakeError(Exception):
    """Exception raised for Snowflake API errors."""

    def __init__(self, message, code=None, sql_state=None):
        super(SnowflakeError, self).__init__(message)
        self.code = code
        self.sql_state = sql_state


snowflake_argument_spec = dict(
    account=dict(type='str', required=True),
    user=dict(type='str', required=True),
    private_key=dict(type='str', no_log=True),
    password=dict(type='str', no_log=True),
    role=dict(type='str'),
    warehouse=dict(type='str'),
    database=dict(type='str'),
    schema=dict(type='str'),
    validate_certs=dict(type='bool', default=True),
)


class SnowflakeClient(object):
    """Client for the Snowflake SQL REST API.

    Executes SQL statements via POST /api/v2/statements and handles
    asynchronous query polling.
    """

    POLL_INTERVAL = 2
    MAX_POLL_SECONDS = 300

    def __init__(self, module):
        self.module = module
        self.account = module.params['account']
        self.user = module.params['user']
        self.private_key = module.params.get('private_key')
        self.password = module.params.get('password')
        self.role = module.params.get('role')
        self.warehouse = module.params.get('warehouse')
        self.database = module.params.get('database')
        self.schema = module.params.get('schema')
        self.validate_certs = module.params.get('validate_certs', True)

        self.base_url = 'https://{0}.snowflakecomputing.com'.format(self.account)
        self.api_url = '{0}/api/v2/statements'.format(self.base_url)

        if not self.private_key and not self.password:
            module.fail_json(msg='Either private_key or password is required for authentication.')

        self._token = self._authenticate()

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _authenticate(self):
        """Obtain a session token via key-pair JWT or username/password.

        For key-pair auth the caller supplies a PEM private key and we
        generate a JWT.  For password auth we call the session token
        endpoint.
        """
        if self.private_key:
            return self._jwt_token()
        return self._password_token()

    def _jwt_token(self):
        """Generate a JWT for key-pair authentication."""
        try:
            import jwt as pyjwt
            import hashlib
            import base64
            from cryptography.hazmat.primitives.serialization import load_pem_private_key
            from cryptography.hazmat.backends import default_backend
        except ImportError:
            self.module.fail_json(
                msg='PyJWT, cryptography libraries are required for key-pair auth. '
                    'Install them with: pip install PyJWT cryptography'
            )

        now = int(time.time())
        private_key_obj = load_pem_private_key(
            self.private_key.encode('utf-8'),
            password=None,
            backend=default_backend(),
        )

        # Snowflake expects the account identifier in uppercase
        account_upper = self.account.upper()
        user_upper = self.user.upper()

        # Build the public key fingerprint for the issuer
        public_key_der = private_key_obj.public_key().public_bytes(
            encoding=__import__('cryptography.hazmat.primitives.serialization',
                                fromlist=['Encoding']).Encoding.DER,
            format=__import__('cryptography.hazmat.primitives.serialization',
                              fromlist=['PublicFormat']).PublicFormat.SubjectPublicKeyInfo,
        )
        sha256_hash = hashlib.sha256(public_key_der).digest()
        fingerprint = base64.b64encode(sha256_hash).decode('utf-8')

        payload = {
            'iss': '{0}.{1}.SHA256:{2}'.format(account_upper, user_upper, fingerprint),
            'sub': '{0}.{1}'.format(account_upper, user_upper),
            'iat': now,
            'exp': now + 3600,
        }

        token = pyjwt.encode(payload, private_key_obj, algorithm='RS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return token

    def _password_token(self):
        """Authenticate via the session/token login endpoint and return the master token."""
        url = '{0}/session/v1/login-request'.format(self.base_url)
        body = json.dumps({
            'data': {
                'LOGIN_NAME': self.user,
                'PASSWORD': self.password,
                'ACCOUNT_NAME': self.account,
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        try:
            resp = open_url(
                url, data=body, headers=headers, method='POST',
                validate_certs=self.validate_certs,
            )
            result = json.loads(resp.read())
            return result['data']['token']
        except (HTTPError, URLError, ValueError, KeyError) as exc:
            self.module.fail_json(msg='Snowflake password authentication failed: {0}'.format(str(exc)))

    # ------------------------------------------------------------------
    # Request helpers
    # ------------------------------------------------------------------

    def _headers(self):
        """Return common request headers."""
        auth_scheme = 'Bearer' if self.password else 'Bearer'
        if self.private_key:
            auth_scheme = 'Bearer'
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer {0}'.format(self._token),
            'X-Snowflake-Authorization-Token-Type': 'KEYPAIR_JWT' if self.private_key else 'SNOWFLAKE',
            'User-Agent': 'AnsibleSnowflakeCollection/1.0',
        }

    def _build_body(self, sql, bindings=None):
        """Build the JSON body for a statement execution request."""
        body = {
            'statement': sql,
            'timeout': 60,
        }
        if self.role:
            body['role'] = self.role
        if self.warehouse:
            body['warehouse'] = self.warehouse
        if self.database:
            body['database'] = self.database
        if self.schema:
            body['schema'] = self.schema
        if bindings:
            body['bindings'] = bindings
        return body

    def _request(self, url, body=None, method='POST'):
        """Execute an HTTP request and return parsed JSON."""
        headers = self._headers()
        data = json.dumps(body) if body else None
        try:
            resp = open_url(
                url, data=data, headers=headers, method=method,
                validate_certs=self.validate_certs,
            )
            status = resp.getcode()
            content = resp.read()
            result = json.loads(content) if content else {}
            return status, result
        except HTTPError as exc:
            try:
                error_body = json.loads(exc.read())
                msg = error_body.get('message', str(exc))
                code = error_body.get('code')
                sql_state = error_body.get('sqlState')
            except (ValueError, AttributeError):
                msg = str(exc)
                code = None
                sql_state = None
            raise SnowflakeError(msg, code=code, sql_state=sql_state)
        except URLError as exc:
            raise SnowflakeError('Connection error: {0}'.format(str(exc)))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute_sql(self, sql, bindings=None):
        """Execute a SQL statement and return the full response.

        Handles asynchronous execution (HTTP 202) by polling for results.

        Returns:
            dict: The API response containing statementHandle, data, and
                  resultSetMetaData.
        """
        body = self._build_body(sql, bindings)
        status, result = self._request(self.api_url, body=body)

        if status == 202:
            # Async query -- poll until complete
            handle = result.get('statementHandle')
            if not handle:
                raise SnowflakeError('Received 202 but no statementHandle in response.')
            return self.get_results(handle)

        if result.get('code') and int(result['code']) >= 390000:
            raise SnowflakeError(
                result.get('message', 'Unknown error'),
                code=result.get('code'),
                sql_state=result.get('sqlState'),
            )

        return result

    def execute_ddl(self, sql):
        """Execute a DDL statement (CREATE, ALTER, DROP).

        Returns:
            dict: The API response.  DDL statements typically return a
                  status message but no row data.
        """
        return self.execute_sql(sql)

    def query(self, sql, bindings=None):
        """Execute a query and return result rows as a list of dicts.

        Returns:
            list[dict]: Each row mapped to column names from metadata.
        """
        result = self.execute_sql(sql, bindings=bindings)
        return self._rows_to_dicts(result)

    def get_results(self, statement_handle):
        """Poll for results of an asynchronous statement.

        Args:
            statement_handle: The handle returned by a 202 response.

        Returns:
            dict: The completed query response.
        """
        url = '{0}/{1}'.format(self.api_url, statement_handle)
        elapsed = 0
        while elapsed < self.MAX_POLL_SECONDS:
            status, result = self._request(url, method='GET')
            query_status = result.get('statementStatusUrl', '')
            code = result.get('code', '0')

            # Success
            if status == 200 and str(code) == '0':
                return result

            # Still running
            if status == 202 or str(code) == '333334':
                time.sleep(self.POLL_INTERVAL)
                elapsed += self.POLL_INTERVAL
                continue

            # Error
            raise SnowflakeError(
                result.get('message', 'Query failed'),
                code=code,
                sql_state=result.get('sqlState'),
            )

        raise SnowflakeError(
            'Query timed out after {0} seconds (handle={1}).'.format(
                self.MAX_POLL_SECONDS, statement_handle
            )
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _rows_to_dicts(result):
        """Convert Snowflake API result data to a list of dicts."""
        meta = result.get('resultSetMetaData', {})
        columns = [col['name'] for col in meta.get('rowType', [])]
        data = result.get('data', [])
        return [dict(zip(columns, row)) for row in data]

    @staticmethod
    def quote_identifier(name):
        """Double-quote a Snowflake identifier, escaping inner quotes."""
        return '"{0}"'.format(name.replace('"', '""'))
