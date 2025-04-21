"""
Palo Alto Configuration Parser Module

This module provides comprehensive parsing capabilities for Palo Alto Networks
firewall configurations in XML format. It converts the hierarchical XML structure
into a more accessible dictionary format and extracts key configuration elements.

Key Features:
- Parses XML configuration files from Palo Alto firewalls
- Extracts interface configurations, security policies, and NAT rules
- Handles address and service objects
- Provides nested dictionary viewing capabilities
- Supports hostname extraction
- Includes detailed logging and error handling

The module uses ElementTree for XML parsing and provides utilities for
exploring the configuration hierarchy at various depth levels.
"""

import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any, Optional
from tabulate import tabulate

# Get module logger
logger = logging.getLogger(__name__)

class PaloAltoParser:
    """
    Parser for Palo Alto Networks firewall configurations.
    
    This class provides functionality to parse and analyze Palo Alto firewall
    configurations in XML format. It converts the XML hierarchy into a dictionary
    structure and extracts key configuration elements into structured data.
    
    Features:
        - XML to dictionary conversion
        - Interface configuration parsing
        - Security policy extraction
        - NAT policy parsing
        - Object (address/service) handling
        - Hostname identification
    
    Attributes:
        config_dict (Dict[str, Any]): Parsed configuration in dictionary format
        hostname (str): Device hostname (defaults to "unknown")
    
    Example:
        >>> parser = PaloAltoParser()
        >>> config = parser.parse_file("palo_alto_config.xml")
        >>> print(f"Found {len(config['Security Policies'])} security policies")
    """

    def __init__(self):
        """
        Initialize the Palo Alto parser.
        
        Creates an empty configuration dictionary and sets default hostname.
        The actual parsing is deferred until parse_file() is called.
        """
        self.config_dict: Dict[str, Any] = {}
        self.hostname = "unknown"

    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """
        Parse a Palo Alto configuration file in XML format.
        
        This method reads an XML configuration file, converts it to a dictionary
        structure, and extracts key configuration elements into organized sections.
        
        Args:
            filepath (str): Path to the XML configuration file
        
        Returns:
            Dict[str, Any]: Parsed configuration data organized by sections:
                - Interfaces: Network interface configurations
                - Security Policies: Security rules and policies
                - NAT Policies: Network address translation rules
                - Objects: Address and service objects
        
        Raises:
            ET.ParseError: If XML parsing fails
            Exception: For other processing errors
        
        Example:
            >>> parser = PaloAltoParser()
            >>> try:
            ...     config = parser.parse_file("config.xml")
            ...     for interface in config['Interfaces']:
            ...         print(f"Interface: {interface['Name']}")
            ... except ET.ParseError:
            ...     print("Invalid XML file")
        """
        try:
            logger.info(f"Parsing Palo Alto configuration file: {filepath}")
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Convert XML to dictionary
            self.config_dict = self._xml_to_dict(root)
            
            # Extract hostname if available
            self._extract_hostname()
            
            # Parse sections into structured data
            parsed_data = self._parse_sections()
            
            logger.info("Successfully parsed Palo Alto configuration")
            return parsed_data
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML file {filepath}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing Palo Alto configuration: {e}")
            raise

    def _extract_hostname(self) -> None:
        """
        Extract hostname from the configuration dictionary.
        
        Attempts to find the hostname in the device-group or system settings
        section of the configuration. Sets the hostname attribute if found,
        otherwise keeps the default "unknown" value.
        
        Notes:
            - Looks in devices/entry/hostname path
            - Logs warning if hostname cannot be extracted
            - Keeps existing hostname if extraction fails
        """
        try:
            # Try to find hostname in device-group or system settings
            if 'devices' in self.config_dict:
                devices = self.config_dict['devices']
                if isinstance(devices, dict) and 'entry' in devices:
                    self.hostname = devices['entry'].get('hostname', 'unknown')
            logger.debug(f"Found hostname: {self.hostname}")
        except Exception as e:
            logger.warning(f"Could not extract hostname: {e}")

    def _parse_sections(self) -> Dict[str, Any]:
        """
        Parse configuration sections into structured data.
        
        This method orchestrates the parsing of various configuration sections,
        calling specific parsers for each section type and combining the results.
        
        Returns:
            Dict[str, Any]: Parsed configuration data with sections:
                - Interfaces: List of interface configurations
                - Security Policies: List of security rules
                - NAT Policies: List of NAT rules
                - Objects: List of address and service objects
        """
        parsed_data = {
            'Interfaces': self._parse_interfaces(),
            'Security Policies': self._parse_security_policies(),
            'NAT Policies': self._parse_nat_policies(),
            'Objects': self._parse_objects()
        }
        return parsed_data

    def _parse_interfaces(self) -> list:
        """
        Parse network interface configurations.
        
        Extracts interface configurations from the network section of the
        configuration, including interface names, types, IP addresses,
        security zones, and VLAN assignments.
        
        Returns:
            list: List of dictionaries containing interface details:
                [
                    {
                        'Name': Interface name,
                        'Type': Interface type,
                        'IP': IP address/subnet,
                        'Zone': Security zone,
                        'VLAN': VLAN ID
                    },
                    ...
                ]
        
        Notes:
            - Handles missing or incomplete interface configurations
            - Returns empty list if no interfaces found
            - Logs errors during parsing
        """
        interfaces = []
        try:
            # Extract interface configurations
            if 'network' in self.config_dict:
                network = self.config_dict['network']
                if 'interface' in network:
                    for interface in network['interface'].get('entry', []):
                        interface_data = {
                            'Name': interface.get('name', ''),
                            'Type': interface.get('type', ''),
                            'IP': interface.get('ip', ''),
                            'Zone': interface.get('zone', ''),
                            'VLAN': interface.get('vlan', '')
                        }
                        interfaces.append(interface_data)
        except Exception as e:
            logger.error(f"Error parsing interfaces: {e}")
        return interfaces

    def _parse_security_policies(self) -> list:
        """
        Parse security policy rules.
        
        Extracts security policies from the configuration, including rule names,
        actions, zones, and other security parameters.
        
        Returns:
            list: List of dictionaries containing security policy details:
                [
                    {
                        'Name': Rule name,
                        'Action': Allow/Deny/Drop,
                        'Source Zone': Source security zone,
                        'Destination Zone': Destination security zone,
                        'Source': Source addresses/groups,
                        'Destination': Destination addresses/groups,
                        'Service': Service/application,
                        'Application': Application ID
                    },
                    ...
                ]
        
        Notes:
            - Processes both intrazone and interzone policies
            - Returns empty list if no policies found
            - Logs errors during parsing
        """
        policies = []
        try:
            if 'policies' in self.config_dict:
                security = self.config_dict['policies'].get('security', {})
                for rule in security.get('rules', []):
                    policy_data = {
                        'Name': rule.get('name', ''),
                        'Action': rule.get('action', ''),
                        'Source Zone': rule.get('from', ''),
                        'Destination Zone': rule.get('to', ''),
                        'Source': rule.get('source', ''),
                        'Destination': rule.get('destination', ''),
                        'Service': rule.get('service', ''),
                        'Application': rule.get('application', '')
                    }
                    policies.append(policy_data)
        except Exception as e:
            logger.error(f"Error parsing security policies: {e}")
        return policies

    def _parse_nat_policies(self) -> list:
        """
        Parse NAT (Network Address Translation) policies.
        
        Extracts NAT rules from the configuration, including source NAT,
        destination NAT, and static NAT configurations.
        
        Returns:
            list: List of dictionaries containing NAT rule details:
                [
                    {
                        'Name': Rule name,
                        'Source': Original source address,
                        'Destination': Original destination address,
                        'Service': Service/port,
                        'Translation': NAT translation details
                    },
                    ...
                ]
        
        Notes:
            - Handles all NAT rule types (source, destination, static)
            - Returns empty list if no NAT rules found
            - Logs errors during parsing
        """
        nat_rules = []
        try:
            if 'policies' in self.config_dict:
                nat = self.config_dict['policies'].get('nat', {})
                for rule in nat.get('rules', []):
                    nat_data = {
                        'Name': rule.get('name', ''),
                        'Source': rule.get('source', ''),
                        'Destination': rule.get('destination', ''),
                        'Service': rule.get('service', ''),
                        'Translation': rule.get('translation', '')
                    }
                    nat_rules.append(nat_data)
        except Exception as e:
            logger.error(f"Error parsing NAT policies: {e}")
        return nat_rules

    def _parse_objects(self) -> list:
        """
        Parse address and service objects.
        
        Extracts network address objects and service objects from the
        configuration, including both predefined and custom objects.
        
        Returns:
            list: List of dictionaries containing object details:
                [
                    {
                        'Name': Object name,
                        'Type': 'address' or 'service',
                        'Value': IP/FQDN for address objects,
                        'Protocol': Protocol for service objects,
                        'Port': Port for service objects
                    },
                    ...
                ]
        
        Notes:
            - Handles both IPv4 and IPv6 address objects
            - Processes FQDN and IP range objects
            - Returns empty list if no objects found
            - Logs errors during parsing
        """
        objects = []
        try:
            if 'objects' in self.config_dict:
                obj_config = self.config_dict['objects']
                # Parse address objects
                for addr in obj_config.get('address', {}).get('entry', []):
                    obj_data = {
                        'Name': addr.get('name', ''),
                        'Type': 'address',
                        'Value': addr.get('ip-netmask', addr.get('fqdn', ''))
                    }
                    objects.append(obj_data)
                # Parse service objects
                for svc in obj_config.get('service', {}).get('entry', []):
                    obj_data = {
                        'Name': svc.get('name', ''),
                        'Type': 'service',
                        'Protocol': svc.get('protocol', ''),
                        'Port': svc.get('port', '')
                    }
                    objects.append(obj_data)
        except Exception as e:
            logger.error(f"Error parsing objects: {e}")
        return objects

    @staticmethod
    def _xml_to_dict(element: ET.Element) -> Dict[str, Any]:
        """
        Convert XML element to dictionary recursively.
        
        This method converts an XML element and all its children into a
        nested dictionary structure, preserving attributes and text content.
        
        Args:
            element (ET.Element): XML element to convert
        
        Returns:
            Dict[str, Any]: Dictionary representation of the XML element:
                - Attributes become dictionary key-value pairs
                - Child elements become nested dictionaries
                - Multiple children with same tag become lists
                - Element text is stored under 'text' key if present
        
        Example:
            XML: <interface name="eth1"><ip>192.168.1.1</ip></interface>
            Dict: {
                'interface': {
                    'name': 'eth1',
                    'ip': '192.168.1.1'
                }
            }
        """
        result = {}

        # Handle attributes if present
        if element.attrib:
            result.update(element.attrib)

        # Handle child elements
        for child in element:
            child_dict = PaloAltoParser._xml_to_dict(child)

            if child.tag in result:
                # If tag already exists, convert to list or append
                if isinstance(result[child.tag], list):
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = [result[child.tag], child_dict]
            else:
                result[child.tag] = child_dict

        # Handle element text
        if element.text and element.text.strip():
            if result:
                result['text'] = element.text.strip()
            else:
                result = element.text.strip()

        return result

    def get_hostname(self) -> str:
        """
        Get the hostname of the Palo Alto device.
        
        Returns:
            str: Device hostname if found during parsing,
                 "unknown" if not found or not yet parsed
        """
        return self.hostname


