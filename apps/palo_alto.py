"""
Parser for Palo Alto configuration files.
Allows viewing nested dictionary structure at configurable depth levels.
"""
import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any, Optional
from tabulate import tabulate

# Get module logger
logger = logging.getLogger(__name__)

class PaloAltoParser:
    """Parser for Palo Alto configuration files"""

    def __init__(self):
        """Initialize the Palo Alto parser"""
        self.config_dict: Dict[str, Any] = {}
        self.hostname = "unknown"

    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """
        Parse a Palo Alto configuration file.

        Args:
            filepath: Path to the configuration file

        Returns:
            Dict containing the parsed data
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
        """Extract hostname from the configuration"""
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
        """Parse configuration sections into structured data"""
        parsed_data = {
            'Interfaces': self._parse_interfaces(),
            'Security Policies': self._parse_security_policies(),
            'NAT Policies': self._parse_nat_policies(),
            'Objects': self._parse_objects()
        }
        return parsed_data

    def _parse_interfaces(self) -> list:
        """Parse interface configurations"""
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
        """Parse security policies"""
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
        """Parse NAT policies"""
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
        """Parse address and service objects"""
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
        """Convert XML to dictionary recursively"""
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
        """Return the hostname found during parsing"""
        return self.hostname


def print_dict_levels(d: Dict[str, Any], current_level: int = 0,
                      max_level: Optional[int] = None, indent: str = ""):
    """
    Print dictionary structure up to specified number of levels.

    Args:
        d: Dictionary to print
        current_level: Current depth level (used internally for recursion)
        max_level: Maximum depth level to print
        indent: Indentation string (used internally for formatting)
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
    Get all items at level 2 of the dictionary.

    Args:
        d: Dictionary to analyze

    Returns:
        List of level 2 items
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
    Display interactive menu for viewing configuration.

    Args:
        config_dict: Configuration dictionary to display
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
    Main function to parse Palo Alto config and display structure.
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