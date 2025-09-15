"""
Configuration management for Unifi DNS Sync

This module provides configuration loading and validation functionality.
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ControllerConfig:
    """Configuration for a Unifi controller."""
    url: str
    username: str
    password: str
    
    def __post_init__(self):
        # Clean up URL
        self.url = self.url.rstrip('/')
        if not self.url.startswith(('http://', 'https://')):
            self.url = f"https://{self.url}"


@dataclass
class DNSConfig:
    """Configuration for DNS settings."""
    target_ip: str = "10.0.0.123"
    show_diff: bool = True
    dry_run: bool = False


@dataclass
class AppConfig:
    """Main application configuration."""
    controller: ControllerConfig
    dns: DNSConfig
    hostnames_file: Optional[str] = None
    verbose: bool = False
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AppConfig':
        """Create AppConfig from dictionary."""
        controller_data = config_dict.get('controller', {})
        dns_data = config_dict.get('dns', {})
        
        controller = ControllerConfig(
            url=controller_data.get('url', ''),
            username=controller_data.get('username', ''),
            password=controller_data.get('password', '')
        )
        
        dns = DNSConfig(
            target_ip=dns_data.get('target_ip', '10.0.0.123'),
            show_diff=dns_data.get('show_diff', True),
            dry_run=dns_data.get('dry_run', False)
        )
        
        return cls(
            controller=controller,
            dns=dns,
            hostnames_file=config_dict.get('hostnames_file'),
            verbose=config_dict.get('verbose', False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert AppConfig to dictionary."""
        return {
            'controller': {
                'url': self.controller.url,
                'username': self.controller.username,
                'password': self.controller.password
            },
            'dns': {
                'target_ip': self.dns.target_ip,
                'show_diff': self.dns.show_diff,
                'dry_run': self.dns.dry_run
            },
            'hostnames_file': self.hostnames_file,
            'verbose': self.verbose
        }


class ConfigLoader:
    """Handles loading configuration from various sources."""
    
    @staticmethod
    def load_from_file(config_path: str) -> AppConfig:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            return AppConfig.from_dict(config_dict)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise
    
    @staticmethod
    def load_from_env() -> Optional[AppConfig]:
        """Load configuration from environment variables."""
        controller_url = os.getenv('UNIFI_CONTROLLER_URL')
        username = os.getenv('UNIFI_USERNAME')
        password = os.getenv('UNIFI_PASSWORD')
        
        if not all([controller_url, username, password]):
            return None
        
        controller = ControllerConfig(
            url=controller_url,
            username=username,
            password=password
        )
        
        dns = DNSConfig(
            target_ip=os.getenv('UNIFI_TARGET_IP', '10.0.0.123'),
            show_diff=os.getenv('UNIFI_SHOW_DIFF', 'true').lower() == 'true',
            dry_run=os.getenv('UNIFI_DRY_RUN', 'false').lower() == 'true'
        )
        
        return AppConfig(
            controller=controller,
            dns=dns,
            hostnames_file=os.getenv('UNIFI_HOSTNAMES_FILE'),
            verbose=os.getenv('UNIFI_VERBOSE', 'false').lower() == 'true'
        )
    
    @staticmethod
    def save_to_file(config: AppConfig, config_path: str) -> None:
        """Save configuration to JSON file."""
        config_dict = config.to_dict()
        # Remove password before saving for security
        config_dict['controller']['password'] = '***REDACTED***'
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Configuration saved to {config_path} (password redacted)")


def find_config_file() -> Optional[str]:
    """Find configuration file in common locations."""
    possible_paths = [
        'config.json',
        'unifi-dns-sync.json',
        os.path.expanduser('~/.config/unifi-dns-sync/config.json'),
        '/etc/unifi-dns-sync/config.json'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found configuration file: {path}")
            return path
    
    return None
