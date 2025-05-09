#!/usr/bin/env python

"""
iPerf Discovery Utility for NetAlly Test Accessory
================================================

This script scans a specified IPv4 network to discover NetAlly Test Accessories
running an iPerf3 server on TCP port 2359. It sends a query message to identify
valid devices and logs results to a file. The script is designed for embedded
systems and uses only Python 3 standard library modules.

Author: Kris Armstrong
Version: 1.0.13
Date: April 17, 2025
"""

__title__ = "iPerf Discovery"
__author__ = "Kris Armstrong"
__version__ = "1.0.13"


# Standard Library Imports
import argparse
import asyncio
import logging
import os
import socket
from datetime import datetime
import ipaddress


# Global Configuration
class Config:
    """Global configuration constants for the iPerf Discovery utility."""
    buffer_size = 4096  # TCP buffer size in bytes
    message = 'TA:getattrlong'.encode('utf-8')  # Query message for iPerf3 servers
    tcp_port = 2359  # Default TCP port for NetAlly Test Accessory
    min_scan_timeout = 0.010  # Minimum socket timeout in seconds (10ms)
    max_scan_timeout = 0.160  # Maximum socket timeout in seconds (160ms)
    query_timeout = 5.0  # Query socket timeout in seconds
    log_file = 'iperfdiscovery.log'  # Log file for debugging and info
    accessory_file = 'iperfaccessory'  # Output file for discovered devices
    option_file = '/mnt/mmc3/iperfaccessory.conf'  # Configuration file path


def setup_logging():
    """Configure logging to write to a file with a standardized format.

    The log file is overwritten on each run. The format includes timestamp,
    log level, and message.
    """
    logging.basicConfig(
        filename=Config.log_file,
        filemode='w',
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )


def clear_accessory_file():
    """Remove the accessory output file if it exists.

    Logs any errors encountered during file removal.
    """
    if os.path.exists(Config.accessory_file):
        try:
            os.remove(Config.accessory_file)
            logging.debug("Cleared accessory file: %s", Config.accessory_file)
        except OSError as err:
            logging.error("Failed to remove %s: %s", Config.accessory_file, err)


