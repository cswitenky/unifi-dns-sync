"""
Unifi DNS Synchronization Package

Automatically sync DNS A records on Unifi controllers.
"""

__version__ = "1.0.0"
__author__ = "cswitenky"
__email__ = ""
__description__ = "Automatically sync DNS A records on Unifi controllers"

from .dns_manager import UnifiDNSManager
from .sync import DNSSync

__all__ = ["UnifiDNSManager", "DNSSync"]
