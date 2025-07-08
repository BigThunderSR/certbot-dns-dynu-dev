# Testing Guide for certbot-dns-dynu-dev

This guide provides comprehensive instructions for testing the certbot-dns-dynu-dev plugin locally and with real domains.

## Prerequisites

1. **Python Environment**: Python 3.9+ (the plugin requires this version)
   - **Note**: If you only have Python 3.8, you can still test the logic, but you'll need to temporarily modify `setup.py` to allow Python 3.8 for testing
2. **Dynu Account**: Sign up at <https://www.dynu.com/> if you don't have one
3. **Test Domain**: A domain managed by Dynu DNS

### Python Version Compatibility

If you're stuck with Python 3.8 for testing, you can temporarily modify the version requirement:

```bash
# Backup the original setup.py
cp setup.py setup.py.backup

# Edit setup.py to allow Python 3.8 (FOR TESTING ONLY)
sed -i 's/python_requires=">=3.9"/python_requires=">=3.8"/' setup.py

# After testing, restore the original
mv setup.py.backup setup.py
```

**Important**: This is only for local testing. The final plugin should maintain the Python 3.9+ requirement.

## Setup Instructions

### Quick Setup (Automated)

For a quick automated setup, use the provided script:

```bash
# For Python 3.9+ systems
./setup_venv_test.sh

# For Python 3.8 systems (testing only)
./setup_venv_test_py38.sh --test

# Simple system-wide testing (no venv)
./simple_test.sh
```

**Note**: If you get venv errors, you may need to install python3-venv:

```bash
sudo apt install python3.8-venv  # On Ubuntu/Debian
```

### Manual Setup

### 1. Install Dependencies

```bash
# Create and activate virtual environment (strongly recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify you're in the virtual environment
which python  # Should show: /path/to/your/project/venv/bin/python
which pip     # Should show: /path/to/your/project/venv/bin/pip

# Install certbot and required dependencies in the virtual environment
pip install --upgrade pip
pip install --upgrade certbot
pip install pytest pytest-cov  # For testing
pip install -e .  # Install the plugin in development mode

# Verify certbot is installed in the venv
which certbot  # Should show: /path/to/your/project/venv/bin/certbot
certbot --version
```

**Important**: All certbot commands in this guide assume you're working within the activated virtual environment. If you deactivate and reactivate later, make sure to run `source venv/bin/activate` again.

### 2. Get Dynu API Credentials

