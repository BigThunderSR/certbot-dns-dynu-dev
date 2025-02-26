# certbot-dns-dynu-dev

[![CodeQL](https://github.com/BigThunderSR/certbot-dns-dynu-dev/actions/workflows/github-code-scanning/codeql/badge.svg?style=plastic)](https://github.com/BigThunderSR/certbot-dns-dynu-dev/actions/workflows/github-code-scanning/codeql)
[![Dependabot Updates](https://github.com/BigThunderSR/certbot-dns-dynu-dev/actions/workflows/dependabot/dependabot-updates/badge.svg?style=plastic)](https://github.com/BigThunderSR/certbot-dns-dynu-dev/actions/workflows/dependabot/dependabot-updates)
[![Python Lint and Test](https://github.com/BigThunderSR/certbot-dns-dynu-dev/actions/workflows/python-lint-test.yml/badge.svg?style=plastic)](https://github.com/BigThunderSR/certbot-dns-dynu-dev/actions/workflows/python-lint-test.yml)
[![Upload Python Package](https://github.com/BigThunderSR/certbot-dns-dynu-dev/actions/workflows/python-publish.yml/badge.svg?style=plastic)](https://github.com/BigThunderSR/certbot-dns-dynu-dev/actions/workflows/python-publish.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/certbot-dns-dynu-dev?style=plastic&labelColor=yellow&color=blue)](https://pypi.org/project/certbot-dns-dynu-dev/)

Updated Dynu DNS Authenticator plugin for [Certbot](https://certbot.eff.org/).

This plugin is built from the ground up and follows the development style and life-cycle
of other `certbot-dns-*` plugins found in the
[Official Certbot Repository](https://github.com/certbot/certbot).

This fork was created because the pull request [Add support for Dynu DNS API](https://github.com/bikram990/certbot-dns-dynu/pull/7) was not being merged in the upstream project by the original author. It has since been merged in the upstream project. However, this fork has been updated for currency and compatibility with the latest versions of Python and Certbot.

This fork is also being used in the Home Assistant Let's Encrypt add-on via <https://github.com/home-assistant/addons/pull/3556>

## Installation

```bash
pip install --upgrade certbot
pip install certbot-dns-dynu-dev
```

## Verify

```bash
certbot plugins --text

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
* dns-dynu
Description: Obtain certificates using a DNS TXT record with Dynu DNS.
Entry point: dns-dynu = certbot_dns_dynu_dev.dns_dynu:Authenticator

...
...
```

## Configuration

The credentials file e.g. `~/dynu-credentials.ini` should look like this:

```ini
dns_dynu_auth_token = AbCbASsd!@34
```

## Usage

```bash
# Obtain a certificate using the Dynu DNS authenticator
certbot ... \
        --authenticator dns-dynu  \
        --dns-dynu-credentials ~/dynu-credentials.ini \
        certonly
```

## FAQ

### Why is the plugin name so long?

This follows the upstream nomenclature: `certbot-dns-<dns-provider>`.

### Why do I have to use `:` as a separator in the name? Why are the configuration file parameters unusual?

This is a limitation of the Certbot interface towards _third-party_ plugins.

For details read the discussions:

- <https://github.com/certbot/certbot/issues/6504#issuecomment-473462138>
- <https://github.com/certbot/certbot/issues/6040>
- <https://github.com/certbot/certbot/issues/4351>
- <https://github.com/certbot/certbot/pull/6372>

## Development

Create a virtualenv, install the plugin (`editable` mode), spawn the environment and run the test:

```bash
virtualenv -p python3 .venv
source .venv/bin/activate
pip install -e .
python ./certbot_dns_dynu_dev/dns_dynu_test.py
```

## License

Copyright ©️ 2023 - 2025 [BigThunderSR](https://github.com/BigThunderSR)

Original Copyright (c) 2021 [Bikramjeet Singh](https://github.com/bikram990)

## Credits

[PowerDNS](https://github.com/pan-net-security/certbot-dns-powerdns)

[dns-lexicon](https://github.com/AnalogJ/lexicon)

## Helpful Links

- [DNS Plugin list](https://certbot.eff.org/docs/using.html?highlight=dns#dns-plugins)

- [acme.sh](https://github.com/acmesh-official/acme.sh)

- [dynu with acme.sh](https://gist.github.com/tavinus/15ea64c50ac5fb7cea918e7786c94a95)

- [dynu api](https://www.dynu.com/Support/API)