def print_dict_levels(d: Dict[str, Any], current_level: int = 0,
                      max_level: Optional[int] = None, indent: str = ""):
    """
    Print a nested dictionary with configurable depth levels.
    
    This utility function prints a nested dictionary structure in a hierarchical
    format, allowing control over the depth of nesting to display. It's particularly
    useful for exploring complex Palo Alto configurations.
    
    Args:
        d (Dict[str, Any]): Dictionary to print
        current_level (int): Current nesting level (used for recursion)
        max_level (Optional[int]): Maximum nesting level to print.
                                 None means print all levels.
        indent (str): Current indentation string (used for recursion)
    
    Example:
        >>> config = {'network': {'interfaces': {'eth0': {'ip': '192.168.1.1'}}}}
        >>> print_dict_levels(config, max_level=2)
        network
          interfaces
            eth0: {...}
    
    Notes:
        - Uses indentation to show hierarchy
        - Shows {...} for truncated nested structures
        - Handles both dictionary and list values
        - Recursively processes nested structures
    """
    if max_level is not None and current_level > max_level:
        return

    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, (dict, list)):
                print(f"{indent}{key}:")
                print_dict_levels(value, current_level + 1, max_level, indent + "  ")
            else:
                print(f"{indent}{key}: {value}")
    elif isinstance(d, list):
        for item in d:
            print_dict_levels(item, current_level, max_level, indent)
    else:
        print(f"{indent}{d}")


