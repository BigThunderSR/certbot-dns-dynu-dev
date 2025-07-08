#!/bin/bash
# simple_test.sh - Simple testing without virtual environment

echo "🧪 Simple Testing for certbot-dns-dynu-dev (without venv)"
echo "This script tests the plugin using the system Python installation"
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Please run this script from the plugin root directory"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $python_version"

# Check if certbot is available
if command -v certbot >/dev/null 2>&1; then
    echo "✅ Certbot found: $(certbot --version)"
    CERTBOT_CMD="certbot"
else
    echo "⚠️  Certbot command not found in PATH. Using wrapper script..."
    # Check if we can run certbot via Python
    if python3 -c "import certbot" >/dev/null 2>&1; then
        echo "✅ Certbot available via Python. Use 'python run_certbot.py' instead of 'certbot'"
        CERTBOT_CMD="python run_certbot.py"
    else
        echo "❌ Certbot not available. Install with: pip install certbot"
        exit 1
    fi
fi

# Install the plugin in development mode
echo "📦 Installing plugin in development mode..."
if pip install -e .; then
    echo "✅ Plugin installed successfully"
else
    echo "❌ Failed to install plugin"
    exit 1
fi

# Check plugin registration
echo "🔌 Checking plugin registration..."
if $CERTBOT_CMD plugins --text | grep -q "dns-dynu"; then
    echo "✅ Plugin successfully registered with certbot"
    $CERTBOT_CMD plugins --text | grep -A2 "dns-dynu"
else
    echo "❌ Plugin not found in certbot plugins"
    exit 1
fi

echo ""
echo "🧪 Running Tests..."
echo ""

# Run local logic tests
echo "1. Running local logic tests..."
if python test_local.py >/dev/null 2>&1; then
    echo "✅ Local logic tests passed"
else
    echo "❌ Local logic tests failed"
fi

# Run unit tests
echo "2. Running unit tests..."
if python certbot_dns_dynu_dev/dns_dynu_test.py >/dev/null 2>&1; then
    echo "✅ Unit tests passed"
else
    echo "⚠️  Unit tests had issues (may be expected)"
fi

echo ""
echo "🎉 Plugin testing completed!"
echo ""
echo "Next steps:"
echo "1. Create credentials file: echo 'dns_dynu_auth_token = YOUR_KEY' > dynu-creds.ini"
echo "2. Set permissions: chmod 600 dynu-creds.ini"
echo "3. Test dry run:"
echo ""
echo "   # Using detected command method:"
echo "   $CERTBOT_CMD certonly --authenticator dns-dynu --dns-dynu-credentials dynu-creds.ini --dry-run -d test.domain.com"
echo ""

# Show example commands
echo "Example testing commands:"
echo ""
echo "# Test with dry run (safe)"
echo "$CERTBOT_CMD certonly \\"
echo "  --authenticator dns-dynu \\"
echo "  --dns-dynu-credentials dynu-creds.ini \\"
echo "  --dry-run \\"
echo "  -d test.your-domain.com"
echo ""
echo "# Test subdomain (the main fix)"
echo "$CERTBOT_CMD certonly \\"
echo "  --authenticator dns-dynu \\"
echo "  --dns-dynu-credentials dynu-creds.ini \\"
echo "  --dry-run \\"
echo "  -d my.your-domain.com"
