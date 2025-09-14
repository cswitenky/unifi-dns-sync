# Unifi DNS Synchronization Tool

A modern Python package for synchronizing DNS A records between JSON configuration files and Unifi controllers. The tool automatically creates missing records and removes obsolete ones.

## Features

- **Sync DNS Records**: Automatically create and delete DNS records based on a JSON list
- **Multiple Controller Support**: Works with any Unifi controller
- **Dry Run Mode**: Test what changes would be made without actually making them
- **Comprehensive Logging**: Detailed logs of all operations
- **Error Handling**: Robust error handling and reporting
- **Modern Python Package**: Proper package structure with setuptools and pip installation
- **Configuration Management**: Support for configuration files and environment variables
- **Comprehensive Testing**: Unit tests with pytest

## Installation

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/cswitenky/unifi-dns-sync.git
   cd unifi-dns-sync
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

3. Or install with development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### From PyPI (when published)

```bash
pip install unifi-dns-sync
```

## Quick Start

### Method 1: Command Line Arguments

```bash
unifi-dns-sync config/dns-records.json \
  --controller https://10.0.0.1 \
  --username your-username \
  --password your-password
```
Note: For those with Ubiquiti accounts with MFA enabled, you can create a local account on the Unifi controller with approporiate permissions and use those credentials instead of your Ubiquiti account credentials.

### Method 2: Configuration File

1. Create a configuration file:
   ```bash
   cp config/config.example.json config.json
   ```

2. Edit `config.json` with your settings:
   ```json
   {
     "controller": {
       "url": "https://10.1.0.1",
       "username": "your-username",
       "password": "your-password"
     },
     "dns": {
       "target_ip": "10.0.10.31",
       "show_diff": true
     },
     "hostnames_file": "config/dns-records.json"
   }
   ```

3. Run the tool:
   ```bash
   unifi-dns-sync
   ```

### Method 3: Environment Variables

Set the following environment variables:
```bash
export UNIFI_CONTROLLER_URL="https://10.1.0.1"
export UNIFI_USERNAME="your-username"
export UNIFI_PASSWORD="your-password"
export UNIFI_TARGET_IP="10.0.10.31"
export UNIFI_HOSTNAMES_FILE="config/dns-records.json"
```

Then run:
```bash
unifi-dns-sync
```

## Usage

### Command Line Options

- `json_file`: Path to JSON file containing list of hostnames, or `-` for stdin (optional, defaults to stdin)
- `--controller`: Unifi controller URL, e.g., `https://10.1.0.1` (required)
- `--username`: Unifi controller username (required)
- `--password`: Unifi controller password (required)
- `--target-ip`: IP address for DNS records (default: `10.0.10.31`)
- `--dry-run`: Show what would be done without making changes
- `--show-diff`: Show detailed diff of DNS record changes
- `--verbose, -v`: Enable debug logging

### Examples

#### Using a JSON File
```bash
unifi-dns-sync config/dns-records.json \
  --controller https://10.1.0.1 \
  --username admin \
  --password secret \
  --target-ip 10.0.10.31
```

#### Using stdin
```bash
echo '["host1.example.com", "host2.example.com"]' | \
  unifi-dns-sync - \
  --controller https://10.1.0.1 \
  --username admin \
  --password secret
```

#### Dry Run Mode
```bash
unifi-dns-sync config/dns-records.json \
  --controller https://10.1.0.1 \
  --username admin \
  --password secret \
  --dry-run \
  --show-diff
```

## Development

### Project Structure

```
unifi-dns-sync/
├── src/
│   └── unifi_dns_sync/
│       ├── __init__.py
│       ├── cli.py              # Command line interface
│       ├── config.py           # Configuration management
│       ├── dns_manager.py      # Unifi DNS API client
│       └── sync.py             # Synchronization utilities
├── tests/
│   ├── __init__.py
│   ├── test_dns_manager.py
│   └── test_sync.py
├── config/
│   ├── dns-records.json        # DNS hostnames configuration
│   ├── config.example.json     # Example configuration file
│   └── .env                    # Environment variables (if using)
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
├── pyproject.toml             # Modern Python packaging
├── Makefile                   # Development tasks
└── README.md
```

### Development Setup

1. Clone and install in development mode:
   ```bash
   git clone https://github.com/cswitenky/unifi-dns-sync.git
   cd unifi-dns-sync
   make install-dev
   ```

2. Run tests:
   ```bash
   make test
   ```

3. Run linting:
   ```bash
   make lint
   ```

4. Format code:
   ```bash
   make format
   ```

### Available Make Targets

- `make install` - Install the package in development mode
- `make install-dev` - Install with development dependencies
- `make test` - Run tests
- `make test-cov` - Run tests with coverage
- `make lint` - Run linting checks
- `make format` - Format code with black
- `make clean` - Clean build artifacts
- `make build` - Build the package
- `make sample-config` - Create a sample configuration file

## Configuration

### JSON Hostnames File

The hostnames file should contain a JSON array of hostnames:

```json
[
    "service1.example.com",
    "service2.example.com",
    "api.example.com"
]
```

