#!/usr/bin/env python3
"""
Local testing script for certbot-dns-dynu-dev plugin
This script allows you to test the plugin logic without making actual API calls
"""

import sys
import os
import unittest
from unittest import mock
import tempfile

# Add the plugin to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'certbot_dns_dynu_dev'))

from certbot_dns_dynu_dev.dns_dynu import _DynuLexiconClient


class MockDynuLexiconClient(_DynuLexiconClient):
    """Mock version that doesn't make real API calls"""
    
    def __init__(self):
        # Don't call the parent constructor to avoid needing real credentials
        self.call_log = []
        self.should_fail_domains = set()
    
    def set_failing_domains(self, domains):
        """Set which domains should fail when accessed"""
        self.should_fail_domains = set(domains)
    
    def _mock_parent_add_txt_record(self, domain, record_name, record_content):
        """Mock the parent class add_txt_record method"""
        call_info = f"add_txt_record({domain}, {record_name}, {record_content})"
        self.call_log.append(call_info)
        print(f"API Call: {call_info}")
        
        if domain in self.should_fail_domains:
            raise Exception(f"No matching domain found: {domain}")
        
        print(f"✅ Successfully added TXT record: {record_name} = {record_content} in zone {domain}")
    
    def _mock_parent_del_txt_record(self, domain, record_name, record_content):
        """Mock the parent class del_txt_record method"""
        call_info = f"del_txt_record({domain}, {record_name}, {record_content})"
        self.call_log.append(call_info)
        print(f"API Call: {call_info}")
        
        if domain in self.should_fail_domains:
            raise Exception(f"No matching domain found: {domain}")
        
        print(f"✅ Successfully deleted TXT record: {record_name} = {record_content} from zone {domain}")


def test_subdomain_scenarios():
    """Test various subdomain scenarios"""
    
    print("="*60)
    print("TESTING SUBDOMAIN FALLBACK LOGIC")
    print("="*60)
    
    # Patch the parent class methods
    with mock.patch.object(_DynuLexiconClient.__bases__[0], 'add_txt_record') as mock_add, \
         mock.patch.object(_DynuLexiconClient.__bases__[0], 'del_txt_record') as mock_del:
        
        client = MockDynuLexiconClient()
        
        # Configure the mocks to call our tracking methods
        mock_add.side_effect = client._mock_parent_add_txt_record
        mock_del.side_effect = client._mock_parent_del_txt_record
        
        # Test Case 1: Subdomain certificate (subdomain zone doesn't exist)
        print("\n" + "─" * 50)
        print("Test Case 1: Certificate for my.domain.com")
        print("Expected: Should fail for my.domain.com zone, succeed for domain.com zone")
        print("─" * 50)
        
        client.set_failing_domains(['my.domain.com'])
        client.call_log = []
        
        try:
            client.add_txt_record('my.domain.com', '_acme-challenge', 'test-validation-token')
            print("Result: ✅ Success")
        except Exception as e:
            print(f"Result: ❌ Failed with: {e}")
        
        print(f"Total API calls made: {len(client.call_log)}")
        for call in client.call_log:
            print(f"  - {call}")
        
        # Test Case 2: Deep subdomain certificate
        print("\n" + "─" * 50)
        print("Test Case 2: Certificate for api.my.domain.com")
        print("Expected: Should fail for api.my.domain.com and my.domain.com, succeed for domain.com")
        print("─" * 50)
        
        client.set_failing_domains(['api.my.domain.com', 'my.domain.com'])
        client.call_log = []
        
        try:
            client.add_txt_record('api.my.domain.com', '_acme-challenge', 'test-validation-token')
            print("Result: ✅ Success")
        except Exception as e:
            print(f"Result: ❌ Failed with: {e}")
        
        print(f"Total API calls made: {len(client.call_log)}")
        for call in client.call_log:
            print(f"  - {call}")
        
        # Test Case 3: Apex domain certificate (should work immediately)
        print("\n" + "─" * 50)
        print("Test Case 3: Certificate for domain.com")
        print("Expected: Should succeed immediately for domain.com zone")
        print("─" * 50)
        
        client.set_failing_domains([])  # No domains should fail
        client.call_log = []
        
        try:
            client.add_txt_record('domain.com', '_acme-challenge', 'test-validation-token')
            print("Result: ✅ Success")
        except Exception as e:
            print(f"Result: ❌ Failed with: {e}")
        
        print(f"Total API calls made: {len(client.call_log)}")
        for call in client.call_log:
            print(f"  - {call}")
        
        # Test Case 4: Record deletion (subdomain)
        print("\n" + "─" * 50)
        print("Test Case 4: Delete TXT record for my.domain.com")
        print("Expected: Should fail for my.domain.com zone, succeed for domain.com zone")
        print("─" * 50)
        
        client.set_failing_domains(['my.domain.com'])
        client.call_log = []
        
        try:
            client.del_txt_record('my.domain.com', '_acme-challenge', 'test-validation-token')
            print("Result: ✅ Success")
        except Exception as e:
            print(f"Result: ❌ Failed with: {e}")
        
        print(f"Total API calls made: {len(client.call_log)}")
        for call in client.call_log:
            print(f"  - {call}")


