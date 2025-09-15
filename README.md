# Unifi DNS Synchronization Tool

Automatically sync DNS A records on Unifi controllers via CLI.

![Demo Screenshot](demo.png)

## Installation

From PyPI (recommended)

```bash
python -m pip install --upgrade pip
python -m pip install unifi-dns-sync
```

From source (development)

```bash
git clone https://github.com/cswitenky/unifi-dns-sync.git
cd unifi-dns-sync
python -m pip install -e .
```

## Usage

Create a JSON file with your hostnames and IPs:

```json
[
  { "service1.example.com": "10.0.10.1" },
  { "service2.example.com": "10.0.20.1" },
  "service3.example.com"
]
```

Run the sync:

```bash
python -m unifi_dns_sync config/dns-records.json \
  --controller https://10.0.0.1 \
  --username admin \
  --password your-password
```

## Options

- `--dry-run` - Show what would change without making changes
- `--show-diff` - Show detailed diff of changes
- `--target-ip` - Default IP for hostnames without explicit IPs (default: 10.0.0.123)
- `--verbose` - Enable debug logging

## JSON Formats

**Simple hostnames** (uses --target-ip):

```json
["host1.com", "host2.com"]
```

**Hostname to IP mapping**:

```json
[{ "host1.com": "1.2.3.4" }, { "host2.com": "5.6.7.8" }]
```

**Explicit format**:

```json
[{ "hostname": "host1.com", "ip": "1.2.3.4" }, { "hostname": "host2.com" }]
```

## License

MIT License