### Configuration File Format

```json
{
  "controller": {
    "url": "https://10.1.0.1",
    "username": "admin",
    "password": "password",
    "name": "Main Controller"
  },
  "dns": {
    "target_ip": "10.0.10.31",
    "show_diff": true,
    "dry_run": false
  },
  "hostnames_file": "config/dns-records.json",
  "verbose": false
}
```

### Environment Variables

- `UNIFI_CONTROLLER_URL`: Controller URL
- `UNIFI_USERNAME`: Username
- `UNIFI_PASSWORD`: Password  
- `UNIFI_TARGET_IP`: Target IP address
- `UNIFI_HOSTNAMES_FILE`: Path to hostnames file
- `UNIFI_SHOW_DIFF`: Show diff (true/false)
- `UNIFI_DRY_RUN`: Dry run mode (true/false)
- `UNIFI_VERBOSE`: Verbose logging (true/false)

## Requirements

- Python 3.8+
- requests >= 2.28.0
- urllib3 >= 1.26.0

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.
  --controller https://10.1.0.1 \
  --username admin \
  --password mypassword
```

#### Using stdin with echo
```bash
echo '["bazarr.switenky.com", "radarr.switenky.com"]' | \
python3 unifi-sync.py \
  --controller https://10.1.0.1 \
  --username admin \
  --password mypassword
```

#### Using stdin with heredoc
```bash
python3 unifi-sync.py --controller https://10.1.0.1 --username admin --password mypassword << 'EOF'
[
    "bazarr.switenky.com",
    "radarr.switenky.com",
    "sonarr.switenky.com"
]
EOF
```

#### Using stdin with pipe from file
```bash
cat dns-records.json | python3 unifi-sync.py \
  --controller https://10.1.0.1 \
  --username admin \
  --password mypassword
```

#### Dry Run (Test Mode)
```bash
python3 unifi-sync.py dns-records.json \
  --controller https://10.1.0.1 \
  --username admin \
  --password mypassword \
  --dry-run
```

#### Sync with Custom Target IP
```bash
echo '["test.switenky.com"]' | python3 unifi-sync.py \
  --controller https://10.0.10.1 \
  --username admin \
  --password mypassword \
  --target-ip 192.168.1.100
```

#### Sync Multiple Controllers
```bash
# Frederick Unifi
echo '["service1.switenky.com", "service2.switenky.com"]' | \
python3 unifi-sync.py \
  --controller https://10.1.0.1 \
  --username admin \
  --password mypassword

# Seattle Unifi  
echo '["service1.switenky.com", "service2.switenky.com"]' | \
python3 unifi-sync.py \
  --controller https://10.0.10.1 \
  --username admin \
  --password mypassword
```

#### Dynamic JSON Generation
```bash
# Generate JSON list from environment or other sources
SERVICES=("bazarr" "radarr" "sonarr" "jellyfin")
JSON_ARRAY=$(printf '"%s.switenky.com",' "${SERVICES[@]}" | sed 's/,$//')
echo "[$JSON_ARRAY]" | python3 unifi-sync.py \
  --controller https://10.1.0.1 \
  --username admin \
  --password mypassword
```

## JSON File Format

The JSON file should contain a simple list of hostnames:

```json
[
    "bazarr.switenky.com",
    "radarr.switenky.com", 
    "sonarr.switenky.com",
    "jellyfin.switenky.com",
    "portainer.switenky.com"
]
```

## How It Works

1. **Load Configuration**: Reads the list of desired hostnames from the JSON file
2. **Fetch Existing Records**: Gets all current DNS A records from the Unifi controller
3. **Compare and Plan**: Determines which records need to be created or deleted
4. **Execute Changes**: Creates missing records and removes obsolete ones
5. **Report Results**: Logs the number of records created, deleted, and unchanged

## Environment Variables

You can also set credentials via environment variables:

```bash
export UNIFI_USERNAME="admin"
export UNIFI_PASSWORD="mypassword"

python3 unifi-sync.py dns-records.json --controller https://10.1.0.1
```

## Integration with Ansible

This script can be easily integrated into your existing Ansible playbooks:

```yaml
- name: Sync DNS records
  command: >
    python3 /path/to/unifi-sync.py /path/to/dns-records.json
    --controller https://{{ unifi_controller_ip }}
    --username {{ unifi_username }}
    --password {{ unifi_password }}
  delegate_to: localhost
```

## Troubleshooting

### SSL Certificate Issues
The script disables SSL verification for self-signed certificates. If you're using valid certificates, you can modify the script to enable verification.

### Authentication Issues
- Ensure your username and password are correct
- Check that the user has sufficient privileges on the Unifi controller
- Verify the controller URL is accessible

### Network Issues
- Ensure the script can reach the Unifi controller
- Check firewall rules and network connectivity
- Verify the controller is running and responding

## Security Notes

- Store credentials securely (use environment variables or secure vaults)
- Consider using API keys instead of passwords when available
- Limit network access to the Unifi controllers
- Run the script from a secure, controlled environment
