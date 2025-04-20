import ipaddress
import logging

logger = logging.getLogger(__name__)

def ip_mask_to_cidr(ip: str, mask: str) -> str:
    """
    Convert an IP address and subnet mask to CIDR notation.

    Args:
        ip (str): The IP address.
        mask (str): The subnet mask.

    Returns:
        str: The IP address in CIDR notation (e.g., '192.168.1.1/24'),
             or an empty string if conversion fails.
    """
    if not ip or not mask:
        return ""
    try:
        interface = ipaddress.IPv4Interface(f"{ip}/{mask}")
        return str(interface)
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError) as e:
        logger.warning(f"Could not convert IP/Mask {ip}/{mask} to CIDR: {e}")
        return "" # Return empty string on error 