def get_level_2_items(d: Dict[str, Any]) -> list:
    """
    Get a list of items at the second level of a nested dictionary.
    
    This utility function extracts and formats items from the second level
    of nesting in a dictionary structure. It's useful for creating menus
    or summaries of configuration sections.
    
    Args:
        d (Dict[str, Any]): Dictionary to analyze
    
    Returns:
        list: List of tuples containing:
            - Index number (1-based)
            - First level key
            - Second level key
            - Preview of the value
    
    Example:
        >>> config = {'network': {'interfaces': {'eth0': {}}, 'dns': {'servers': []}}}
        >>> items = get_level_2_items(config)
        >>> print(items)
        [(1, 'network', 'interfaces', '{...}'), (2, 'network', 'dns', '{...}')]
    
    Notes:
        - Only processes dictionary values
        - Provides a preview of deeper structures
        - Useful for building interactive menus
    """
    level_2_items = []
    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, dict):
                for sub_key in value.keys():
                    level_2_items.append(f"{key}.{sub_key}")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        for sub_key in item.keys():
                            level_2_items.append(f"{key}.{sub_key}")
    return sorted(list(set(level_2_items)))


def display_menu(config_dict: Dict[str, Any]) -> None:
    """
    Display an interactive menu for exploring configuration sections.
    
    This function creates a user-friendly menu interface for navigating
    through a Palo Alto configuration dictionary. It shows available
    sections and allows users to select which parts to explore.
    
    Args:
        config_dict (Dict[str, Any]): Configuration dictionary to display
    
    Example:
        >>> config = parse_config("palo_alto.xml")
        >>> display_menu(config)
        Available sections:
        1. network > interfaces
        2. policies > security
        3. objects > address
        ...
        Enter section number (q to quit):
    
    Notes:
        - Uses tabulate for formatted output
        - Provides section previews
        - Supports quit option
        - Handles invalid input gracefully
    """
    while True:
        # Get level 2 items for display options
        level_2_items = get_level_2_items(config_dict)

        # Create menu options
        menu_options = [
            ["1", "Select level to display"],
            ["2", "Display specific section"],
            ["q", "Quit"]
        ]

        print("\nAvailable Options:")
        print(tabulate(menu_options, headers=["Choice", "Action"], tablefmt="grid"))

        choice = input("\nEnter your choice: ").lower()

        if choice == 'q':
            break
        elif choice == '1':
            try:
                levels = int(input("Enter number of levels to display: "))
                if levels < 0:
                    print("Please enter a positive number")
                    continue
                print("\nConfiguration structure:")
                print_dict_levels(config_dict, max_level=levels)
            except ValueError:
                print("Please enter a valid number")
        elif choice == '2':
            # Display available sections
            section_options = [[str(i + 1), item] for i, item in enumerate(level_2_items)]
            print("\nAvailable Sections:")
            print(tabulate(section_options, headers=["Choice", "Section"], tablefmt="grid"))

            try:
                section_choice = int(input("\nEnter section number: ")) - 1
                if 0 <= section_choice < len(level_2_items):
                    selected_path = level_2_items[section_choice].split('.')

                    # Navigate to selected section
                    current_dict = config_dict
                    for key in selected_path:
                        if isinstance(current_dict, dict):
                            current_dict = current_dict.get(key, {})
                        elif isinstance(current_dict, list):
                            # Handle list case if needed
                            current_dict = current_dict[0].get(key, {})

                    # Ask for levels to display
                    try:
                        levels = int(input("Enter number of additional levels to display: "))
                        if levels < 0:
                            print("Please enter a positive number")
                            continue
                        print(f"\nDisplaying section: {level_2_items[section_choice]}")
                        print_dict_levels(current_dict, max_level=levels)
                    except ValueError:
                        print("Please enter a valid number")
                else:
                    print("Invalid section number")
            except ValueError:
                print("Please enter a valid number")
        else:
            print("Invalid choice")


def main():
    """
    Main entry point for the Palo Alto configuration parser.
    
    This function provides a command-line interface for parsing and
    exploring Palo Alto configuration files. It handles file selection,
    parsing, and interactive exploration of the configuration.
    
    Usage:
        $ python palo_alto.py [config_file]
    
    Features:
        - Command line argument support
        - Interactive file selection
        - Configuration exploration menu
        - Error handling and logging
    
    Example:
        >>> if __name__ == '__main__':
        ...     main()
    
    Notes:
        - Accepts optional command line argument for config file
        - Falls back to interactive mode if no file specified
        - Provides error messages for invalid files
        - Supports quit option at any point
    """
    # Parse XML file
    tree = ET.parse('input/UNCSO-Panorama-M-200_017607002338.xml')
    root = tree.getroot()

    # Convert to dictionary
    config_dict = PaloAltoParser._xml_to_dict(root)

    # Display interactive menu
    display_menu(config_dict)


if __name__ == "__main__":
    main()