def test_record_name_construction():
    """Test how record names are constructed for different scenarios"""
    
    print("\n" + "="*60)
    print("TESTING RECORD NAME CONSTRUCTION")
    print("="*60)
    
    test_cases = [
        ('my.domain.com', '_acme-challenge', 'domain.com', '_acme-challenge.my'),
        ('api.my.domain.com', '_acme-challenge', 'domain.com', '_acme-challenge.api.my'),
        ('test.api.my.domain.com', '_acme-challenge', 'domain.com', '_acme-challenge.test.api.my'),
        ('domain.com', '_acme-challenge', 'domain.com', '_acme-challenge'),
    ]
    
    for original_domain, record_name, target_zone, expected_adjusted_name in test_cases:
        print(f"\nScenario: Certificate for {original_domain}")
        print(f"Target zone: {target_zone}")
        print(f"Original record name: {record_name}")
        print(f"Expected adjusted name: {expected_adjusted_name}")
        
        # Simulate the logic in the plugin
        domain_parts = original_domain.split('.')
        zone_parts = target_zone.split('.')
        
        # Find how many parts to include in the subdomain prefix
        zone_part_count = len(zone_parts)
        subdomain_part_count = len(domain_parts) - zone_part_count
        
        if subdomain_part_count > 0:
            subdomain_parts = '.'.join(domain_parts[:subdomain_part_count])
            adjusted_name = f"{record_name}.{subdomain_parts}" if record_name else subdomain_parts
        else:
            adjusted_name = record_name
        
        print(f"Calculated adjusted name: {adjusted_name}")
        
        if adjusted_name == expected_adjusted_name:
            print("✅ Correct!")
        else:
            print("❌ Mismatch!")


def create_test_credentials():
    """Create a temporary credentials file for testing"""
    
    print("\n" + "="*60)
    print("CREATING TEST CREDENTIALS FILE")
    print("="*60)
    
    # Create a temporary credentials file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write("dns_dynu_auth_token = 00000000-0000-0000-0000-000000000000\n")
        temp_file = f.name
    
    print(f"Created temporary credentials file: {temp_file}")
    print("Contents:")
    with open(temp_file, 'r') as f:
        print(f.read())
    
    print("\nTo use this with certbot, you would run:")
    print(f"certbot certonly \\")
    print(f"  --authenticator dns-dynu \\")
    print(f"  --dns-dynu-credentials {temp_file} \\")
    print(f"  -d your-domain.com")
    
    return temp_file


def main():
    """Main testing function"""
    
    print("🧪 Local Testing for certbot-dns-dynu-dev Plugin")
    print("This script tests the subdomain fallback logic without making real API calls")
    
    # Run the tests
    test_subdomain_scenarios()
    test_record_name_construction()
    
    # Create test credentials
    cred_file = create_test_credentials()
    
    print("\n" + "="*60)
    print("TESTING SUMMARY")
    print("="*60)
    print("✅ Plugin logic tests completed")
    print("✅ Record name construction tests completed") 
    print("✅ Test credentials file created")
    
    print(f"\nTo clean up, delete: {cred_file}")
    
    print("\n💡 Next Steps:")
    print("1. Install the plugin: pip install -e .")
    print("2. Get real Dynu API credentials")
    print("3. Test with a real domain you control")
    print("4. Use --dry-run flag first for safety")


if __name__ == "__main__":
    main()
