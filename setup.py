#! /usr/bin/env python
"""Test for DNS Authenticator for Dynu"""

from os import path
from setuptools import setup
from setuptools import find_packages

VERSION = "0.0.8"

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'acme>3.0.0',
    'certbot>3.0.0',
    'dns-lexicon>3.0.0',
    'tldextract>=5.0.0',
    'dnspython',
    'mock',
    'setuptools>=68.0.0',
    'requests'
]


here = path.abspath(path.dirname(__file__))

setup(
    name='certbot-dns-dynu-dev',
    version=VERSION,

    description="Updated Dynu DNS Authenticator plugin for Certbot",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/BigThunderSR/certbot-dns-dynu-dev',
    download_url='https://github.com/BigThunderSR/certbot-dns-dynu-dev/archive/refs/tags/'
                + VERSION + '.tar.gz',
    author="Updated by BigThunderSR; original author Bikramjeet Sing,",
    license='Apache License 2.0',
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],

    packages=find_packages(),
    install_requires=install_requires,

    # extras_require={
    #     'docs': docs_extras,
    # },

    entry_points={
        'certbot.plugins': [
            'dns-dynu = certbot_dns_dynu_dev.dns_dynu:Authenticator',
        ],
    },
    test_suite='certbot_dns_dynu_dev',
)
