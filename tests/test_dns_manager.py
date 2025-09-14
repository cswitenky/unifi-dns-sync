"""
Tests for the DNS manager functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from unifi_dns_sync.dns_manager import UnifiDNSManager


class TestUnifiDNSManager:
    """Test cases for the UnifiDNSManager class."""
    
    @patch('unifi_dns_sync.dns_manager.requests.Session')
    def test_init_and_authentication(self, mock_session_class):
        """Test initialization and authentication."""
        # Mock session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {'deviceToken': 'fake_token'}
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        # Mock cookies
        mock_cookie = Mock()
        mock_cookie.name = 'TOKEN'
        mock_cookie.value = 'fake.jwt.token'
        mock_session.cookies = [mock_cookie]
        
        with patch.object(UnifiDNSManager, '_extract_csrf_token_from_jwt') as mock_extract:
            mock_extract.return_value = 'fake_csrf'
            
            # Initialize manager
            manager = UnifiDNSManager(
                controller_url="https://test.local",
                username="testuser",
                password="testpass"
            )
            
            # Verify authentication was called
            mock_session.post.assert_called_once()
            assert manager.token == 'fake_token'
            assert manager.csrf_token == 'fake_csrf'
    
    def test_url_cleanup(self):
        """Test that controller URL is properly cleaned."""
        with patch.object(UnifiDNSManager, '_authenticate'):
            manager = UnifiDNSManager(
                controller_url="https://test.local/",
                username="testuser",
                password="testpass"
            )
            assert manager.controller_url == "https://test.local"
    
    @patch('unifi_dns_sync.dns_manager.requests.Session')
    def test_make_request_with_csrf(self, mock_session_class):
        """Test making requests with CSRF token."""
        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock authentication
        with patch.object(UnifiDNSManager, '_authenticate'):
            manager = UnifiDNSManager(
                controller_url="https://test.local",
                username="testuser",
                password="testpass"
            )
            manager.csrf_token = "test_csrf"
            
            # Mock successful response
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_session.request.return_value = mock_response
            
            # Make a request
            result = manager._make_request("GET", "/api/test")
            
            # Verify the request was made with CSRF header
            mock_session.request.assert_called_once()
            args, kwargs = mock_session.request.call_args
            assert kwargs['headers']['x-csrf-token'] == "test_csrf"
            assert result == mock_response
