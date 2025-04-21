"""
Device Type Identification Module

This module provides functionality to automatically identify the type of network device
from configuration files or show-tech outputs. It works by scanning the file contents
for vendor-specific markers and command outputs.

Supported device types:
- Cisco IOS (Traditional IOS devices)
- Cisco NXOS (Nexus switches)
- Cisco ASA (Adaptive Security Appliance)
- Palo Alto (PAN-OS devices)

The module uses a hierarchical approach to identification:
1. First checks for explicit version strings
2. Then looks for vendor-specific markers
3. Finally tries to infer from command output formats
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def identify_device_type(filepath: str) -> str:
    """
    Identify the type of network device from a configuration or show-tech file.
    
    This function performs a quick scan of the file (first 1000 lines) looking for
    identifying markers that indicate the device type. It uses a hierarchical approach
    to identification, starting with the most specific markers and falling back to
    more general ones if needed.
    
    Args:
        filepath (str): Path to the configuration or show-tech file to analyze.
                       The file should be readable and contain text content.
    
    Returns:
        str: Identified device type, one of:
            - "Cisco IOS": Traditional Cisco IOS devices
            - "Cisco NXOS": Cisco Nexus switches
            - "Cisco ASA": Cisco ASA firewalls
            - "Palo Alto": Palo Alto Networks devices
            - "Unknown": If the device type cannot be determined
    
    Examples:
        >>> device_type = identify_device_type("config_backup.txt")
        >>> if device_type != "Unknown":
        ...     print(f"Found {device_type} configuration")
    
    Notes:
        - The function only reads the first 1000 lines of the file to be efficient
        - Uses UTF-8 encoding with error ignoring for maximum compatibility
        - Falls back to "Cisco IOS" if generic Cisco commands are found but type is unclear
        - Logs errors if file reading fails but won't raise exceptions
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            # Read first 1000 lines or until EOF
            content = ''.join(f.readline() for _ in range(1000))
            
            # Check for Palo Alto XML format
            if '<?xml' in content and any(x in content for x in ['<config', '<show']):
                if 'panos' in content.lower():
                    return "Palo Alto"
            
            # Check for ASA
            if any(x in content for x in ['ASA Version', 'PIX Version', 'Cisco Adaptive Security Appliance']):
                return "Cisco ASA"
            
            # Check for Nexus
            if any(x in content for x in ['NX-OS', 'Nexus']):
                return "Cisco NXOS"
            
            # Check for IOS
            if any(x in content for x in ['IOS Software', 'Cisco IOS Software']):
                return "Cisco IOS"
            
            # If no clear markers found, try to infer from command output format
            if 'show running-config' in content or 'show startup-config' in content:
                # Looks like Cisco, but not sure which type
                # Default to IOS as it's most common
                return "Cisco IOS"
            
            return "Unknown"
            
    except Exception as e:
        logger.error(f"Error identifying device type for {filepath}: {e}")
        return "Unknown" 