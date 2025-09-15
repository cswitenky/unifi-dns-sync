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
    def load_hostnames_from_json(file_path: str = None) -> List[dict]:
        """
        Load the list of desired hostnames from a JSON file or stdin.

        Supported formats:
          - Simple list of hostnames: ["a.example.com", "b.example.com"]
          - List of objects (hostname + single ip), e.g.:
              [{"hostname": "a.example.com", "ip": "1.2.3.4"},
               {"b.example.com": "3.3.3.3"}]

        IMPORTANT: Each DNS entry may specify at most one IP. If a list of IPs is provided
        it must contain exactly one element; otherwise a ValueError is raised.

        Returns a normalized list of dicts with keys:
          - 'hostname': str
          - 'ip': Optional[str] (None means use default target IP)
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
                raise ValueError("JSON must contain a list of hostnames or host objects")

            normalized = []
            import ipaddress

            for item in hostnames:
                # Simple string entry -> hostname with no explicit IP
                if isinstance(item, str):
                    hostname = item.strip()
                    if not DNSSync.validate_hostname(hostname):
                        raise ValueError(f"Invalid hostname: {hostname}")
                    normalized.append({'hostname': hostname, 'ip': None})
                    continue

                # Object entry -> must contain hostname and optional ip (single)
                if isinstance(item, dict):
                    # Explicit object with 'hostname' key
                    if 'hostname' in item:
                        hostname = item.get('hostname')
                        if not isinstance(hostname, str) or not hostname.strip():
                            raise ValueError(f"Invalid hostname in object: {item}")
                        hostname = hostname.strip()
                        if not DNSSync.validate_hostname(hostname):
                            raise ValueError(f"Invalid hostname: {hostname}")

                        ip_val = None
                        if 'ip' in item and item.get('ip') is not None:
                            ip_val = item.get('ip')
                        elif 'ips' in item and item.get('ips') is not None:
                            ip_val = item.get('ips')

                        if ip_val is None:
                            ip = None
                        elif isinstance(ip_val, str):
                            try:
                                ipaddress.ip_address(ip_val)
                            except Exception:
                                raise ValueError(f"Invalid IP address: {ip_val}")
                            ip = ip_val
                        elif isinstance(ip_val, list):
                            if len(ip_val) != 1:
                                raise ValueError(f"Each hostname may specify only one IP. Got: {ip_val}")
                            single_ip = ip_val[0]
                            if not isinstance(single_ip, str):
                                raise ValueError(f"Invalid IP entry: {single_ip} in {item}")
                            try:
                                ipaddress.ip_address(single_ip)
                            except Exception:
                                raise ValueError(f"Invalid IP address: {single_ip}")
                            ip = single_ip
                        else:
                            raise ValueError(f"Invalid ip format for hostname {hostname}: {ip_val}")

                        normalized.append({'hostname': hostname, 'ip': ip})
                        continue

                    # Shorthand mapping {"host.example.com": "1.2.3.4"} or to list
                    if len(item) == 1:
                        key, value = next(iter(item.items()))
                        if not isinstance(key, str) or not key.strip():
                            raise ValueError(f"Invalid hostname key: {key}")
                        hostname = key.strip()
                        if not DNSSync.validate_hostname(hostname):
                            raise ValueError(f"Invalid hostname: {hostname}")

                        if value is None:
                            ip = None
                        elif isinstance(value, str):
                            try:
                                ipaddress.ip_address(value)
                            except Exception:
                                raise ValueError(f"Invalid IP address: {value}")
                            ip = value
                        elif isinstance(value, list):
                            if len(value) != 1:
                                raise ValueError(f"Each hostname may specify only one IP. Got: {value}")
                            single_ip = value[0]
                            if not isinstance(single_ip, str):
                                raise ValueError(f"Invalid IP entry: {single_ip} in {item}")
                            try:
                                ipaddress.ip_address(single_ip)
                            except Exception:
                                raise ValueError(f"Invalid IP address: {single_ip}")
                            ip = single_ip
                        else:
                            raise ValueError(f"Invalid value for hostname {hostname}: {value}")

                        normalized.append({'hostname': hostname, 'ip': ip})
                        continue

                # If we get here the item format is invalid
                raise ValueError(f"Invalid host entry: {item}")

            return normalized

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
    def filter_valid_hostnames(hostnames: List[object]) -> List[dict]:
        """
        Filter a list of host entries to only include valid ones.

        Accepts either strings or normalized dicts as produced by load_hostnames_from_json.
        Returns a list of normalized dicts with keys 'hostname' and 'ip'.
        """
        valid_hostnames = []
        for item in hostnames:
            # If provided a plain string, validate and normalize
            if isinstance(item, str):
                if DNSSync.validate_hostname(item):
                    valid_hostnames.append({'hostname': item.strip(), 'ip': None})
                else:
                    logger.warning(f"Skipping invalid hostname: {item}")
                continue

            # If already a normalized dict
            if isinstance(item, dict) and 'hostname' in item:
                hostname = item.get('hostname')
                if DNSSync.validate_hostname(hostname):
                    # keep ip as-is (may be None)
                    valid_hostnames.append({'hostname': hostname.strip(), 'ip': item.get('ip')})
                else:
                    logger.warning(f"Skipping invalid hostname: {hostname}")
                continue

            logger.warning(f"Skipping invalid hostname entry: {item}")

        return valid_hostnames
