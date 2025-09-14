# Unifi DNS Sync - Developer Documentation

## Architecture Overview

The Unifi DNS Sync tool is designed with a modular architecture that separates concerns and makes the codebase maintainable and testable.

### Core Components

#### 1. `dns_manager.py` - UnifiDNSManager Class
- Handles all communication with Unifi controllers
- Manages authentication and session handling
- Provides methods for CRUD operations on DNS records
- Handles JWT token extraction and CSRF token management

#### 2. `sync.py` - DNSSync Utilities
- Provides utilities for hostname validation
- Handles loading and parsing of JSON configuration files
- Contains filtering and validation logic

#### 3. `config.py` - Configuration Management
- Manages application configuration from multiple sources
- Supports JSON files, environment variables
- Provides configuration validation and defaults

#### 4. `cli.py` - Command Line Interface
- Implements the command-line interface using argparse
- Orchestrates the synchronization process
- Handles dry-run mode and output formatting

## API Documentation

### UnifiDNSManager

```python
class UnifiDNSManager:
    def __init__(self, controller_url: str, username: str, password: str, target_ip: str = "10.0.10.31")
```

**Methods:**
- `get_existing_dns_records() -> List[Dict]` - Fetch all DNS records
- `create_dns_record(hostname: str) -> Dict` - Create a new DNS record
- `delete_dns_record(record_id: str, hostname: str = None) -> None` - Delete a DNS record
- `sync_dns_records(desired_hostnames: List[str], show_diff: bool = True) -> Dict[str, int]` - Sync records

### DNSSync

```python
class DNSSync:
    @staticmethod
    def load_hostnames_from_json(file_path: str = None) -> List[str]
    
    @staticmethod
    def validate_hostname(hostname: str) -> bool
    
    @staticmethod
    def filter_valid_hostnames(hostnames: List[str]) -> List[str]
```

## Configuration

### Hierarchy
1. Command line arguments (highest priority)
2. Configuration file
3. Environment variables
4. Default values (lowest priority)

### Configuration File Schema

```json
{
  "controller": {
    "url": "string (required)",
    "username": "string (required)", 
    "password": "string (required)",
    "name": "string (optional)"
  },
  "dns": {
    "target_ip": "string (default: 10.0.10.31)",
    "show_diff": "boolean (default: true)",
    "dry_run": "boolean (default: false)"
  },
  "hostnames_file": "string (optional)",
  "verbose": "boolean (default: false)"
}
```

## Error Handling

The application uses Python's logging module for consistent error reporting:

- **INFO**: Normal operation messages
- **WARNING**: Non-fatal issues (invalid hostnames, missing CSRF tokens)
- **ERROR**: Fatal errors that prevent operation
- **DEBUG**: Detailed technical information (enabled with --verbose)

## Testing

### Test Structure

```
tests/
├── __init__.py              # Test configuration
├── test_dns_manager.py      # Tests for DNS manager
└── test_sync.py             # Tests for sync utilities
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
python -m pytest tests/test_sync.py -v
```

## Security Considerations

1. **Password Handling**: Passwords are never logged or stored in plaintext
2. **SSL Verification**: Disabled for self-signed certificates (configurable)
3. **CSRF Protection**: CSRF tokens are extracted and used for API calls
4. **Configuration Security**: Configuration files can exclude passwords

## Adding New Features

### Adding a New Command Line Option

1. Update `create_parser()` in `cli.py`
2. Handle the new option in `main()`
3. Add tests for the new functionality
4. Update documentation

### Adding Support for New DNS Record Types

1. Extend `UnifiDNSManager.create_dns_record()` method
2. Update the record filtering logic in `get_existing_dns_records()`
3. Add validation for new record types
4. Add tests

### Adding New Configuration Sources

1. Extend `ConfigLoader` class in `config.py`
2. Add new loading method
3. Update configuration hierarchy in `cli.py`
4. Add tests

## Deployment

### Package Building

```bash
# Build wheel and source distribution
make build

# The package will be in dist/
```

### Publishing to PyPI

```bash
# Build and publish (requires credentials)
make publish
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install .

ENTRYPOINT ["unifi-dns-sync"]
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check credentials
   - Verify controller URL is accessible
   - Check for self-signed certificate issues

2. **CSRF Token Issues**
   - May indicate controller version compatibility
   - Check debug logs for JWT token parsing

3. **DNS Record Creation Failures**
   - Verify permissions on controller
   - Check for conflicting records
   - Validate hostname format

### Debug Mode

Enable debug mode with `--verbose` to see:
- HTTP requests and responses
- JWT token parsing details
- Detailed error information

## Contributing

1. Follow PEP 8 style guide
2. Add type hints to new functions
3. Include docstrings for public methods
4. Add tests for new functionality
5. Update documentation

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **mypy** for type checking

Run `make format` and `make lint` before submitting changes.