1. Log into your Dynu account
2. Go to "Account" → "API Credentials"
3. Generate an API key
4. Note down the API key (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

### 3. Create Credentials File

Create a file (e.g., `~/dynu-credentials.ini`) with your API key:

```ini
dns_dynu_auth_token = your-api-key-here
```

**Important**: Set proper file permissions for security:

```bash
chmod 600 ~/dynu-credentials.ini
```

## Virtual Environment Testing

### Benefits of Using Virtual Environment

- **Isolation**: Prevents conflicts with system-wide Python packages
- **Clean testing**: Ensures only required dependencies are present
- **Version control**: Pin specific versions of certbot and dependencies
- **Safety**: Won't affect your system's certbot installation

### Virtual Environment Commands

```bash
# Activate the virtual environment (must be done each time you open a new terminal)
source venv/bin/activate

# Check if you're in the virtual environment
echo $VIRTUAL_ENV  # Should show the path to your venv

# Install additional packages if needed
pip install package-name

# See what's installed in the venv
pip list

# Deactivate when done (optional - closing terminal also works)
deactivate
```

### Testing Commands Within Virtual Environment

Once your virtual environment is activated, all these commands will use the venv's certbot:

```bash
# Check plugin registration
certbot plugins --text
# Or if certbot is not in PATH:
python run_certbot.py plugins --text

# Run tests
python certbot_dns_dynu_dev/dns_dynu_test.py
pytest certbot_dns_dynu_dev/dns_dynu_test.py -v

# Test with dry run
certbot certonly --authenticator dns-dynu --dry-run -d test.domain.com ...
# Or if certbot is not in PATH:
python run_certbot.py certonly --authenticator dns-dynu --dry-run -d test.domain.com ...
```

## Testing Methods

### Method 1: Unit Tests

Run the existing unit tests to verify the code works correctly:

```bash
# Run all tests
python certbot_dns_dynu_dev/dns_dynu_test.py

# Run with pytest for better output (if available)
pytest certbot_dns_dynu_dev/dns_dynu_test.py -v
```

### Method 2: Local Logic Testing

Use the provided test script to verify the subdomain fallback logic:

```bash
python test_local.py
```

This script:

- Tests subdomain fallback scenarios without making real API calls
- Verifies record name construction logic
- Shows exactly how the plugin handles different domain configurations

### Method 3: Dry Run Testing

Test with real credentials but without actually requesting certificates:

```bash
# If certbot is in PATH:
certbot certonly \
    --authenticator dns-dynu \
    --dns-dynu-credentials ~/dynu-credentials.ini \
    --dns-dynu-propagation-seconds 120 \
    --dry-run \
    -d your-test-domain.com \
    --email your-email@example.com \
    --agree-tos \
    --non-interactive

# If certbot is not in PATH, use the wrapper script:
python run_certbot.py certonly \
    --authenticator dns-dynu \
    --dns-dynu-credentials ~/dynu-credentials.ini \
    --dns-dynu-propagation-seconds 120 \
    --dry-run \
    -d your-test-domain.com \
    --email your-email@example.com \
    --agree-tos \
    --non-interactive
```

**What this does:**

- Uses real Dynu API credentials
- Creates and removes TXT records in your DNS
- Does NOT actually request certificates from Let's Encrypt
- Safe to run multiple times

### Method 4: Subdomain Testing

Test the specific subdomain functionality that was fixed:

```bash
# Test subdomain certificate (the main issue this plugin fixes)
# If certbot is in PATH:
certbot certonly \
    --authenticator dns-dynu \
    --dns-dynu-credentials ~/dynu-credentials.ini \
    --dns-dynu-propagation-seconds 120 \
    --dry-run \
    -d my.your-domain.com \
    --email your-email@example.com \
    --agree-tos \
    --non-interactive

# If certbot is not in PATH, use the wrapper script:
python run_certbot.py certonly \
    --authenticator dns-dynu \
    --dns-dynu-credentials ~/dynu-credentials.ini \
    --dns-dynu-propagation-seconds 120 \
    --dry-run \
    -d my.your-domain.com \
    --email your-email@example.com \
    --agree-tos \
    --non-interactive

# Test deep subdomain
# If certbot is in PATH:
certbot certonly \
    --authenticator dns-dynu \
    --dns-dynu-credentials ~/dynu-credentials.ini \
    --dns-dynu-propagation-seconds 120 \
    --dry-run \
    -d api.my.your-domain.com \
    --email your-email@example.com \
    --agree-tos \
    --non-interactive

# If certbot is not in PATH, use the wrapper script:
python run_certbot.py certonly \
    --authenticator dns-dynu \
    --dns-dynu-credentials ~/dynu-credentials.ini \
    --dns-dynu-propagation-seconds 120 \
    --dry-run \
    -d api.my.your-domain.com \
    --email your-email@example.com \
    --agree-tos \
    --non-interactive
```

### Method 5: Real Certificate Testing

**⚠️ Only do this with a test domain you control!**

```bash
# Request a real certificate for testing
# If certbot is in PATH:
certbot certonly \
    --authenticator dns-dynu \
    --dns-dynu-credentials ~/dynu-credentials.ini \
    --dns-dynu-propagation-seconds 120 \
    -d test.your-domain.com \
    --email your-email@example.com \
    --agree-tos \
    --non-interactive

# If certbot is not in PATH, use the wrapper script:
python run_certbot.py certonly \
    --authenticator dns-dynu \
    --dns-dynu-credentials ~/dynu-credentials.ini \
    --dns-dynu-propagation-seconds 120 \
    -d test.your-domain.com \
    --email your-email@example.com \
    --agree-tos \
    --non-interactive
```

## Verification Steps

### 1. Check DNS Records During Testing

While running tests, you can verify DNS records are being created:

```bash
# Check if TXT record was created
dig TXT _acme-challenge.my.your-domain.com

# Check with specific DNS server
dig @8.8.8.8 TXT _acme-challenge.my.your-domain.com
```

### 2. Enable Debug Logging

For detailed logging during testing:

```bash
# If certbot is in PATH:
certbot certonly \
    --authenticator dns-dynu \
    --dns-dynu-credentials ~/dynu-credentials.ini \
    --dry-run \
    -d your-test-domain.com \
    --email your-email@example.com \
    --agree-tos \
    --non-interactive \
    --debug

# If certbot is not in PATH, use the wrapper script:
python run_certbot.py certonly \
    --authenticator dns-dynu \
    --dns-dynu-credentials ~/dynu-credentials.ini \
    --dry-run \
    -d your-test-domain.com \
    --email your-email@example.com \
    --agree-tos \
    --non-interactive \
    --debug
```

### 3. Check Certbot Plugin Registration

Verify the plugin is properly installed:

```bash
# If certbot is in PATH:
certbot plugins --text

# If certbot is not in PATH, use the wrapper script:
python run_certbot.py plugins --text
```

You should see:

```bash
* dns-dynu
Description: Obtain certificates using a DNS TXT record with Dynu DNS.
Entry point: dns-dynu = certbot_dns_dynu_dev.dns_dynu:Authenticator
```

## Expected Behavior

### For Subdomain Certificates

When requesting a certificate for `my.domain.com`:

1. Plugin tries to create `_acme-challenge` TXT record in `my.domain.com` zone
2. If that fails (zone doesn't exist), falls back to `domain.com` zone
3. Creates `_acme-challenge.my` TXT record in `domain.com` zone
4. Certbot validates the challenge
5. Plugin cleans up by deleting the TXT record

### Log Messages to Look For

During successful subdomain certificate requests, you should see logs like:

```bash
Failed to add TXT record to my.domain.com zone: No matching domain found
Trying to add TXT record to parent zone domain.com with name _acme-challenge.my
```

## Troubleshooting

### Common Issues

1. **"No matching domain found"**:
   - Verify your domain is configured in Dynu
   - Check your API credentials

2. **Permission denied**:
   - Check credentials file permissions: `chmod 600 ~/dynu-credentials.ini`

3. **DNS propagation timeout**:
   - Increase `--dns-dynu-propagation-seconds` (try 300 for 5 minutes)

4. **Plugin not found**:
   - Run `pip install -e .` to install in development mode
   - Check `certbot plugins` output

5. **"No module named certbot.\_\_main\_\_"**:
   - Use `python run_certbot.py` instead of `python -m certbot`
   - The wrapper script handles certbot execution properly

6. **"Command 'certbot' not found"**:
   - Use the provided wrapper: `python run_certbot.py`
   - Or install certbot system-wide: `sudo apt install certbot`

### Debug Commands

```bash
# Test DNS resolution
nslookup your-domain.com

# Test API connectivity (if you have curl)
curl -H "Authorization: Bearer your-api-key" https://api.dynu.com/v2/domains

# Check DNS propagation
dig TXT _acme-challenge.your-domain.com @8.8.8.8
```

## Testing Scenarios

### Scenario 1: Apex Domain

- Domain: `domain.com`
- Expected: Direct creation of `_acme-challenge` in `domain.com` zone
- Should work immediately

### Scenario 2: Single Subdomain  

- Domain: `my.domain.com`
- Expected: Fallback to `domain.com` zone with record `_acme-challenge.my`
- Tests the main fix

### Scenario 3: Deep Subdomain

- Domain: `api.my.domain.com`  
- Expected: Fallback to `domain.com` zone with record `_acme-challenge.api.my`
- Tests multiple level fallback

### Scenario 4: Wildcard Certificate

- Domain: `*.domain.com`
- Expected: Creation of `_acme-challenge` in `domain.com` zone
- Should work like apex domain

## Success Criteria

✅ Unit tests pass
✅ Local logic tests pass  
✅ Dry run completes without errors
✅ DNS records are created and deleted properly
✅ Subdomain certificates can be obtained
✅ No manual DNS record creation required

## Next Steps

After successful local testing:

1. Test with staging Let's Encrypt environment first
2. Consider creating CI/CD pipeline for automated testing
3. Test with multiple domain configurations
4. Document any edge cases discovered

## Security Notes

- Never commit credentials files to version control
- Use restrictive file permissions on credentials files
- Consider using environment variables for credentials in production
- Test with non-production domains first
