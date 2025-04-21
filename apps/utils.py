"""
Network Utility Functions Module

This module provides utility functions for common network-related operations,
particularly focusing on IP address manipulations and conversions.
These functions are used throughout the network configuration parser
to standardize and simplify network address handling.
"""

import ipaddress
import logging

logger = logging.getLogger(__name__)

def ip_mask_to_cidr(ip: str, mask: str) -> str:
    """
    Convert an IP address and subnet mask to CIDR notation.
    
    This function takes an IP address and its subnet mask (in dotted decimal format)
    and converts them to CIDR (Classless Inter-Domain Routing) notation. This is
    useful for standardizing network address representations and making them more
    compact.
    
    Args:
        ip (str): The IP address in dotted decimal format (e.g., '192.168.1.1')
        mask (str): The subnet mask in dotted decimal format (e.g., '255.255.255.0')
    
    Returns:
        str: The IP address in CIDR notation (e.g., '192.168.1.1/24').
             Returns an empty string if the conversion fails due to invalid input.
    
    Examples:
        >>> ip_mask_to_cidr('192.168.1.1', '255.255.255.0')
        '192.168.1.1/24'
        >>> ip_mask_to_cidr('10.0.0.1', '255.255.0.0')
        '10.0.0.1/16'
        >>> ip_mask_to_cidr('invalid', '255.255.255.0')
        ''
    
    Notes:
        - Both IP and mask must be in valid IPv4 format
        - Common subnet masks and their CIDR equivalents:
          * 255.255.255.0  -> /24
          * 255.255.0.0    -> /16
          * 255.0.0.0      -> /8
        - Invalid inputs are logged as warnings and return empty string
    """
    if not ip or not mask:
        return ""
    try:
        interface = ipaddress.IPv4Interface(f"{ip}/{mask}")
        return str(interface)
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError) as e:
        logger.warning(f"Could not convert IP/Mask {ip}/{mask} to CIDR: {e}")
        return "" # Return empty string on error 