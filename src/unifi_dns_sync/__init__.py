"""
Unifi DNS Synchronization Package

A Python package for synchronizing DNS A records between JSON configuration files 
and Unifi controllers.
"""

__version__ = "1.0.0"
__author__ = "cswitenky"
__email__ = ""
__description__ = "Synchronize DNS records with Unifi controllers"

from .dns_manager import UnifiDNSManager
from .sync import DNSSync

__all__ = ["UnifiDNSManager", "DNSSync"]
