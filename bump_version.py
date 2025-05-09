#!/usr/bin/env python

"""
Version Bump Utility for iPerf Discovery
=======================================

This script increments the patch version of the iPerf Discovery project,
updates the version in iperf_discovery.py, and appends a changelog entry
to changelog.txt. It uses only Python 3 standard library modules for
compatibility with embedded systems.

Usage:
    python3 bump_version.py "Description of changes"

Example:
    python3 bump_version.py "Added IPv6 support"
"""

import re
from datetime import datetime
from pathlib import Path
import argparse


def parse_arguments():
    """Parse command-line arguments.

    Returns:
        str: Changelog entry description provided by the user.
    """
    parser = argparse.ArgumentParser(
        description="Increment iPerf Discovery version and update changelog."
    )
    parser.add_argument(
        'description',
        help="Description of changes for the changelog"
    )
    return parser.parse_args().description


def get_current_version(file_path):
    """Extract the current version from the Python script.

    Args:
        file_path (Path): Path to the Python script.

    Returns:
        tuple: (version string, major, minor, patch) or None if not found.

    Raises:
        ValueError: If the version format is invalid.
    """
    version_pattern = r"__version__ = \"(\d+)\.(\d+)\.(\d+)\""
    try:
        with file_path.open('r') as file:
            content = file.read()
        match = re.search(version_pattern, content)
        if match:
            major, minor, patch = map(int, match.groups())
            return match.group(0), major, minor, patch
        raise ValueError("Version not found in file")
    except (FileNotFoundError, ValueError) as err:
        print(f"Error: {err}")
        return None


def increment_version(major, minor, patch):
    """Increment the patch version.

    Args:
        major (int): Major version number.
        minor (int): Minor version number.
        patch (int): Patch version number.

    Returns:
        str: New version string (e.g., "1.0.13").
    """
    return f"{major}.{minor}.{patch + 1}"


def update_script(file_path, old_version_line, new_version):
    """Update the version in the Python script.

    Args:
        file_path (Path): Path to the Python script.
        old_version_line (str): The current __version__ line.
        new_version (str): The new version string.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with file_path.open('r') as file:
            content = file.read()

        # Update __version__
        new_version_line = f'__version__ = "{new_version}"'
        content = content.replace(old_version_line, new_version_line)

        # Update argparse version
        old_argparse = f'version=f"%(prog)s {old_version_line.split("=")[1].strip().strip(\'"\')}"'
        new_argparse = f'version=f"%(prog)s {new_version}"'
        content = content.replace(old_argparse, new_argparse)

        # Update header date
        old_date_pattern = r"Date: (.*?)\n"
        new_date = f"Date: {datetime.now().strftime('%B %d, %Y')}\n"
        content = re.sub(old_date_pattern, new_date, content)

        with file_path.open('w') as file:
            file.write(content)
        return True
    except (FileNotFoundError, OSError) as err:
        print(f"Error updating script: {err}")
        return False


def update_changelog(file_path, new_version, description):
    """Append a new entry to the changelog.

    Args:
        file_path (Path): Path to the changelog file.
        new_version (str): The new version string.
        description (str): Description of changes.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with file_path.open('r') as file:
            content = file.read()

        new_entry = (
            f"\n## Version {new_version} ({datetime.now().strftime('%B %d, %Y')})\n\n"
            f"- {description}\n"
        )
        content = new_entry + content

        with file_path.open('w') as file:
            file.write(content)
        return True
    except ( generally:
        print(f"Error updating changelog: {err}")
        return False


def main():
    """Main function to bump the version and update files."""
    script_path = Path('iperf_discovery.py')
    changelog_path = Path('changelog.txt')
    description = parse_arguments()

    # Get current version
    version_info = get_current_version(script_path)
    if not version_info:
        return

    old_version_line, major, minor, patch = version_info
    new_version = increment_version(major, minor, patch)

    # Update files
    if update_script(script_path, old_version_line, new_version):
        print(f"Updated script to version {new_version}")
    else:
        print("Failed to update script")
        return

    if update_changelog(changelog_path, new_version, description):
        print(f"Updated changelog with version {new_version}")
    else:
        print("Failed to update changelog")


if __name__ == "__main__":
    main()