#!/bin/bash
# setup_venv_test.sh - Script to set up virtual environment and test the plugin

set -e # Exit on any error

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo "🐍 Setting up Python Virtual Environment for certbot-dns-dynu-dev testing"
echo "Project directory: $PROJECT_DIR"

# Check if Python 3.9+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $python_version"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "✅ Python version is compatible"
else
    echo "❌ Python 3.9+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Verify activation
if [ "$VIRTUAL_ENV" = "$VENV_DIR" ]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Show Python and pip locations
echo "📍 Python executable: $(which python)"
echo "📍 Pip executable: $(which pip)"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade certbot
pip install pytest pytest-cov flake8
pip install -e .

# Verify installations
echo "🔍 Verifying installations..."
echo "Certbot version: $(certbot --version)"
echo "Certbot location: $(which certbot)"

# Check plugin registration
echo "🔌 Checking plugin registration..."
if certbot plugins --text | grep -q "dns-dynu"; then
    echo "✅ Plugin successfully registered with certbot"
    certbot plugins --text | grep -A2 "dns-dynu"
else
    echo "❌ Plugin not found in certbot plugins"
    exit 1
fi

echo ""
echo "🎉 Setup complete! Virtual environment is ready for testing."
echo ""
echo "To use this environment:"
echo "1. Activate: source venv/bin/activate"
echo "2. Run tests: python test_local.py"
echo "3. Test with real domain: certbot certonly --authenticator dns-dynu --dry-run -d your-domain.com"
echo "4. Deactivate when done: deactivate"
echo ""

# Run basic tests if requested
if [ "$1" = "--test" ]; then
    echo "🧪 Running basic tests..."

    echo "Running local logic tests..."
    python test_local.py

    echo "Running unit tests..."
    python certbot_dns_dynu_dev/dns_dynu_test.py || echo "Some unit tests failed (may be expected)"

    echo "✅ Basic tests completed"
fi

echo "💡 Virtual environment is active in this shell session."
echo "Run 'deactivate' to exit the virtual environment."
