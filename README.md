# iPerf Discovery Utility

## Overview

The iPerf Discovery Utility is a Python 3 script designed to locate NetAlly Test Accessories running iPerf3 servers on a specified IPv4 network. It scans for devices listening on TCP port 2359, queries them with a specific message, and logs the results to a file. The script is optimized for embedded systems, using only Python 3 standard library modules.

This utility is intended for network administrators and engineers using NetAlly Test Accessories to perform network performance testing with iPerf3.

## Features

- Scans an IPv4 network for hosts with TCP port 2359 open.
- Queries responsive hosts to identify valid NetAlly Test Accessories.
- Logs detailed debugging information and results to `iperfdiscovery.log`.
- Outputs discovered device details to `iperfaccessory`.
- Supports configurable socket timeouts via command-line or configuration file.
- Uses asynchronous I/O (`asyncio`) for efficient scanning.
- Provides verbose console output option for real-time feedback.

## Requirements

- Python 3.6 or later (standard library only).
- Access to the target network.
- Write permissions for log and output files.
- Optional: Configuration file at `/mnt/mmc3/iperfaccessory.conf` for custom timeouts.

## Installation

No installation is required. Copy the `iperf_discovery.py` script to your system and ensure it has executable permissions:

```bash
chmod +x iperf_discovery.py
```

## Usage

Run the script with a network address in CIDR notation (e.g., `192.168.1.0/24`):

```bash
./iperf_discovery.py 192.168.1.0/24
```

### Command-Line Options

- `network`: The IPv4 network to scan (required, e.g., `192.168.1.0/24`).
- `-t, --timeout SECONDS`: Override the default socket timeout (default: 0.010s).
- `-v, --version`: Display the script version (1.0.13).
- `-o, --options`: Use settings from `/mnt/mmc3/iperfaccessory.conf`.
- `--verbose`: Enable verbose console output.

### Example Commands

Scan the 192.168.1.0/24 network with default settings:

```bash
./iperf_discovery.py 192.168.1.0/24
```

Scan with a custom timeout of 0.05 seconds:

```bash
./iperf_discovery.py 192.168.1.0/24 --timeout 0.05
```

Scan with verbose output and configuration file:

```bash
./iperf_discovery.py 192.168.1.0/24 --options --verbose
```

### Configuration File

The optional configuration file at `/mnt/mmc3/iperfaccessory.conf` can specify a custom timeout. Example format:

```
timeout=0.050
```

The timeout must be between 0.010 and 0.160 seconds. If the file is missing or invalid, the default timeout (0.010s) is used.

## Output

- **Log File**: `iperfdiscovery.log` contains detailed debug and info messages, including scan progress, errors, and a summary.
- **Accessory File**: `iperfaccessory` contains details of discovered NetAlly Test Accessories, formatted as `<IP>: <attributes>`.

Example `iperfaccessory` content:

```
192.168.1.100: MAC=00:11:22:33:44:55;Batt=Full;PoeV=48V;NsType=Ethernet
```

## Development

### Versioning

To increment the version number and update the changelog, use the `bump_version.py` script:

```bash
python3 bump_version.py "Added new feature X"
```

This increments the patch version (e.g., 1.0.13 to 1.0.14), updates `iperf_discovery.py`, and appends a changelog entry.

### Git Workflow

- **Branches**:
  - `main`: Stable, production-ready code.
  - `develop`: Integration branch for new features and fixes.
  - Feature/bugfix branches: Named `feature/<name>` or `bugfix/<name>`.
- **Commit Messages**:
  - Format: `<type>(<scope>): <description>`
  - Types: `feat`, `fix`, `docs`, `refactor`, `chore`.
  - Example: `feat(scanning): Add IPv6 support`

## Notes

- The script is designed for embedded systems and avoids third-party dependencies.
- Asynchronous I/O (`asyncio`) ensures efficient scanning, even on large networks.
- The script overwrites the log and accessory files on each run.
- Interrupt the script with `Ctrl+C` to stop scanning gracefully.

## Known Limitations

- Only IPv4 networks are supported.
- The configuration file parser supports only a single `timeout` setting.
- No support for IPv6 or non-TCP protocols.

## Contributing

This script is maintained by Kris Armstrong. For bug reports or feature requests, contact the NetAlly support team.

## License

This software is proprietary and intended for use with NetAlly Test Accessories. Unauthorized distribution or modification is prohibited.

## Version

1.0.13 (April 17, 2025)