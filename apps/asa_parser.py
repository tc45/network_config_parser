import pandas as pd
import logging
from ciscoconfparse2 import CiscoConfParse
from ntc_templates.parse import parse_output
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
import datetime
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class AsaParser:
    """Parser for Cisco ASA configuration files."""

    def __init__(self):
        self.hostname = "unknown" # Initialize hostname

    def parse_file(self, file_path):
        """Parse the ASA configuration file."""
        try:
            logging.info(f"Parsing file: {file_path}")
            with open(file_path, 'r') as file:
                config_data = file.read()
            return self.parse_data(config_data)
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logging.error(f"Failed to parse file: {e}")
            raise

    def parse_data(self, config_data):
        """Parse ASA configuration data from a string."""
        try:
            if self.is_running_config(config_data):
                logging.info("Detected running configuration. Using CiscoConfParse.")
                running_config_parser = AsaRunningConfigParser(config_data)
                parsed_data = running_config_parser.parse()
                self.hostname = running_config_parser.get_hostname() # Get hostname from sub-parser
                return parsed_data
            else:
                logging.debug("Splitting configuration into sections")
                sections = self.split_config_into_sections(config_data)
                parsed_data = {}
                for section_name, section_data in sections.items():
                    logging.debug(f"Parsing section: {section_name}")
                    parsed_data[section_name] = self.parse_section(section_name, section_data)
                return parsed_data
        except Exception as e:
            logging.error(f"Failed to parse data: {e}")
            raise

    def is_running_config(self, config_data):
        """Determine if the configuration data is a running configuration."""
        # Simple heuristic: check for common running-config markers
        return "ASA Version" in config_data and "interface" in config_data

    def split_config_into_sections(self, config_data):
        """Split the configuration into sections."""
        sections = {
            'interfaces': self.extract_section(config_data, 'interface'),
            'access_lists': self.extract_section(config_data, 'access-list'),
            # Add more sections as needed
        }
        logging.debug(f"Sections identified: {list(sections.keys())}")
        return sections

    def extract_section(self, config_data, section_keyword):
        """Extract a specific section from the configuration."""
        section_lines = []
        capture = False
        for line in config_data.splitlines():
            if line.startswith(section_keyword):
                capture = True
            if capture:
                section_lines.append(line)
            if line == '' and capture:
                break
        return '\n'.join(section_lines)

    def parse_section(self, section_name, section_data):
        """Parse a specific section of the configuration."""
        try:
            parsed_section = parse_output(platform='cisco_asa', command=f'show {section_name}', data=section_data)
            return parsed_section
        except Exception as e:
            logging.error(f"Failed to parse section {section_name}: {e}")
            return None

    def get_hostname(self):
        """Return the hostname found during parsing."""
        return self.hostname


