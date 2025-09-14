"""
DNS Synchronization utilities

This module provides utilities for loading configuration files and managing DNS synchronization.
"""

import json
import sys
import logging
from typing import List

logger = logging.getLogger(__name__)


class DNSSync:
    """High-level DNS synchronization utilities."""
    
    @staticmethod
    def load_hostnames_from_json(file_path: str = None) -> List[str]:
        """
        Load the list of desired hostnames from a JSON file or stdin.
        
        Args:
            file_path: Path to the JSON file containing the hostname list, or None to read from stdin
            
        Returns:
            List of hostnames
        """
        try:
            if file_path is None or file_path == '-':
                # Read from stdin
                logger.info("Reading hostnames from stdin...")
                json_data = sys.stdin.read()
                hostnames = json.loads(json_data)
            else:
                # Read from file
                logger.info(f"Reading hostnames from {file_path}")
                with open(file_path, 'r') as f:
                    hostnames = json.load(f)
            
            if not isinstance(hostnames, list):
                raise ValueError("JSON must contain a list of hostnames")
            
            # Validate hostnames
            for hostname in hostnames:
                if not isinstance(hostname, str) or not hostname.strip():
                    raise ValueError(f"Invalid hostname: {hostname}")
            
            return [hostname.strip() for hostname in hostnames]
        
        except FileNotFoundError:
            logger.error(f"JSON file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading hostnames: {e}")
            raise
    
    @staticmethod
    def validate_hostname(hostname: str) -> bool:
        """
        Validate a hostname string.
        
        Args:
            hostname: The hostname to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not hostname or not isinstance(hostname, str):
            return False
        
        # Basic validation - you could make this more strict
        hostname = hostname.strip()
        if not hostname:
            return False
        
        # Check for valid characters and basic format
        import re
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]*[a-zA-Z0-9])?$'
        return bool(re.match(pattern, hostname))
    
    @staticmethod
    def filter_valid_hostnames(hostnames: List[str]) -> List[str]:
        """
        Filter a list of hostnames to only include valid ones.
        
        Args:
            hostnames: List of hostnames to filter
            
        Returns:
            List of valid hostnames
        """
        valid_hostnames = []
        for hostname in hostnames:
            if DNSSync.validate_hostname(hostname):
                valid_hostnames.append(hostname.strip())
            else:
                logger.warning(f"Skipping invalid hostname: {hostname}")
        
        return valid_hostnames
