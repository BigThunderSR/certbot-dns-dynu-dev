#!/usr/bin/env python3
"""
Interactive testing script for certbot-dns-dynu-dev plugin
This script helps you test specific scenarios interactively
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


def print_banner(title):
    """Print a formatted banner"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{title}")
    print("-" * len(title))


def get_user_input(prompt, default=None):
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def check_python_version():
    """Check if Python version meets requirements"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.9+")
        return False


def check_certbot_installation():
    """Check if certbot is installed"""
    try:
        result = subprocess.run(['certbot', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Certbot installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Certbot not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Certbot not found")
        return False


def check_plugin_installation():
    """Check if the plugin is installed"""
    try:
        result = subprocess.run(['certbot', 'plugins', '--text'], 
                              capture_output=True, text=True, timeout=10)
        if 'dns-dynu' in result.stdout:
            print("✅ Plugin installed and recognized by certbot")
            return True
        else:
            print("❌ Plugin not found in certbot plugins list")
            print("Run: pip install -e . to install in development mode")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Cannot check plugin status")
        return False


def create_credentials_file():
    """Create a credentials file"""
    print_section("Creating Credentials File")
    
    print("You need a Dynu API key to test this plugin.")
    print("Get one from: https://www.dynu.com/Account/APICredentials")
    
    api_key = get_user_input("Enter your Dynu API key")
    
    if not api_key:
        print("❌ API key required")
        return None
    
    # Create credentials file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(f"dns_dynu_auth_token = {api_key}\n")
        cred_file = f.name
    
    # Set permissions
    os.chmod(cred_file, 0o600)
    
    print(f"✅ Created credentials file: {cred_file}")
    return cred_file


def test_dry_run(cred_file, domain):
    """Run a dry-run test"""
    print_section(f"Testing Dry Run for {domain}")
    
    email = get_user_input("Enter email for certbot", "test@example.com")
    
    cmd = [
        'certbot', 'certonly',
        '--authenticator', 'dns-dynu',
        '--dns-dynu-credentials', cred_file,
        '--dns-dynu-propagation-seconds', '120',
        '--dry-run',
        '-d', domain,
        '--email', email,
        '--agree-tos',
        '--non-interactive'
    ]
    
    print("Running command:")
    print(" ".join(cmd))
    print("\nThis will:")
    print("- Create TXT records in your DNS")
    print("- Test the ACME challenge process")
    print("- Clean up the TXT records")
    print("- NOT issue a real certificate")
    
    proceed = get_user_input("Proceed? (y/n)", "y").lower()
    
    if proceed == 'y':
        try:
            result = subprocess.run(cmd, timeout=300)  # 5 minute timeout
            if result.returncode == 0:
                print("✅ Dry run successful!")
                return True
            else:
                print("❌ Dry run failed")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Dry run timed out")
            return False
    else:
        print("Skipped")
        return None


def run_logic_tests():
    """Run the local logic tests"""
    print_section("Running Local Logic Tests")
    
    test_script = Path(__file__).parent / "test_local.py"
    
    if test_script.exists():
        try:
            result = subprocess.run([sys.executable, str(test_script)], timeout=60)
            if result.returncode == 0:
                print("✅ Logic tests passed")
                return True
            else:
                print("❌ Logic tests failed")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Logic tests timed out")
            return False
    else:
        print("❌ test_local.py not found")
        return False


def run_unit_tests():
    """Run the unit tests"""
    print_section("Running Unit Tests")
    
    test_file = Path(__file__).parent / "certbot_dns_dynu_dev" / "dns_dynu_test.py"
    
    if test_file.exists():
        try:
            result = subprocess.run([sys.executable, str(test_file)], timeout=60)
            if result.returncode == 0:
                print("✅ Unit tests passed")
                return True
            else:
                print("❌ Some unit tests failed (this may be expected)")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Unit tests timed out")
            return False
    else:
        print("❌ dns_dynu_test.py not found")
        return False


def main():
    """Main interactive testing function"""
    
    print_banner("Interactive Testing for certbot-dns-dynu-dev")
    
    print("This script will guide you through testing the plugin.")
    print("Make sure you have a Dynu account and a test domain!")
    
    # System checks
    print_section("System Compatibility Check")
    
    if not check_python_version():
        print("Please upgrade to Python 3.9 or later")
        return
    
    if not check_certbot_installation():
        print("Please install certbot: pip install certbot")
        return
    
    if not check_plugin_installation():
        print("Please install the plugin: pip install -e .")
        return
    
    # Test selection
    print_section("Test Selection")
    print("Available tests:")
    print("1. Unit tests (test internal logic)")
    print("2. Local logic tests (test subdomain fallback)")
    print("3. Dry run with real domain (requires Dynu credentials)")
    print("4. All tests")
    
    choice = get_user_input("Select test (1-4)", "4")
    
    cred_file = None
    
    if choice in ['3', '4']:
        cred_file = create_credentials_file()
        if not cred_file:
            print("Cannot run dry-run tests without credentials")
            choice = '1' if choice == '3' else '2'
    
    # Run selected tests
    results = {}
    
    if choice in ['1', '4']:
        results['unit'] = run_unit_tests()
    
    if choice in ['2', '4']:
        results['logic'] = run_logic_tests()
    
    if choice in ['3', '4'] and cred_file:
        print_section("Domain Testing")
        print("Testing scenarios:")
        print("- Apex domain (domain.com)")
        print("- Subdomain (my.domain.com) - Main fix")
        print("- Deep subdomain (api.my.domain.com)")
        
        domain = get_user_input("Enter your test domain (you must own this)")
        
        if domain:
            # Test apex domain
            results['apex'] = test_dry_run(cred_file, domain)
            
            # Test subdomain
            subdomain = f"test.{domain}"
            results['subdomain'] = test_dry_run(cred_file, subdomain)
            
            # Test deep subdomain if user wants
            if get_user_input("Test deep subdomain? (y/n)", "n").lower() == 'y':
                deep_subdomain = f"api.test.{domain}"
                results['deep'] = test_dry_run(cred_file, deep_subdomain)
    
    # Summary
    print_banner("Test Results Summary")
    
    for test_name, result in results.items():
        if result is True:
            print(f"✅ {test_name.title()} test: PASSED")
        elif result is False:
            print(f"❌ {test_name.title()} test: FAILED")
        elif result is None:
            print(f"⏭️  {test_name.title()} test: SKIPPED")
    
    # Cleanup
    if cred_file:
        cleanup = get_user_input("Delete credentials file? (y/n)", "y").lower()
        if cleanup == 'y':
            os.unlink(cred_file)
            print(f"🗑️  Deleted {cred_file}")
    
    print("\n💡 Next Steps:")
    if all(r in [True, None] for r in results.values()):
        print("✅ All tests passed! Your plugin is working correctly.")
        print("You can now use it with real domains:")
        print("certbot certonly --authenticator dns-dynu --dns-dynu-credentials /path/to/creds -d your-domain.com")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        print("Common fixes:")
        print("- Ensure Python 3.9+")
        print("- Run: pip install -e .")
        print("- Check Dynu API credentials")
        print("- Verify domain ownership")


if __name__ == "__main__":
    main()
