"""
Device type identification module.
Identifies the type of network device from configuration files.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def identify_device_type(filepath: str) -> str:
    """
    Identify the type of device from a configuration file.
    Does a quick scan of the file looking for identifying markers.
    
    Args:
        filepath: Path to the configuration file
    
    Returns:
        str: Device type ("Cisco IOS", "Cisco NXOS", "Cisco ASA", "Palo Alto", or "Unknown")
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