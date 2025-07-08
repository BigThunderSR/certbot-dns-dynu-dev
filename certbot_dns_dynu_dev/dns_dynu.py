"""Updated DNS Authenticator for Dynu."""

import logging

# from certbot import interfaces
# from certbot import errors

from certbot.plugins import dns_common
from certbot.plugins import dns_common_lexicon

from lexicon.providers import dynu  # pylint: disable=no-name-in-module

logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """Updated DNS Authenticator for Dynu."""

    description = 'Obtain certificates using a DNS TXT record with Dynu DNS.'

    ttl = 60

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add, default_propagation_seconds=60):
        # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(
              add, default_propagation_seconds=default_propagation_seconds)
        add("credentials", help="Dynu credentials file.")

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return ('This plugin configures a DNS TXT record to respond to a '
                'dns-01 challenge using Dynu API')

    def _setup_credentials(self):
        self._configure_file('credentials',
                             'Absolute path to Dynu credentials file')
        dns_common.validate_file_permissions(self.conf('credentials'))
        self.credentials = self._configure_credentials(
            'credentials',
            'Dynu credentials file',
            {
                'auth-token': 'Dynu-compatible API key (API-Key)',
            }
        )

    def _perform(self, domain, validation_name, validation):
        self._get_dynu_client().add_txt_record(
            domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self._get_dynu_client().del_txt_record(
            domain, validation_name, validation)

    def _get_dynu_client(self):
        if not self.credentials:
            self._setup_credentials()
        assert self.credentials is not None, \
            "Credentials should be set after _setup_credentials()"
        return _DynuLexiconClient(
            self.credentials.conf('auth-token'),
            self.ttl
        )


class _DynuLexiconClient(dns_common_lexicon.LexiconClient):
    """Encapsulates all communication with Dynu via Lexicon."""

    def __init__(self, auth_token, ttl):
        super(_DynuLexiconClient, self).__init__()

        config = dns_common_lexicon.build_lexicon_config('dynu', {
            'ttl': ttl,
        }, {
            'auth_token': auth_token,
        })

        self.provider = dynu.Provider(config)

    def add_txt_record(self, domain, record_name, record_content):
        """Add a TXT record to the domain."""
        try:
            # First try to add the record using the full domain as the zone
            # This handles cases where the subdomain is managed as its own zone
            super(_DynuLexiconClient, self).add_txt_record(
                domain, record_name, record_content)
        except Exception as e:
            logger.debug("Failed to add TXT record to %s zone: %s", domain, e)
            # If that fails, try to find the parent domain zone
            # Split the domain and try progressively shorter domains
            domain_parts = domain.split('.')
            for i in range(len(domain_parts) - 1):
                parent_domain = '.'.join(domain_parts[i:])
                if i > 0:
                    # Adjust the record name to include the subdomain parts
                    subdomain_parts = '.'.join(domain_parts[:i])
                    adjusted_name = (f"{record_name}.{subdomain_parts}"
                                     if record_name else subdomain_parts)
                else:
                    adjusted_name = record_name

                try:
                    logger.debug(
                        "Trying to add TXT record to parent zone %s "
                        "with name %s", parent_domain, adjusted_name)
                    super(_DynuLexiconClient, self).add_txt_record(
                        parent_domain, adjusted_name, record_content)
                    return  # Success, exit the function
                except Exception as parent_e:
                    logger.debug("Failed to add TXT record to %s zone: %s",
                                 parent_domain, parent_e)
                    continue

            # If all attempts failed, raise the original exception
            raise e

    def del_txt_record(self, domain, record_name, record_content):
        """Delete a TXT record from the domain."""
        try:
            # First try to delete the record using the full domain as the zone
            super(_DynuLexiconClient, self).del_txt_record(
                domain, record_name, record_content)
        except Exception as e:
            logger.debug("Failed to delete TXT record from %s zone: %s",
                         domain, e)
            # If that fails, try to find the parent domain zone
            # Split the domain and try progressively shorter domains
            domain_parts = domain.split('.')
            for i in range(len(domain_parts) - 1):
                parent_domain = '.'.join(domain_parts[i:])
                if i > 0:
                    # Adjust the record name to include the subdomain parts
                    subdomain_parts = '.'.join(domain_parts[:i])
                    adjusted_name = (f"{record_name}.{subdomain_parts}"
                                     if record_name else subdomain_parts)
                else:
                    adjusted_name = record_name

                try:
                    logger.debug(
                        "Trying to delete TXT record from parent zone %s "
                        "with name %s", parent_domain, adjusted_name)
                    super(_DynuLexiconClient, self).del_txt_record(
                        parent_domain, adjusted_name, record_content)
                    return  # Success, exit the function
                except Exception as parent_e:
                    logger.debug("Failed to delete TXT record from %s zone: %s",
                                 parent_domain, parent_e)
                    continue

            # If all attempts failed, raise the original exception
            raise e

    def _handle_http_error(self, e, domain_name):
        if domain_name in str(e) and (
            # 4.0 and 4.1 compatibility
            str(e).startswith(
                '422 Client Error: Unprocessable Entity for url:') or
            # 4.2
            str(e).startswith('404 Client Error: Not Found for url:')
        ):
            return  # Expected errors when zone name guess is wrong
        return super(_DynuLexiconClient, self)._handle_http_error(
            e, domain_name)

    def _handle_general_error(self, e, domain_name):
        # Error from https://github.com/AnalogJ/lexicon/blob/master/lexicon/providers/dynu.py#L38
        if str(e) == "No matching domain found":
            return  # Expected error when zone name guess is wrong.
        return super(_DynuLexiconClient, self)._handle_general_error(
            e, domain_name)
