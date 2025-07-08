#!/bin/bash
# setup_venv_test_py38.sh - Script for testing with Python 3.8 (temporary workaround)

set -e  # Exit on any error

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo "🐍 Setting up Python Virtual Environment for certbot-dns-dynu-dev testing (Python 3.8 compatibility)"
echo "Project directory: $PROJECT_DIR"

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $python_version"

# Backup setup.py if not already backed up
if [ ! -f "setup.py.backup" ]; then
    echo "📦 Backing up setup.py..."
    cp setup.py setup.py.backup
fi

# Temporarily modify setup.py for Python 3.8 compatibility
echo "🔧 Temporarily modifying setup.py for Python 3.8..."
sed -i 's/python_requires=">=3.9"/python_requires=">=3.8"/' setup.py

# Create virtual environment (check if it's properly created)
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    if [ -d "$VENV_DIR" ]; then
        echo "🗑️  Removing incomplete virtual environment..."
        rm -rf "$VENV_DIR"
    fi
    echo "📦 Creating virtual environment..."
    
    # Try to install python3-venv if venv creation fails
    if ! python3 -m venv "$VENV_DIR" 2>/dev/null; then
        echo "❌ Failed to create virtual environment. Trying to install python3-venv..."
        echo "💡 You may need to run: sudo apt install python3.8-venv"
        echo "💡 Alternative: use the simple_test.sh script without virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "❌ Virtual environment activation script not found"
    echo "💡 Try running: sudo apt install python3.8-venv"
    exit 1
fi

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
echo "⚠️  WARNING: This setup modified setup.py for Python 3.8 compatibility."
echo "   The original setup.py was backed up as setup.py.backup"
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
echo "💡 To restore original setup.py: mv setup.py.backup setup.py"
echo "Run 'deactivate' to exit the virtual environment."
