#!/usr/bin/env python3
"""
Certbot wrapper script for systems where certbot command is not in PATH
"""

import sys
from certbot import main

if __name__ == "__main__":
    # Pass all command line arguments to certbot
    sys.exit(main.main(sys.argv[1:]))