def parse_arguments():
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.

    Raises:
        SystemExit: If the network argument is invalid.
    """
    parser = argparse.ArgumentParser(
        description="Discover NetAlly Test Accessories running iPerf3 servers on a network."
    )
    parser.add_argument(
        'network',
        help="IPv4 network to scan (e.g., 192.168.1.0/24)",
        type=str
    )
    parser.add_argument(
        '-t', '--timeout',
        type=float,
        help="Socket timeout in seconds (overrides default %.3fs)" % Config.min_scan_timeout
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        '-o', '--options',
        action='store_true',
        help="Use advanced configuration from %s" % Config.option_file
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="Enable verbose console output"
    )

    args = parser.parse_args()

    # Validate network
    try:
        ipaddress.ip_network(args.network, strict=False)
    except ValueError as err:
        parser.error(f"Invalid network address: {args.network} ({err})")

    # Add console logging if verbose
    if args.verbose:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        )
        logging.getLogger().addHandler(console_handler)

    return args


def parse_options_file():
    """Parse the options configuration file to retrieve settings.

    Returns:
        float: Timeout value from the file, or None if parsing fails.
    """
    try:
        with open(Config.option_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('timeout='):
                    try:
                        timeout = float(line.split('=')[1])
                        if Config.min_scan_timeout <= timeout <= Config.max_scan_timeout:
                            logging.debug("Parsed timeout from %s: %.3fs", Config.option_file, timeout)
                            return timeout
                        logging.warning("Timeout out of range: %.3fs", timeout)
                    except ValueError:
                        logging.error("Invalid timeout format in %s: %s", Config.option_file, line)
        logging.debug("No valid timeout found in %s", Config.option_file)
    except (OSError, FileNotFoundError) as err:
        logging.error("Failed to read %s: %s", Config.option_file, err)
    return None


async def tcp_port_ping_single(host, timeout):
    """Check if a single host has the specified TCP port open.

    Args:
        host (ipaddress.IPv4Address): The host to check.
        timeout (float): Socket timeout in seconds.

    Returns:
        ipaddress.IPv4Address or None: The host if the port is open, else None.
    """
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(str(host), Config.tcp_port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        logging.debug("Host %s has port %d open", host, Config.tcp_port)
        return host
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as err:
        logging.debug("Failed to connect to %s:%d: %s", host, Config.tcp_port, err)
        return None


async def tcp_port_ping(network, timeout):
    """Scan the network for hosts with the iPerf3 server port open.

    Args:
        network (ipaddress.IPv4Network): The network to scan.
        timeout (float): Socket timeout in seconds.

    Returns:
        tuple: List of responsive hosts, total IP count, active IP count.
    """
    total_ip_count = 0
    active_ip_count = 0
    responsive_hosts = []

    start_time = datetime.now()
    logging.info("Starting TCP port scan on %s", network)

    tasks = [
        tcp_port_ping_single(host, timeout)
        for host in network.hosts()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for host, result in zip(network.hosts(), results):
        total_ip_count += 1
        if result and not isinstance(result, Exception):
            active_ip_count += 1
            responsive_hosts.append(result)

    end_time = datetime.now()
    scan_time = end_time - start_time

    logging.info(
        "TCP scan completed: %d/%d hosts active (%.3fs)",
        active_ip_count, total_ip_count, scan_time.total_seconds()
    )

    return responsive_hosts, total_ip_count, active_ip_count, scan_time


async def iperf_query_single(host):
    """Query a single host for iPerf3 server attributes.

    Args:
        host (ipaddress.IPv4Address): The host to query.

    Returns:
        tuple: (host, response) if successful, else (host, None).
    """
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(str(host), Config.tcp_port),
            timeout=Config.query_timeout
        )
        writer.write(Config.message)
        await writer.drain()
        response = await reader.read(Config.buffer_size)
        writer.close()
        await writer.wait_closed()
        logging.debug("Received response from %s: %s", host, response)
        return host, response
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as err:
        logging.debug("Query failed for %s: %s", host, err)
        return host, None


async def iperf_query(responsive_hosts, total_ip_count, active_ip_count, scan_time):
    """Query responsive hosts to identify valid iPerf3 servers.

    Args:
        responsive_hosts (list): List of hosts with open ports.
        total_ip_count (int): Total IPs scanned.
        active_ip_count (int): Number of hosts with open ports.
        scan_time (datetime.timedelta): Time taken for TCP scan.

    Returns:
        None
    """
    start_time = datetime.now()
    logging.info("Starting iPerf query on %d hosts", len(responsive_hosts))

    tasks = [iperf_query_single(host) for host in responsive_hosts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    valid_count = 0
    invalid_count = 0
    accessories = []

    for host, response in results:
        if response and isinstance(response, bytes):
            try:
                decoded = response.decode('utf-8')
                if 'iPerf Remote' in decoded:
                    valid_count += 1
                    accessories.append((host, decoded))
                    logging.debug("Valid iPerf Remote at %s: %s", host, decoded)
                else:
                    invalid_count += 1
                    logging.info("Invalid iPerf Remote at %s: %s", host, decoded)
            except UnicodeDecodeError:
                invalid_count += 1
                logging.error("Failed to decode response from %s", host)
        else:
            invalid_count += 1
            logging.debug("No response from %s", host)

    end_time = datetime.now()
    query_time = end_time - start_time
    total_time = scan_time + query_time

    logging.info(
        "iPerf query completed: %d valid, %d invalid (%.3fs)",
        valid_count, invalid_count, query_time.total_seconds()
    )

    write_accessory_file(accessories)
    log_summary(
        valid_count, invalid_count, active_ip_count,
        total_ip_count, scan_time, query_time, total_time
    )


def write_accessory_file(accessories):
    """Write discovered iPerf3 server details to the accessory file.

    Args:
        accessories (list): List of (host, response) tuples for valid devices.
    """
    try:
        with open(Config.accessory_file, 'a') as file:
            for host, response in accessories:
                cleaned = clean_response(response)
                file.write(f"{host}: {cleaned}\n")
        logging.debug("Wrote %d entries to %s", len(accessories), Config.accessory_file)
    except OSError as err:
        logging.error("Failed to write to %s: %s", Config.accessory_file, err)


def clean_response(response):
    """Clean the response string for output.

    Args:
        response (str): Raw response from the iPerf3 server.

    Returns:
        str: Cleaned response with standardized formatting.
    """
    cleaned = response.strip()
    cleaned = ' '.join(cleaned.split())  # Remove duplicate spaces
    replacements = {
        'ethaddr=': 'MAC=',
        'PS9: ': 'Batt=',
        'PS8: ': 'PoeV=',
        'EtherType: ': 'NsType=',
        'Device ID: ': 'NsDev=',
        'Addresses: ': 'NsAddr=',
        'Platform: ': 'NsPlatform=',
        'Port ID: ': 'NsPort=',
        'Vlan ID:': 'NsVlan=',
        '\\n': ';'
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    return cleaned


def log_summary(valid_count, invalid_count, active_ip_count, total_ip_count,
                scan_time, query_time, total_time):
    """Log a summary of the scan and query results.

    Args:
        valid_count (int): Number of valid iPerf3 servers.
        invalid_count (int): Number of invalid responses.
        active_ip_count (int): Number of hosts with open ports.
        total_ip_count (int): Total IPs scanned.
        scan_time (datetime.timedelta): TCP scan duration.
        query_time (datetime.timedelta): Query duration.
        total_time (datetime.timedelta): Total duration.
    """
    logging.info("Summary:")
    logging.info("  Total IPs scanned: %d", total_ip_count)
    logging.info("  Hosts with port %d open: %d", Config.tcp_port, active_ip_count)
    logging.info("  Valid iPerf Remotes: %d", valid_count)
    logging.info("  Invalid responses: %d", invalid_count)
    logging.info("  TCP scan time: %.3fs", scan_time.total_seconds())
    logging.info("  iPerf query time: %.3fs", query_time.total_seconds())
    logging.info("  Total time: %.3fs", total_time.total_seconds())


async def main():
    """Main function to coordinate the iPerf Discovery process.

    Parses arguments, configures the scan, and runs the discovery process.
    """
    setup_logging()
    clear_accessory_file()
    args = parse_arguments()

    # Determine timeout
    timeout = Config.min_scan_timeout
    if args.options:
        parsed_timeout = parse_options_file()
        if parsed_timeout is not None:
            timeout = parsed_timeout
    if args.timeout is not None:
        if Config.min_scan_timeout <= args.timeout <= Config.max_scan_timeout:
            timeout = args.timeout
        else:
            logging.warning(
                "Timeout %.3fs out of range (%.3f-%.3f), using default %.3fs",
                args.timeout, Config.min_scan_timeout, Config.max_scan_timeout, timeout
            )

    try:
        network = ipaddress.ip_network(args.network, strict=False)
        responsive_hosts, total_ip_count, active_ip_count, scan_time = await tcp_port_ping(network, timeout)
        await iperf_query(responsive_hosts, total_ip_count, active_ip_count, scan_time)
    except KeyboardInterrupt:
        logging.info("Scan interrupted by user")
    except Exception as err:
        logging.error("Unexpected error: %s", err)


if __name__ == "__main__":
    asyncio.run(main())