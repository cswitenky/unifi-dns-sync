"""
Tests for the DNS synchronization functionality
"""

import pytest
from unittest.mock import Mock, patch
from unifi_dns_sync.sync import DNSSync


class TestDNSSync:
    """Test cases for the DNSSync class."""
    
    def test_validate_hostname_valid(self):
        """Test hostname validation with valid hostnames."""
        valid_hostnames = [
            "example.com",
            "sub.example.com",
            "test-server.local",
            "server1.domain.org",
            "a.b.c.d.e"
        ]
        
        for hostname in valid_hostnames:
            assert DNSSync.validate_hostname(hostname) is True
    
    def test_validate_hostname_invalid(self):
        """Test hostname validation with invalid hostnames."""
        invalid_hostnames = [
            "",
            "   ",
            None,
            "example..com",
            ".example.com",
            "example.com.",
            "ex ample.com",
            "example$.com"
        ]
        
        for hostname in invalid_hostnames:
            assert DNSSync.validate_hostname(hostname) is False
    
    def test_filter_valid_hostnames(self):
        """Test filtering of valid hostnames."""
        hostnames = [
            "valid.com",
            "",
            "also-valid.org",
            "invalid..hostname",
            "another.valid.host"
        ]
        
        result = DNSSync.filter_valid_hostnames(hostnames)
        expected = ["valid.com", "also-valid.org", "another.valid.host"]
        
        assert result == expected
    
    def test_load_hostnames_from_json_file(self, tmp_path):
        """Test loading hostnames from a JSON file."""
        # Create a temporary JSON file
        json_file = tmp_path / "test_hostnames.json"
        hostnames_data = ["test1.com", "test2.org", "test3.net"]
        json_file.write_text(str(hostnames_data).replace("'", '"'))
        
        result = DNSSync.load_hostnames_from_json(str(json_file))
        assert result == hostnames_data
    
    def test_load_hostnames_invalid_json(self, tmp_path):
        """Test loading hostnames from invalid JSON."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("invalid json content")
        
        with pytest.raises(Exception):
            DNSSync.load_hostnames_from_json(str(json_file))
    
    def test_load_hostnames_file_not_found(self):
        """Test loading hostnames from non-existent file."""
        with pytest.raises(FileNotFoundError):
            DNSSync.load_hostnames_from_json("nonexistent.json")
