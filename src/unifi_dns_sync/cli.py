"""
Command Line Interface for Unifi DNS Sync

This module provides the command line interface for the unifi-dns-sync tool.
"""

import argparse
import logging
import sys
from typing import Dict

from .dns_manager import UnifiDNSManager
from .sync import DNSSync

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    if verbose:
        logger.info("Debug logging enabled")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Synchronize DNS records with Unifi controller",
        prog="unifi-dns-sync"
    )
    
    parser.add_argument(
        "json_file", 
        nargs="?", 
        default="-", 
        help="Path to JSON file containing list of hostnames, or '-' for stdin (default: stdin)"
    )
    
    parser.add_argument(
        "--controller", 
        required=True, 
        help="Unifi controller URL (e.g., https://10.1.0.1)"
    )
    
    parser.add_argument(
        "--username", 
        required=True, 
        help="Unifi controller username"
    )
    
    parser.add_argument(
        "--password", 
        required=True, 
        help="Unifi controller password"
    )
    
    parser.add_argument(
        "--target-ip", 
        default="10.0.10.31", 
        help="IP address for DNS records (default: 10.0.10.31)"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be done without making changes"
    )
    
    parser.add_argument(
        "--show-diff", 
        action="store_true", 
        help="Show detailed diff of DNS record changes"
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable debug logging"
    )
    
    return parser


def run_dry_run(dns_manager: UnifiDNSManager, hostnames: list, show_diff: bool) -> None:
    """Run in dry-run mode to show what would change."""
    logger.info("DRY RUN MODE - No changes will be made")
    logger.info(f"Would sync these hostnames: {hostnames}")
    
    if show_diff:
        # Get current state and show what would change
        existing_records = dns_manager.get_existing_dns_records()
        existing_dict = {record['key']: record for record in existing_records 
                       if record.get('record_type') == 'A'}
        existing_set = set(existing_dict.keys())
        desired_set = set(hostnames)
        
        changes = {
            'created': list(desired_set - existing_set),
            'deleted': list(existing_set - desired_set),
            'unchanged': list(desired_set & existing_set)
        }
        
        logger.info("\nDRY RUN - PREVIEW OF CHANGES:")
        print()  # Add a blank line for better separation
        dns_manager._display_diff(changes)


def main() -> None:
    """Main function to run the DNS synchronization CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    try:
        # Load desired hostnames
        if args.json_file == '-':
            logger.info("Loading hostnames from stdin...")
        else:
            logger.info(f"Loading hostnames from {args.json_file}")
        
        hostnames = DNSSync.load_hostnames_from_json(args.json_file)
        
        # Filter valid hostnames
        valid_hostnames = DNSSync.filter_valid_hostnames(hostnames)
        if len(valid_hostnames) != len(hostnames):
            logger.warning(f"Filtered {len(hostnames) - len(valid_hostnames)} invalid hostnames")
        
        logger.info(f"Loaded {len(valid_hostnames)} valid hostnames")
        
        # Initialize DNS manager
        dns_manager = UnifiDNSManager(
            controller_url=args.controller,
            username=args.username,
            password=args.password,
            target_ip=args.target_ip
        )
        
        if args.dry_run:
            run_dry_run(dns_manager, valid_hostnames, args.show_diff)
            return
        
        # Perform synchronization
        results = dns_manager.sync_dns_records(valid_hostnames, show_diff=args.show_diff)
        
        # Report results
        logger.info("Synchronization completed successfully!")
        logger.info(f"Results: {results['created']} created, {results['deleted']} deleted, {results['existing']} existing")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
