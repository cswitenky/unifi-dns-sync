"""
DNS Manager for Unifi Controllers

This module provides the UnifiDNSManager class for managing DNS records on Unifi controllers.
"""

import json
import logging
import base64
from typing import List, Dict, Set, Optional
from urllib.parse import urljoin
import requests
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class UnifiDNSManager:
    """Manages DNS records on Unifi controllers."""
    
    def __init__(self, controller_url: str, username: str, password: str, target_ip: str = "10.0.10.31"):
        """
        Initialize the Unifi DNS Manager.
        
        Args:
            controller_url: Base URL of the Unifi controller (e.g., https://10.1.0.1)
            username: Unifi controller username
            password: Unifi controller password
            target_ip: IP address to assign to DNS records (default: 10.0.10.31)
        """
        self.controller_url = controller_url.rstrip('/')
        self.username = username
        self.password = password
        self.target_ip = target_ip
        self.session = requests.Session()
        self.session.verify = False  # For self-signed certificates
        self.token = None
        self.session_id = None
        self.csrf_token = None
        
        # Authenticate on initialization
        self._authenticate()
        
    def _extract_csrf_token_from_jwt(self, jwt_token: str) -> Optional[str]:
        """Extract CSRF token from JWT payload."""
        try:
            logger.debug(f"Extracting CSRF from JWT: {jwt_token[:50]}...")
            
            # JWT format: header.payload.signature
            parts = jwt_token.split('.')
            if len(parts) != 3:
                logger.warning(f"JWT has {len(parts)} parts, expected 3")
                return None
            
            # Decode the payload (second part)
            payload = parts[1]
            logger.debug(f"JWT payload (base64): {payload[:50]}...")
            
            # Add padding if needed for base64 decoding
            payload += '=' * (4 - len(payload) % 4)
            decoded_payload = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded_payload)
            
            logger.debug(f"JWT payload keys: {list(payload_data.keys())}")
            
            csrf_token = payload_data.get('csrfToken')
            if csrf_token:
                logger.debug(f"Found CSRF token: {csrf_token}")
            else:
                logger.warning("CSRF token not found in JWT payload")
                logger.debug(f"Full JWT payload: {payload_data}")
            
            return csrf_token
        except Exception as e:
            logger.warning(f"Failed to extract CSRF token from JWT: {e}")
            logger.debug(f"JWT token: {jwt_token}")
            return None
        
    def _authenticate(self) -> None:
        """Authenticate with the Unifi controller and get session tokens."""
        login_url = f"{self.controller_url}/api/auth/login"
        login_payload = {
            "username": self.username,
            "password": self.password,
            "token": "",
            "rememberMe": False
        }
        
        try:
            logger.info("Authenticating with Unifi controller...")
            response = self.session.post(login_url, json=login_payload, timeout=30)
            response.raise_for_status()
            
            # Extract tokens from response
            user_data = response.json()
            self.token = user_data.get('deviceToken')
            
            # Look for TOKEN cookie which contains the JWT with CSRF
            token_cookie = None
            for cookie in self.session.cookies:
                if cookie.name == 'TOKEN':
                    token_cookie = cookie.value
                    break
                elif cookie.name == 'JSESSIONID':
                    self.session_id = cookie.value
            
            # Extract CSRF token from the TOKEN cookie (not deviceToken)
            if token_cookie:
                logger.debug("Found TOKEN cookie, extracting CSRF from it")
                self.csrf_token = self._extract_csrf_token_from_jwt(token_cookie)
            elif self.token:
                logger.debug("No TOKEN cookie found, trying deviceToken")
                self.csrf_token = self._extract_csrf_token_from_jwt(self.token)
            
            if not self.token:
                raise ValueError("Failed to get authentication token from response")
            
            if not self.csrf_token:
                logger.warning("Failed to extract CSRF token from JWT")
            
            # Set up cookies for future requests (TOKEN cookie should already be set by session)
            if not token_cookie and self.token:
                self.session.cookies.set('TOKEN', self.token)
            
            logger.info(f"Authentication successful (CSRF token: {'found' if self.csrf_token else 'missing'})")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse authentication response: {e}")
            raise
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an authenticated request to the Unifi controller."""
        url = urljoin(self.controller_url, endpoint)
        
        # Add CSRF token to headers if available
        headers = kwargs.get('headers', {})
        if self.csrf_token:
            headers['x-csrf-token'] = self.csrf_token
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            logger.error(f"URL: {url}")
            logger.error(f"Method: {method}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
    
    def get_existing_dns_records(self) -> List[Dict]:
        """
        Get all existing static DNS records from the controller.
        
        Returns:
            List of DNS record dictionaries
        """
        logger.info("Fetching existing DNS records...")
        response = self._make_request("GET", "/proxy/network/v2/api/site/default/static-dns")
        records = response.json()
        logger.info(f"Found {len(records)} existing DNS records")
        return records
    
    def create_dns_record(self, hostname: str) -> Dict:
        """
        Create a new DNS A record.
        
        Args:
            hostname: The hostname/FQDN for the DNS record
            
        Returns:
            Created DNS record dictionary
        """
        payload = {
            "record_type": "A",
            "value": self.target_ip,
            "key": hostname,
            "enabled": True
        }
        
        logger.info(f"Creating DNS record: {hostname} -> {self.target_ip}")
        response = self._make_request(
            "POST", 
            "/proxy/network/v2/api/site/default/static-dns",
            json=payload
        )
        return response.json()
    
    def delete_dns_record(self, record_id: str, hostname: str = None) -> None:
        """
        Delete a DNS record by ID.
        
        Args:
            record_id: The ID of the DNS record to delete
            hostname: Optional hostname for logging purposes
        """
        log_msg = f"Deleting DNS record ID: {record_id}"
        if hostname:
            log_msg += f" ({hostname})"
        logger.info(log_msg)
        
        self._make_request(
            "DELETE", 
            f"/proxy/network/v2/api/site/default/static-dns/{record_id}"
        )
    
    def sync_dns_records(self, desired_hostnames: List[str], show_diff: bool = True) -> Dict[str, int]:
        """
        Synchronize DNS records with the desired list.
        
        Args:
            desired_hostnames: List of hostnames that should have DNS records
            show_diff: Whether to display a diff of changes
            
        Returns:
            Dictionary with counts of created, deleted, and existing records
        """
        # Get existing records
        existing_records = self.get_existing_dns_records()
        
        # Create sets for comparison
        desired_set = set(desired_hostnames)
        existing_dict = {record['key']: record for record in existing_records 
                        if record.get('record_type') == 'A'}
        existing_set = set(existing_dict.keys())
        
        # Find records to create and delete
        to_create = desired_set - existing_set
        to_delete = existing_set - desired_set
        existing_correct = desired_set & existing_set
        
        logger.info(f"Synchronization plan:")
        logger.info(f"  Records to create: {len(to_create)}")
        logger.info(f"  Records to delete: {len(to_delete)}")
        logger.info(f"  Records already correct: {len(existing_correct)}")
        
        # Store changes for diff display
        changes = {
            'created': [],
            'deleted': [],
            'unchanged': list(existing_correct)
        }
        
        # Create missing records
        created_count = 0
        for hostname in to_create:
            try:
                self.create_dns_record(hostname)
                changes['created'].append(hostname)
                created_count += 1
            except Exception as e:
                logger.error(f"Failed to create record for {hostname}: {e}")
        
        # Delete obsolete records
        deleted_count = 0
        for hostname in to_delete:
            try:
                record = existing_dict[hostname]
                self.delete_dns_record(record['_id'], hostname)
                changes['deleted'].append(hostname)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete record for {hostname}: {e}")
        
        # Display diff if there were changes
        if show_diff and (changes['created'] or changes['deleted']):
            self._display_diff(changes)
        elif not (changes['created'] or changes['deleted']):
            logger.info("No changes made - DNS records are already synchronized")
        
        return {
            'created': created_count,
            'deleted': deleted_count,
            'existing': len(existing_correct)
        }
    
    def _display_diff(self, changes: Dict[str, List[str]]) -> None:
        """Display a diff-style summary of DNS record changes."""
        print("\n" + "="*60)
        print("DNS RECORD CHANGES")
        print("="*60)
        
        # Show deletions (red/minus)
        if changes['deleted']:
            print(f"\n❌ DELETED ({len(changes['deleted'])} records):")
            for hostname in sorted(changes['deleted']):
                print(f"  - {hostname} -> {self.target_ip}")
        # Show additions (green/plus) 
        if changes['created']:
            print(f"\n✅ CREATED ({len(changes['created'])} records):")
            for hostname in sorted(changes['created']):
                print(f"  + {hostname} -> {self.target_ip}")
        
        # Show unchanged (for context)
        if changes['unchanged']:
            print(f"\n⚪ UNCHANGED ({len(changes['unchanged'])} records):")
            for hostname in sorted(changes['unchanged']):
                print(f"    {hostname} -> {self.target_ip}")
        
        print("\n" + "="*60)
        
        # Summary line
        total_changes = len(changes['created']) + len(changes['deleted'])
        print(f"SUMMARY: {total_changes} changes ({len(changes['created'])} created, {len(changes['deleted'])} deleted)")
        print("="*60)