class AsaRunningConfigParser:
    """
    Parser for Cisco ASA running configurations using CiscoConfParse.

    This class handles the parsing of ASA configuration files, with special focus on:
    - Access Lists (stored in self.access_lists)
    - Network Objects (stored in self.objects_data)
    - Interfaces, NAT rules, and Crypto maps

    Attributes:
        config_data (str): Raw configuration data to be parsed
        objects_data (dict): Dictionary of parsed network/service objects, keyed by object name
        access_lists (dict): Dictionary of parsed access lists, keyed by ACL name
    """

    def __init__(self, config_data):
        """
        Initialize the parser with configuration data.

        Args:
            config_data (str): Raw configuration data to be parsed
        """
        self.config_data = config_data
        self.objects_data = {}  # Dictionary to store parsed objects
        self.access_lists = {}  # Dictionary to store parsed access lists, organized by ACL name
        self.hostname = "unknown" # Initialize hostname

    def parse(self):
        """Parse the running configuration."""
        try:
            parse = CiscoConfParse(self.config_data.splitlines(), syntax='asa')
            parsed_data = {}

            # Extract general information
            parsed_data['general'] = self.parse_general_info(parse)
            # Store hostname found in general info
            if parsed_data['general']:
                 self.hostname = parsed_data['general'][0].get('Hostname', 'unknown')

            logging.debug(f"General Info: {parsed_data['general']}")

            # Extract interface configurations
            interfaces = parse.find_objects(r"^interface")
            parsed_data['interfaces'] = [
                self.parse_interface(interface)
                for interface in interfaces
            ]
            logging.debug(f"Interfaces: {parsed_data['interfaces']}")

            # Extract routes
            parsed_data['routes'] = self.parse_routes(parse)
            logging.debug(f"Routes: {parsed_data['routes']}")

            # Extract access lists and store them in self.access_lists
            access_lists = parse.find_objects(r"^access-list")
            parsed_data['access_lists'] = []
            for i, acl in enumerate(access_lists):
                parsed_acl = self.parse_access_list(acl, i + 1)
                parsed_data['access_lists'].append(parsed_acl)

                # Store in self.access_lists dictionary using ACL name as key
                acl_name = parsed_acl.get('ACL Name', '')
                if acl_name:
                    if acl_name not in self.access_lists:
                        self.access_lists[acl_name] = []
                    self.access_lists[acl_name].append(parsed_acl)

            logging.debug(f"Access Lists: {parsed_data['access_lists']}")

            # Extract object definitions
            objects = parse.find_objects(r"^object")
            parsed_data['objects'] = [
                entry
                for obj in objects
                for entry in self.parse_object(obj)
            ]
            logging.debug(f"Objects: {parsed_data['objects']}")

            # Store objects in the instance variable
            self.objects_data = {entry['Name']: entry for entry in parsed_data['objects']}

            # Extract NAT rules
            nat_rules = parse.find_objects(r"^nat")
            parsed_data['nat_rules'] = [
                self.parse_nat_rule(nat)
                for nat in nat_rules
            ]
            logging.debug(f"NAT Rules: {parsed_data['nat_rules']}")

            # Extract crypto map configurations
            crypto_maps = parse.find_objects(r"^crypto map")
            parsed_data['crypto_maps'] = [
                self.parse_crypto_map(crypto)
                for crypto in crypto_maps
            ]
            logging.debug(f"Crypto Maps: {parsed_data['crypto_maps']}")

            logging.info("Running configuration parsed successfully.")
            return parsed_data

        except Exception as e:
            logging.error(f"Failed to parse running configuration: {e}")
            raise

    def parse_general_info(self, parse):
        """Parse general information from the configuration."""
        general_info = {}

        # Extract hostname
        hostname_obj = parse.find_objects(r"^hostname")
        general_info['Hostname'] = hostname_obj[0].text.split()[-1] if hostname_obj else ''

        # Extract version
        version_obj = parse.find_objects(r"^ASA Version")
        general_info['Version'] = version_obj[0].text.split()[-1] if version_obj else ''

        # Count interfaces
        interfaces = parse.find_objects(r"^interface")
        general_info['# Interfaces'] = len(interfaces)

        # Count port-channels
        port_channels = parse.find_objects(r"^interface Port-channel")
        general_info['# Port Channels'] = len(port_channels)

        # Extract boot command
        boot_obj = parse.find_objects(r"^boot system")
        general_info['Boot Command'] = boot_obj[0].text if boot_obj else ''

        # Extract timezone
        timezone_obj = parse.find_objects(r"^clock timezone")
        general_info['Timezone'] = ' '.join(timezone_obj[0].text.split()[2:]) if timezone_obj else ''

        # Extract DNS information
        dns_servers = parse.find_objects(r"^dns server-group")
        dns_servers_list = []
        if dns_servers:
            for child in dns_servers[0].children:
                if 'name-server' in child.text:
                    dns_servers_list.append(child.text.split()[-1])
        general_info['DNS Servers'] = ', '.join(dns_servers_list)

        domain_obj = parse.find_objects(r"^domain-name")
        general_info['DNS Name'] = domain_obj[0].text.split()[-1] if domain_obj else ''

        # Count objects and object-groups
        objects = parse.find_objects(r"^object ")
        object_groups = parse.find_objects(r"^object-group")
        general_info['# Objects'] = len(objects)
        general_info['# Object-groups'] = len(object_groups)

        # Count access lists (excluding remarks)
        acl_count = 0
        acl_entries = parse.find_objects(r"^access-list")
        for acl in acl_entries:
            parts = acl.text.split()
            # Only count if it's not a remark line
            if len(parts) > 2 and parts[2] != 'remark':
                acl_count += 1
        general_info['# Access List'] = acl_count

        # Count NAT rules
        nat_rules = parse.find_objects(r"^nat")
        general_info['# NAT'] = len(nat_rules)

        # Count crypto tunnels (unique map numbers)
        crypto_maps = parse.find_objects(r"^crypto map")
        map_numbers = set()
        for crypto_map in crypto_maps:
            parts = crypto_map.text.split()
            if len(parts) > 3:  # Ensure we have enough parts
                try:
                    # Try to convert the third part to int to verify it's a number
                    map_number = int(parts[3])
                    map_numbers.add(map_number)
                except ValueError:
                    # Skip if not a number (e.g., interface application line)
                    continue
        general_info['# Crypto Tunnels'] = len(map_numbers)

        return [general_info]  # Return as list to maintain consistency with other sections

    def parse_routes(self, parse):
        """Parse static routes from the configuration."""
        routes = []
        route_entries = parse.find_objects(r"^route")

        for route in route_entries:
            parts = route.text.split()
            try:
                interface = parts[1]
                dest_network = parts[2]
                dest_subnet = parts[3]
                next_hop = parts[4]
                admin_distance = parts[5] if len(parts) > 5 else '1'

                routes.append({
                    'Interface': interface,
                    'Destination Network': dest_network,
                    'Destination Subnet': dest_subnet,
                    'Next Hop': next_hop,
                    'Admin Distance': admin_distance
                })
            except IndexError as e:
                logging.error(f"Failed to parse route: {route.text} - {e}")
                continue

        return routes

    def parse_interface(self, interface):
        """Parse interface details into separate columns."""
        try:
            ip_address_line = self.extract_child_value(interface, 'ip address')
            ip_address, subnet_mask, standby = self.split_ip_address(ip_address_line)
            return {
                'Interface': interface.text.split()[-1],
                'Nameif': self.extract_child_value(interface, 'nameif'),
                'Security Level': self.extract_child_value(interface, 'security-level'),
                'IP Address': ip_address,
                'Subnet Mask': subnet_mask,
                'CIDR': self.convert_to_cidr(subnet_mask),
                'Standby': standby,
                'Full Parsed Line': interface.text
            }
        except IndexError as e:
            logging.error(f"Failed to parse interface: {interface.text} - {e}")
            return {'Full Parsed Line': interface.text}

    def split_ip_address(self, ip_address_line):
        """Split IP address line into address, subnet mask, and standby."""
        parts = ip_address_line.split()
        ip_address = parts[0] if len(parts) > 0 else ''
        subnet_mask = parts[1] if len(parts) > 1 else ''
        standby = parts[3] if len(parts) > 3 else ''
        return ip_address, subnet_mask, standby

    def convert_to_cidr(self, subnet_mask):
        """Convert subnet mask to CIDR notation."""
        try:
            if not subnet_mask:
                logging.warning("Empty subnet mask encountered.")
                return ''
            return sum(bin(int(x)).count('1') for x in subnet_mask.split('.'))
        except ValueError as e:
            logging.error(f"Failed to convert subnet mask to CIDR: {subnet_mask} - {e}")
            return ''

    def extract_child_value(self, parent, keyword):
        """Extract the value of a child line that starts with a specific keyword."""
        for child in parent.children:
            if child.text.strip().startswith(keyword):
                return child.text.split(maxsplit=1)[-1]
        logging.warning(f"Keyword '{keyword}' not found in parent: {parent.text}")
        return ''

    def parse_access_list(self, acl, line_number):
        """
        Parse access list entries into structured data.

        This method handles complex ACL parsing including:
        - Object and object-group resolution
        - Network vs service object differentiation
        - Port specifications
        - Rule status (active/inactive)
        - Protocol handling from object-groups

        Args:
            acl: CiscoConfParse object representing an access-list entry
            line_number (int): Line number in the configuration

        Returns:
            dict: Parsed ACL entry with the following keys:
                - ACL Name
                - Line Number
                - Type
                - Action
                - Protocol
                - Source
                - Source Port
                - Destination
                - Destination Port
                - Log Status
                - Inactive
                - Remark
                - Full Parsed Line
        """
        try:
            # Split the ACL line into parts for parsing
            parts = acl.text.split()
            acl_name = parts[1] if len(parts) > 1 else ''
            acl_type = parts[2] if len(parts) > 2 else ''

            # Handle remark type ACLs differently
            if acl_type == 'remark':
                remark = ' '.join(parts[3:])
                # Return a remark entry with empty fields except for the remark text
                return {
                    'ACL Name': acl_name,
                    'Line Number': line_number,
                    'Type': 'remark',
                    'Action': '',
                    'Protocol': '',
                    'Source': '',
                    'Source Port': '',
                    'Destination': '',
                    'Destination Port': '',
                    'Log Status': '',
                    'Inactive': '',
                    'Remark': remark,
                    'Full Parsed Line': acl.text
                }
            else:
                # Parse regular ACL entries
                action = parts[3] if len(parts) > 3 else ''
                protocol = ''  # Initialize protocol as empty

                # Initialize parsing variables
                source, source_port, destination, destination_port = '', '', '', ''
                log_status = 'disable' if 'disable' in parts else ''
                inactive = 'Inactive' if 'inactive' in parts else ''

                # Process parts after action
                i = 4  # Start after action instead of protocol
                while i < len(parts):
                    part = parts[i]

                    # Skip keywords that don't need processing
                    if part in ['log', 'disable', 'inactive']:
                        i += 1
                        continue

                    # Handle object and object-group references
                    if part in ['object', 'object-group']:
                        if i + 1 < len(parts):
                            obj_name = parts[i + 1]
                            # Look up object type in objects_data dictionary
                            if obj_name in self.objects_data:
                                obj_type = self.objects_data[obj_name]['Object Type']

                                # Handle protocol object-groups
                                if obj_type in ['protocol', 'TCPUDP']:
                                    source = obj_name  # Store protocol object as source
                                # Network objects go to source/destination
                                elif obj_type in ['network', 'network-object']:
                                    if not source or source == protocol:  # If source is holding protocol, move to real source
                                        source = obj_name
                                    else:
                                        destination = obj_name
                                # Service objects go to port specifications
                                elif obj_type in ['service', 'service-object', 'tcp', 'udp']:
                                    if not destination_port:
                                        destination_port = obj_name
                                    elif not source_port:
                                        source_port = obj_name
                            else:
                                # Default handling for unknown objects
                                if not source or source == protocol:
                                    source = obj_name
                                else:
                                    destination = obj_name
                            i += 2  # Skip object name
                            continue

                    # Handle 'any' keyword in source/destination
                    elif part == 'any':
                        if not source or source == protocol:
                            source = 'any'
                        else:
                            destination = 'any'

                    # Handle explicit port specifications
                    elif part == 'eq' and i + 1 < len(parts):
                        if destination and not destination_port:
                            destination_port = parts[i + 1]
                        elif not source_port:
                            source_port = parts[i + 1]
                        i += 2  # Skip port number
                        continue
                    # Handle explicit protocols if specified
                    elif part in ['ip', 'tcp', 'udp', 'icmp']:
                        protocol = part

                    i += 1

                # Return the parsed ACL entry
                return {
                    'ACL Name': acl_name,
                    'Line Number': line_number,
                    'Type': acl_type,
                    'Action': action,
                    'Protocol': protocol,
                    'Source': source,
                    'Source Port': source_port,
                    'Destination': destination,
                    'Destination Port': destination_port,
                    'Log Status': log_status,
                    'Inactive': inactive,
                    'Remark': '',
                    'Full Parsed Line': acl.text
                }
        except Exception as e:
            logging.error(f"Failed to parse access list: {acl.text} - {e}")
            return {'Full Parsed Line': acl.text}

    def parse_object(self, obj):
        """Parse object into specified columns."""
        try:
            obj_name = self.extract_object_name(obj)
            obj_type = self.determine_object_type(obj)
            description = self.extract_description(obj)
            protocol = self.extract_protocol(obj)
            full_parsed_line = self.construct_full_parsed_line(obj)

            entries = []
            for child in obj.children:
                child_type, value = self.extract_object_details(child)
                if child_type:  # Ensure we only add valid child types
                    entries.append({
                        'Name': obj_name,
                        'Object Type': obj_type,
                        'Type': child_type,
                        'Value': value,
                        'Description': description,
                        'Object-Group Protocol': protocol,
                        'Full Parsed Line': full_parsed_line
                    })

            return entries
        except Exception as e:
            logging.error(f"Failed to parse object: {obj.text} - {e}")
            return [{'Full Parsed Line': obj.text}]

    def extract_object_name(self, obj):
        """Extract the object name."""
        parts = obj.text.split()
        return parts[2] if len(parts) > 2 else ''

    def determine_object_type(self, obj):
        """Determine the type of object or object-group."""
        parts = obj.text.split()
        if 'object-group' in parts:
            index = parts.index('object-group')
            return parts[index + 1] if len(parts) > index + 1 else 'object-group'
        elif 'object network' in obj.text:
            return 'network'
        elif 'object service' in obj.text:
            return 'service'
        return 'object'

    def extract_protocol(self, obj):
        """Extract protocol for object-group."""
        parts = obj.text.split()
        if 'object-group' in parts and len(parts) > 3:
            return parts[3]
        return ''

    def extract_description(self, obj):
        """Extract description if present."""
        for child in obj.children:
            if 'description' in child.text:
                return ' '.join(child.text.split()[1:])
        return ''

    def construct_full_parsed_line(self, obj):
        """Construct the full parsed line with parent and child objects."""
        child_lines = ''.join([f"[{child.text}]" for child in obj.children])
        return f"{obj.text} {child_lines}"

    def extract_object_details(self, child):
        """Extract object type and value from a child."""
        parts = child.text.split()
        if 'network-object' in parts:
            return 'network-object', parts[-1]
        elif 'subnet' in parts:
            return 'subnet', parts[-2]
        elif 'host' in parts:
            return 'host', parts[-1]
        elif 'fqdn' in parts:
            version = 'v4' if 'ipv4' in parts else 'v6'
            return f'FQDN {version}', parts[-1]
        elif 'range' in parts:
            return 'range', parts[-2]
        elif 'port-object' in parts:
            return 'port-object', parts[-1]
        elif 'service-object' in parts:
            return 'service-object', ' '.join(parts[1:])
        elif 'group-object' in parts:
            return 'group-object', parts[1]
        return '', ''

    def parse_nat_rule(self, nat):
        """Parse NAT rule into multiple columns."""
        try:
            parts = nat.text.split()
            return {
                'Source': parts[2] if len(parts) > 2 else '',
                'Destination': parts[4] if len(parts) > 4 else '',
                'Translation': parts[6] if len(parts) > 6 else '',
                'Options': ' '.join(parts[7:]) if len(parts) > 7 else '',
                'Full Parsed Line': nat.text
            }
        except IndexError as e:
            logging.error(f"Failed to parse NAT rule: {nat.text} - {e}")
            return {'Full Parsed Line': nat.text}

    def parse_crypto_map(self, crypto):
        """Parse crypto map into specified columns."""
        try:
            parts = crypto.text.split()
            map_name = parts[2] if len(parts) > 2 else ''
            line_number = parts[3] if len(parts) > 3 else ''
            match_address = self.extract_child_value(crypto, 'match address')
            peer = self.extract_child_value(crypto, 'set peer')
            ike_version = 'ikev1' if 'ikev1' in crypto.text else 'ikev2'
            transform_set = self.extract_child_value(crypto, 'set ikev1 transform-set')
            applied_interface = self.extract_child_value(crypto, 'interface')
            return {
                'Line Number': line_number,
                'Map Name': map_name,
                'Match Address': match_address,
                'Peer': peer,
                'IKE Version': ike_version,
                'Transform Set': transform_set,
                'Applied Interface': applied_interface,
                'Full Parsed Line': crypto.text
            }
        except IndexError as e:
            logging.error(f"Failed to parse crypto map: {crypto.text} - {e}")
            return {'Full Parsed Line': crypto.text}

    def get_hostname(self):
        """Return the hostname found during parsing."""
        return self.hostname