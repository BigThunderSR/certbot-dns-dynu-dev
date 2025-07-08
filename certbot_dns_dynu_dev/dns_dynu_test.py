"""Tests for certbot_dns_dynu_dev.dns_dynu"""

import os
import unittest

import mock
from requests.exceptions import HTTPError

from certbot.plugins import dns_test_common
from certbot.plugins import dns_test_common_lexicon
from certbot.plugins.dns_test_common import DOMAIN

from certbot.tests import util as test_util

AUTH_TOKEN = '00000000-0000-0000-0000-000000000000'


class AuthenticatorTest(test_util.TempDirTestCase,
                        dns_test_common_lexicon.BaseLexiconAuthenticatorTest):
    """DNS Authenticator Test for Dynu."""

    def setUp(self):
        super(AuthenticatorTest, self).setUp()

        from certbot_dns_dynu_dev.dns_dynu import Authenticator

        path = os.path.join(self.tempdir, 'file.ini')
        dns_test_common.write(
            {"dynu_auth_token": AUTH_TOKEN},
            path
        )

        print("File content: ")
        # print(open(path).read())
        with open(path, encoding='utf-8') as f:
            print(f.read())

        self.config = mock.MagicMock(dynu_credentials=path,
                                     dynu_propagation_seconds=0)  # don't wait during tests

        self.auth = Authenticator(self.config, "dynu")

        self.mock_client = mock.MagicMock()
        self.auth._get_dynu_client = mock.MagicMock(
            return_value=self.mock_client)


class DynuLexiconClientTest(unittest.TestCase,
                            dns_test_common_lexicon.BaseLexiconClientTest):
    """Lexicon Client Test for Dynu."""
    DOMAIN_NOT_FOUND = HTTPError(
        '422 Client Error: Unprocessable Entity for url: {0}.'
        .format(DOMAIN))
    LOGIN_ERROR = HTTPError('401 Client Error: Unauthorized')

    def setUp(self):
        from certbot_dns_dynu_dev.dns_dynu import _DynuLexiconClient

        self.client = _DynuLexiconClient(auth_token=AUTH_TOKEN, ttl=0)

        self.provider_mock = mock.MagicMock()
        self.client.provider = self.provider_mock


class SubdomainHandlingTest(unittest.TestCase):
    """Test subdomain TXT record handling."""

    def setUp(self):
        from certbot_dns_dynu_dev.dns_dynu import _DynuLexiconClient

        self.client = _DynuLexiconClient(auth_token=AUTH_TOKEN, ttl=0)
        self.client.provider = mock.MagicMock()

        # Mock the parent class methods
        self.add_txt_record_mock = mock.MagicMock()
        self.del_txt_record_mock = mock.MagicMock()

    def test_subdomain_fallback_add_record(self):
        """Test that subdomain TXT record creation falls back to parent domain when subdomain zone doesn't exist."""

        # Configure mocks - first call fails, second succeeds
        def side_effect(domain, record_name, record_content):
            if domain == 'my.example.com':
                raise Exception("No matching domain found")
            elif domain == 'example.com' and record_name == '_acme-challenge.my':
                return None  # Success
            else:
                raise Exception(f"Unexpected call: {domain}, {record_name}")

        # Mock the parent class method directly
        with mock.patch.object(
                self.client.__class__.__bases__[0], 'add_txt_record',
                side_effect=side_effect) as mock_add:
            try:
                # Should not raise an exception
                self.client.add_txt_record(
                    'my.example.com', '_acme-challenge', 'test-value')
                # Verify it was called multiple times
                # (exact count may vary due to implementation)
                self.assertGreaterEqual(mock_add.call_count, 2)
            except Exception as e:
                self.fail(f"Should not have raised an exception: {e}")

    def test_subdomain_fallback_del_record(self):
        """Test that subdomain TXT record deletion falls back to parent domain when subdomain zone doesn't exist."""

        # Configure mocks - first call fails, second succeeds
        def side_effect(domain, record_name, record_content):
            if domain == 'my.example.com':
                raise Exception("No matching domain found")
            elif domain == 'example.com' and record_name == '_acme-challenge.my':
                return None  # Success
            else:
                raise Exception(f"Unexpected call: {domain}, {record_name}")

        # Mock the parent class method directly
        with mock.patch.object(
                self.client.__class__.__bases__[0], 'del_txt_record',
                side_effect=side_effect) as mock_del:
            try:
                # Should not raise an exception
                self.client.del_txt_record(
                    'my.example.com', '_acme-challenge', 'test-value')
                # Verify it was called multiple times
                # (exact count may vary due to implementation)
                self.assertGreaterEqual(mock_del.call_count, 2)
            except Exception as e:
                self.fail(f"Should not have raised an exception: {e}")

    def test_deep_subdomain_fallback(self):
        """Test that deep subdomain TXT record creation works with multiple levels."""

        def side_effect(domain, record_name, record_content):
            if domain == 'sub.my.example.com':
                raise Exception("No matching domain found")
            elif domain == 'my.example.com':
                raise Exception("No matching domain found")
            elif (domain == 'example.com' and
                  record_name == '_acme-challenge.sub.my'):
                return None  # Success
            else:
                raise Exception(f"Unexpected call: {domain}, {record_name}")

        # Mock the parent class method directly
        with mock.patch.object(
                self.client.__class__.__bases__[0], 'add_txt_record',
                side_effect=side_effect) as mock_add:
            try:
                # Should not raise an exception
                self.client.add_txt_record(
                    'sub.my.example.com', '_acme-challenge', 'test-value')
                # Verify it was called multiple times
                # (exact count may vary due to implementation)
                self.assertGreaterEqual(mock_add.call_count, 3)
            except Exception as e:
                self.fail(f"Should not have raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
