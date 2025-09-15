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
        help="Path to JSON file containing hostnames or host-to-IP mappings, or '-' for stdin (default: stdin)"
    )
    
    parser.add_argument(
        "--controller", 
        required=True, 
        help="Unifi controller URL (e.g., https://10.0.0.1)"
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
        default="10.0.0.123", 
        help="IP address for DNS records (default: 10.0.0.123)"
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


def run_dry_run(dns_manager: UnifiDNSManager, desired_entries: list, show_diff: bool) -> None:
    """Run in dry-run mode to show what would change.

    desired_entries: list of normalized dicts with 'hostname' and optional 'ip'.
    """
    logger.info("DRY RUN MODE - No changes will be made")
    logger.info(f"Would sync these entries: {desired_entries}")

    if show_diff:
        # Get current state and show what would change
        existing_records = dns_manager.get_existing_dns_records()
        # Build existing map hostname -> set of ips
        existing_map = {}
        for record in existing_records:
            if record.get('record_type') != 'A':
                continue
            existing_map.setdefault(record.get('key'), set()).add(record.get('value'))

        # Normalize desired entries into hostname -> single ip mapping
        desired_map = {}
        for entry in desired_entries:
            hostname = entry.get('hostname') if isinstance(entry, dict) else entry
            ip = entry.get('ip') if isinstance(entry, dict) else None
            if ip is None:
                desired_map[hostname] = {dns_manager.target_ip}
            else:
                desired_map[hostname] = {ip}

        # Construct changes structure compatible with _display_diff
        changes = {'created': [], 'deleted': [], 'unchanged': []}

        desired_hostnames = set(desired_map.keys())
        existing_hostnames = set(existing_map.keys())

        for hostname in desired_hostnames:
            desired_ips = desired_map.get(hostname, {dns_manager.target_ip})
            existing_ips = existing_map.get(hostname, set())

            # Since only one IP is allowed per hostname, take the single desired IP
            desired_ip = next(iter(desired_ips))

            if desired_ip in existing_ips:
                changes['unchanged'].append((hostname, desired_ip))
            else:
                changes['created'].append((hostname, desired_ip))

            # Any existing IPs that are not the desired one should be deleted
            for ip in sorted(existing_ips - {desired_ip}):
                changes['deleted'].append((hostname, ip))

        # Hostnames present in existing but not desired should be deleted entirely
        for hostname in sorted(existing_hostnames - desired_hostnames):
            for ip in sorted(existing_map.get(hostname, [])):
                changes['deleted'].append((hostname, ip))

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
        # Load desired hostnames/entries
        if args.json_file == '-':
            logger.info("Loading hostnames from stdin...")
        else:
            logger.info(f"Loading hostnames from {args.json_file}")

        entries = DNSSync.load_hostnames_from_json(args.json_file)

        # Filter and validate entries
        valid_entries = DNSSync.filter_valid_hostnames(entries)
        if len(valid_entries) != len(entries):
            logger.warning(f"Filtered {len(entries) - len(valid_entries)} invalid host entries")

        logger.info(f"Loaded {len(valid_entries)} valid host entries")

        # Initialize DNS manager
        dns_manager = UnifiDNSManager(
            controller_url=args.controller,
            username=args.username,
            password=args.password,
            target_ip=args.target_ip
        )

        if args.dry_run:
            run_dry_run(dns_manager, valid_entries, args.show_diff)
            return

        # Perform synchronization
        results = dns_manager.sync_dns_records(valid_entries, show_diff=args.show_diff)
        
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
