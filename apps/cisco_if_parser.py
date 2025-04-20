#!/usr/bin/env python3

"""
Cisco Configuration Parser - Parses interface and access-list configurations
from Cisco devices and creates formatted output.
"""

import argparse
import logging
import re
import os
from datetime import datetime
from typing import Dict, List, Optional
from ciscoconfparse2 import CiscoConfParse
from tabulate import tabulate
import ipaddress
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
import sys
from openpyxl import Workbook, load_workbook

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure rich console with custom theme
custom_theme = Theme({
    "info": "green",
    "warning": "yellow",
    "error": "orange1",
    "debug": "red"
})
console = Console(theme=custom_theme)

# Configure logging with both file and rich console handlers
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        # Rich console handler
        RichHandler(
            console=console,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True
        ),
        # File handler
        logging.FileHandler(
            filename='logs/cisco_parser.log',
            mode='a',  # Append mode
            encoding='utf-8'
        )
    ]
)

logger = logging.getLogger(__name__)


class CiscoConfigParser:
    """Base class for Cisco configuration parsers"""

    # Class-level cache for storing parsed sections
    _section_cache = {}

    def __init__(self, show_tech_file: str):
        """
        Initialize the base parser

        Args:
            show_tech_file (str): Path to the show tech file
        """
        self.show_tech_file = show_tech_file
        self.hostname = "unknown"
        self.running_config: Optional[str] = None
        self.device_type: Optional[str] = None

        # Check if file has already been parsed
        if show_tech_file in self._section_cache:
            cache = self._section_cache[show_tech_file]
            self.running_config = cache['running_config']
            self.device_type = cache['device_type']
            self.hostname = cache['hostname']
            logger.debug(f"Using cached sections for {show_tech_file}")
        else:
            self._extract_sections()

    def _extract_sections(self) -> None:
        """Extract sections from show tech output"""
        try:
            # Read file with ASCII encoding
            with open(self.show_tech_file, 'r', encoding='ascii') as f:
                content = f.read()

            # Determine device type and store it
            self.device_type = _determine_device_type(content)

            if self.device_type == "Nexus Switch":
                logger.debug("Detected Nexus device, using Nexus-style parsing")
                # More flexible pattern for Nexus running-config
                running_patterns = [
                    r'(?:^|\n)(?:`show running-config`|show running-config\n)',
                    r'(?:^|\n)(?:`show running`|show running\n)',
                    r'(?:^|\n)[\s\*]*show running-config[\s\*]*\n',
                    r'(?:^|\n)[\s\*]*show running[\s\*]*\n'
                ]

                # Try each pattern until we find a match
                for pattern in running_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        start_pos = match.end()
                        # More flexible pattern for next show command
                        next_show = re.search(
                            r'(?:^|\n)(?:`show|show\s+|[\s\*]*show\s+)',
                            content[start_pos:]
                        )

                        if next_show:
                            end_pos = start_pos + next_show.start()
                            config_section = content[start_pos:end_pos].strip()
                        else:
                            # If no next show command found, take rest of content
                            config_section = content[start_pos:].strip()

                        # Verify this is actually a config section by checking for common config elements
                        if re.search(r'version|hostname|interface|boot|system|feature', config_section, re.MULTILINE):
                            self.running_config = config_section
                            logger.debug(
                                f"Found Nexus running-config section with {len(self.running_config.splitlines())} lines")
                            break

                    if self.running_config:
                        break

                # If still no running config found, try one more time with section markers
                if not self.running_config:
                    logger.debug("Trying alternative Nexus section parsing")
                    sections = re.split(r'\n={3,}|\n-{3,}|\n\*{3,}', content)
                    for section in sections:
                        if re.search(r'show running-config|show running', section[:100], re.IGNORECASE):
                            if re.search(r'version|hostname|interface|boot|system|feature', section, re.MULTILINE):
                                self.running_config = section.strip()
                                logger.debug(f"Found Nexus running-config using alternative parsing")
                                break

            else:
                logger.debug(f"Detected {self.device_type}, using IOS-style parsing")
                # IOS-style section parsing
                sections = re.split(r'\n-{18,} .* -+\n', content)
                section_headers = re.findall(r'\n(-{18,} .* -+)\n', content)

                logger.debug(f"Found {len(section_headers)} sections in show tech")

                # Find the running-config section
                for i, header in enumerate(section_headers):
                    if 'show running-config' in header.lower() or 'show running' in header.lower():
                        self.running_config = sections[i + 1]
                        logger.debug(
                            f"Found IOS running-config section with {len(self.running_config.splitlines())} lines")
                        break

            if not self.running_config:
                logger.error("Could not find running-config section")
                raise ValueError("Running-config section not found in show tech")

            # Extract hostname from running-config - improved pattern matching
            hostname_pattern = re.compile(r'^hostname\s+(\S+)', re.MULTILINE)
            hostname_match = hostname_pattern.search(self.running_config)
            if hostname_match:
                self.hostname = hostname_match.group(1)
                logger.info(f"Found hostname: {self.hostname}")
            else:
                logger.warning("Could not find hostname in running-config")
                self.hostname = "unknown"

            # Cache the parsed sections
            self._section_cache[self.show_tech_file] = {
                'running_config': self.running_config,
                'device_type': self.device_type,
                'hostname': self.hostname
            }

        except Exception as e:
            logger.error(f"Failed to process show tech file: {e}")
            raise

    def _convert_wildcard_to_cidr(self, ip: str, wildcard: str) -> str:
        """
        Convert IP with wildcard mask to CIDR notation

        Args:
            ip (str): IP address
            wildcard (str): Wildcard mask

        Returns:
            str: IP address in CIDR notation
        """
        try:
            # Convert wildcard to netmask
            wildcard_parts = [int(x) for x in wildcard.split('.')]
            netmask_parts = [255 - x for x in wildcard_parts]
            netmask = '.'.join(str(x) for x in netmask_parts)

            # Create network with netmask
            network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
            return str(network)
        except Exception as e:
            logger.error(f"Failed to convert wildcard to CIDR: {e}")
            return f"{ip}/{wildcard}"

    def save_to_excel(self, data: List[Dict], headers: List[str], sheet_name: str) -> str:
        """
        Save data to Excel worksheet

        Args:
            data: List of dictionaries containing the data
            headers: List of column headers
            sheet_name: Name of the worksheet

        Returns:
            str: Path to Excel file
        """
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)

        # Generate filename based on hostname with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/{self.hostname}_{timestamp}.xlsx"

        try:
            # Load existing workbook or create new one
            if os.path.exists(filename):
                wb = load_workbook(filename)
                # Remove sheet if it already exists
                if sheet_name in wb.sheetnames:
                    wb.remove(wb[sheet_name])
            else:
                wb = Workbook()
                # Remove default sheet
                if 'Sheet' in wb.sheetnames:
                    wb.remove(wb['Sheet'])

            # Create new worksheet
            ws = wb.create_sheet(sheet_name)

            # Write headers
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)

            # Write data
            for row, entry in enumerate(data, 2):
                for col, header in enumerate(headers, 1):
                    ws.cell(row=row, column=col, value=entry[header])

            # Save workbook
            wb.save(filename)
            logger.info(f"Successfully saved data to {sheet_name} sheet in {filename}")
            return filename

        except Exception as e:
            logger.error(f"Failed to save Excel file: {e}")
            raise


class CiscoACLParser(CiscoConfigParser):
    """Parser for Cisco access-list configurations"""

    def __init__(self, show_tech_file: str):
        """Initialize the ACL parser"""
        super().__init__(show_tech_file)
        self.acls: List[Dict] = []
        self._parse_acls()

    def _parse_acls(self) -> None:
        """Parse access-list configurations"""
        if not self.running_config:
            return

        self.acls = []  # Reset ACLs list

        try:
            # First find all unique ACL numbers/names
            acl_ids = set()
            logger.debug("Scanning config for access-lists...")
            for line in self.running_config.splitlines():
                line = line.strip()
                if line.startswith('access-list'):
                    parts = line.split()
                    if len(parts) >= 2:
                        acl_ids.add(parts[1])

            # Log all found ACLs before starting processing
            logger.debug(f"Found these ACLs in config: {', '.join(sorted(acl_ids))}")

            # Now process each ACL
            for acl_id in sorted(acl_ids):
                logger.debug(f"Processing access-list {acl_id}")
                current_remarks = []
                line_number = 0

                # Find all lines for this ACL
                acl_lines = [line.strip() for line in self.running_config.splitlines()
                             if line.strip().startswith(f'access-list {acl_id}')]

                # Process each line for this ACL
                for line in acl_lines:
                    parts = line.split()

                    # Handle remarks
                    if parts[2] == 'remark':
                        remark = ' '.join(parts[3:])
                        current_remarks.append(remark)
                        logger.debug(f"Found Remark in access-list {acl_id} - {remark}")
                        continue

                    # Increment line number for non-remark entries
                    line_number += 1
                    logger.debug(f"Processing line {line_number} of access-list {acl_id} - {line}")

                    # Create entry
                    entry = {
                        'Line': line_number,
                        'Number': acl_id,
                        'Action': parts[2],
                        'Protocol': parts[3],
                        'Src-IP': '',
                        'Src-Protocol': '',
                        'Dst-IP': '',
                        'Dst-Protocol': '',
                        'Remark': ' | '.join(current_remarks)
                    }

                    # Parse source
                    idx = 4
                    if parts[idx] == 'host':
                        entry['Src-IP'] = f"{parts[idx + 1]}/32"
                        idx += 2
                    elif parts[idx] == 'any':
                        entry['Src-IP'] = 'any'
                        idx += 1
                    else:
                        if idx + 1 < len(parts) and re.match(r'\d+\.\d+\.\d+\.\d+', parts[idx + 1]):
                            entry['Src-IP'] = self._convert_wildcard_to_cidr(parts[idx], parts[idx + 1])
                            idx += 2
                        else:
                            entry['Src-IP'] = parts[idx]
                            idx += 1

                    # Parse destination
                    if idx < len(parts):
                        if parts[idx] == 'host':
                            entry['Dst-IP'] = f"{parts[idx + 1]}/32"
                            idx += 2
                        elif parts[idx] == 'any':
                            entry['Dst-IP'] = 'any'
                            idx += 1
                        else:
                            if idx + 1 < len(parts) and re.match(r'\d+\.\d+\.\d+\.\d+', parts[idx + 1]):
                                entry['Dst-IP'] = self._convert_wildcard_to_cidr(parts[idx], parts[idx + 1])
                                idx += 2
                            else:
                                entry['Dst-IP'] = parts[idx]
                                idx += 1

                    # Parse remaining protocol information
                    while idx < len(parts):
                        if parts[idx] in ['eq', 'gt', 'lt', 'neq']:
                            protocol_value = parts[idx + 1]
                            if parts[idx] != 'eq':
                                protocol_value = f"{parts[idx]} {protocol_value}"

                            if not entry['Src-Protocol'] and entry['Protocol'] in ['tcp', 'udp']:
                                entry['Src-Protocol'] = protocol_value
                            else:
                                entry['Dst-Protocol'] = protocol_value
                            idx += 2
                        elif parts[idx] == 'established':
                            entry['Dst-Protocol'] = 'established'
                            idx += 1
                        else:
                            idx += 1

                    logger.debug(f"Parsed line {line_number} of access-list {acl_id} - " +
                                 f"Line: {entry['Line']}, Number: {entry['Number']}, " +
                                 f"Action: {entry['Action']}, Protocol: {entry['Protocol']}, " +
                                 f"Src-IP: {entry['Src-IP']}, Src-Protocol: {entry['Src-Protocol']}, " +
                                 f"Dst-IP: {entry['Dst-IP']}, Dst-Protocol: {entry['Dst-Protocol']}, " +
                                 f"Remark: {entry['Remark']}")

                    self.acls.append(entry)

                logger.debug(f"Completed processing access-list {acl_id}")

        except Exception as e:
            logger.error(f"Failed to parse ACL entry: {e}")
            raise

    def save_output(self, display: bool = False) -> None:
        """
        Save or display ACL information

        Args:
            display (bool): If True, display table. If False, save to Excel
        """
        # Check if any ACLs were found
        if not self.acls:
            logger.info("No ACLs found in configuration")
            return

        headers = ["Line", "Number", "Action", "Protocol", "Src-IP",
                   "Src-Protocol", "Dst-IP", "Dst-Protocol", "Remark"]

        if display:
            print(tabulate(self.acls, headers=headers, tablefmt="grid"))
        else:
            filename = self.save_to_excel(self.acls, headers, "ACLs")
            print(f"ACL data saved to: {filename}")


class CiscoInterfaceParser(CiscoConfigParser):
    """Parser for Cisco interface configurations"""

    def __init__(self, show_tech_file: str):
        """Initialize the interface parser"""
        super().__init__(show_tech_file)
        self.interfaces: Dict = {}
        self.show_interfaces: Optional[str] = None
        self.show_interfaces_brief: Optional[str] = None
        self._extract_interface_section()
        self._parse_interfaces()

    def _extract_interface_section(self) -> None:
        """Extract show interfaces section from show tech"""
        try:
            with open(self.show_tech_file, 'r', encoding='ascii') as f:
                content = f.read()

            # Extract show interface(s) section - handle both singular and plural forms
            if self.device_type == "Nexus Switch":
                # For Nexus devices - look for both detailed and brief outputs
                show_int_detailed = re.search(
                    r'(?:^|\n)(?:`show interface[s]?`|show interface[s]?\n)(.*?)(?=\n`show|\nshow\s|$)',
                    content, re.DOTALL
                )
                show_int_brief = re.search(
                    r'(?:^|\n)(?:`show interface[s]? brief`|show interface[s]? brief\n)(.*?)(?=\n`show|\nshow\s|$)',
                    content, re.DOTALL
                )

                if show_int_detailed:
                    self.show_interfaces = show_int_detailed.group(1)
                    logger.info("Found Nexus detailed interface section")
                if show_int_brief:
                    self.show_interfaces_brief = show_int_brief.group(1)
                    logger.info("Found Nexus brief interface section")

                if not (show_int_detailed or show_int_brief):
                    logger.warning("Could not find Nexus interface sections")
            else:
                # For IOS devices - original behavior
                show_int_match = re.search(
                    r'------------------ show interface[s]? ------------------\n(.*?)(?=\n-{18,}|\Z)',
                    content, re.DOTALL | re.MULTILINE
                )

                if show_int_match:
                    self.show_interfaces = show_int_match.group(1)
                    logger.info("Successfully extracted IOS interface section")
                else:
                    logger.warning("Could not find IOS interface section")

        except Exception as e:
            logger.error(f"Failed to extract interface sections: {e}")

    def _normalize_interface_name(self, if_name: str) -> str:
        """
        Normalize interface names between running-config and show interface brief formats

        Args:
            if_name (str): Interface name to normalize

        Returns:
            str: Normalized interface name
        """
        # Strip any leading/trailing whitespace
        if_name = if_name.strip()

        # Handle Ethernet interfaces
        if if_name.lower().startswith(('eth', 'ethernet')):
            # Extract the interface number
            match = re.search(r'(?:eth(?:ernet)?)\s*(\d+/\d+(?:/\d+)?)', if_name, re.IGNORECASE)
            if match:
                return f"Ethernet{match.group(1)}"

        # Handle Port-channel interfaces
        elif if_name.lower().startswith(('po', 'port-channel')):
            # Extract the port-channel number
            match = re.search(r'(?:po(?:rt-channel)?)\s*(\d+)', if_name, re.IGNORECASE)
            if match:
                return f"port-channel{match.group(1)}"

        # Handle VLAN interfaces
        elif if_name.lower().startswith('vlan'):
            # Extract the VLAN number
            match = re.search(r'vlan\s*(\d+)', if_name, re.IGNORECASE)
            if match:
                return f"Vlan{match.group(1)}"

        # Handle mgmt interfaces
        elif if_name.lower().startswith(('mgmt', 'management')):
            # Extract the management interface number
            match = re.search(r'(?:mgmt(?:mt)?)\s*(\d+/\d+)', if_name, re.IGNORECASE)
            if match:
                return f"mgmt{match.group(1)}"

        # Return original name if no normalization needed
        return if_name

    def _get_column_positions(self, header_line: str, section_type: str) -> Dict[str, tuple]:
        """
        Get the start and end positions of each column from the header line

        Args:
            header_line (str): The header line containing column names
            section_type: Type of section being parsed (ethernet, portchannel, vlan, mgmt)

        Returns:
            Dict[str, tuple]: Dictionary of column name to (start, end) positions
        """
        logger.debug(f"Getting column positions for section type: {section_type}")
        logger.debug(f"Header line: {header_line}")

        # Get the first line after the dashed separator
        lines = [line for line in header_line.splitlines() if line.strip() and not line.startswith('-')]
        if not lines:
            return {}

        header = lines[0]  # Use only the first header line
        logger.debug(f"Using header line: {header}")

        # Define column names and their identifying text for each section type
        if section_type == 'ethernet':
            # Define the column headers we're looking for
            columns = {}

            # Find Ethernet column (starts at position 0)
            columns['interface'] = (0, 13)  # Ethernet takes up about 13 chars
            columns['vlan'] = (13, 21)  # VLAN takes up about 8 chars
            columns['type'] = (21, 26)  # Type takes up about 5 chars
            columns['mode'] = (26, 33)  # Mode takes up about 7 chars
            columns['status'] = (33, 41)  # Status takes up about 8 chars
            columns['reason'] = (41, 65)  # Reason takes up about 24 chars
            columns['speed'] = (65, 75)  # Speed takes up about 10 chars
            columns['port_ch'] = (75, 80)  # Port Ch # takes the rest

        elif section_type == 'portchannel':
            columns = {}
            columns['interface'] = (0, 13)
            columns['vlan'] = (13, 21)
            columns['type'] = (21, 26)
            columns['mode'] = (26, 33)
            columns['status'] = (33, 41)
            columns['reason'] = (41, 65)
            columns['speed'] = (65, 73)
            columns['port_ch'] = (73, 80)  # Protocol field

        elif section_type == 'vlan':
            columns = {}
            columns['interface'] = (0, 10)
            columns['vlan'] = (10, 45)  # Secondary VLAN(Type) field
            columns['status'] = (45, 53)
            columns['reason'] = (53, 80)

        elif section_type == 'mgmt':
            columns = {}
            columns['interface'] = (0, 7)
            columns['vrf'] = (7, 19)
            columns['status'] = (19, 28)
            columns['ip'] = (28, 65)
            columns['speed'] = (65, 73)
            columns['mtu'] = (73, 80)

        logger.debug(f"Mapped columns: {columns}")
        return columns

    def _parse_interface_line(self, line: str, columns: Dict[str, tuple]) -> Dict[str, str]:
        """
        Parse a line of interface data using column positions

        Args:
            line (str): The line to parse
            columns: Dictionary of column positions

        Returns:
            Dict[str, str]: Parsed interface data
        """
        data = {}

        # Ensure line is at least as long as the last column position
        max_pos = max(end for start, end in columns.values())
        padded_line = line.ljust(max_pos)

        # Extract each field using column positions
        for field, (start, end) in columns.items():
            value = padded_line[start:end].strip()

            # Special handling for port_ch field - extract only numerical value
            if field == 'port_ch':
                # Find any number in the value
                match = re.search(r'\d+', value)
                value = match.group() if match else ''

            data[field] = value
            logger.debug(f"Extracted {field}: '{value}' from positions {start}:{end}")

        return data

    def _parse_interfaces(self) -> None:
        """Parse interface configurations"""
        if not self.running_config:
            return

        try:
            parse = CiscoConfParse(self.running_config.splitlines())
            interface_objs = parse.find_objects(r"^interface")

            logger.debug(f"Found {len(interface_objs)} interfaces in running-config")

            for interface in interface_objs:
                interface_name = interface.text.split("interface ")[1]
                normalized_name = self._normalize_interface_name(interface_name)
                logger.debug(f"\nParsing interface configuration for: {interface_name} (normalized: {normalized_name})")

                # Initialize interface dictionary using normalized name
                self.interfaces[normalized_name] = {
                    "if_name": normalized_name,
                    "vlan": "",
                    "type": self._determine_type(normalized_name),
                    "mode": "",
                    "status": "",
                    "reason": "",
                    "speed": "",
                    "port_channel": "",
                    "description": ""
                }

                # Parse interface details
                for child in interface.children:
                    logger.debug(f"  Processing child config: {child.text}")
                    if "description" in child.text:
                        self.interfaces[normalized_name]["description"] = child.text.split("description ")[1]
                        logger.debug(f"    Found description: {self.interfaces[normalized_name]['description']}")
                    elif "switchport access vlan" in child.text:
                        self.interfaces[normalized_name]["vlan"] = child.text.split("switchport access vlan ")[1]
                        self.interfaces[normalized_name]["mode"] = "access"
                        logger.debug(f"    Found access VLAN: {self.interfaces[normalized_name]['vlan']}")
                    elif "switchport trunk native vlan" in child.text:
                        self.interfaces[normalized_name]["vlan"] = child.text.split("switchport trunk native vlan ")[1]
                        self.interfaces[normalized_name]["mode"] = "trunk"
                        logger.debug(f"    Found trunk native VLAN: {self.interfaces[normalized_name]['vlan']}")
                    elif "switchport mode trunk" in child.text:
                        self.interfaces[normalized_name]["mode"] = "trunk"
                        logger.debug(f"    Found trunk mode")
                    elif "channel-group" in child.text:
                        port_channel = child.text.split("channel-group ")[1].split(" ")[0]
                        self.interfaces[normalized_name]["port_channel"] = port_channel
                        logger.debug(f"    Found port-channel: {port_channel}")

                # Set mode to routed if no switchport commands found
                if not self.interfaces[normalized_name]["mode"]:
                    self.interfaces[normalized_name]["mode"] = "routed"
                    logger.debug(f"    No switchport mode found, setting to routed")

            logger.debug("\nCompleted initial interface parsing from running-config")
            self._update_interface_status()

        except Exception as e:
            logger.error(f"Failed to parse interfaces: {e}")
            raise

    def _determine_type(self, interface_name: str) -> str:
        """
        Determine interface type based on interface name

        Args:
            interface_name (str): Name of the interface

        Returns:
            str: Interface type (ethernet, vlan, or port-channel)
        """
        if interface_name.lower().startswith("vlan"):
            return "vlan"
        elif interface_name.lower().startswith("port-channel"):
            return "port-channel"
        else:
            return "ethernet"

    def _update_interface_status(self) -> None:
        """Update interface status from show interfaces section"""
        if not (hasattr(self, 'show_interfaces') or hasattr(self, 'show_interfaces_brief')):
            logger.debug("No interface status sections found")
            return

        try:
            if self.device_type == "Nexus Switch":
                logger.debug("\nProcessing Nexus interface status:")
                if hasattr(self, 'show_interfaces_brief'):
                    brief_lines = self.show_interfaces_brief.splitlines()
                    current_section = None
                    current_columns = None
                    in_section = False

                    for line in brief_lines:
                        line = line.strip()

                        # Skip empty lines
                        if not line:
                            continue

                        # Check for section separator
                        if line.startswith('-'):
                            in_section = not in_section  # Toggle section state
                            continue

                        # If we're at the start of a section, check for headers
                        if in_section:
                            if 'Ethernet' in line and 'VLAN' in line:
                                current_section = 'ethernet'
                                current_columns = self._get_column_positions(line, 'ethernet')
                                logger.debug("Entering ethernet section")
                                in_section = False  # Reset to handle data lines
                                continue
                            elif 'Port-channel' in line and 'VLAN' in line:
                                current_section = 'portchannel'
                                current_columns = self._get_column_positions(line, 'portchannel')
                                logger.debug("Entering port-channel section")
                                in_section = False
                                continue
                            # Add other section checks...

                        # Skip the interface/header continuation line
                        if 'Interface' in line or 'Ch #' in line:
                            continue

                        # Process data lines
                        if current_section and current_columns:
                            parsed_data = self._parse_interface_line(line, current_columns)
                            logger.debug(f"Parsed line: {line}")
                            logger.debug(f"Parsed data: {parsed_data}")

                            if_name = self._normalize_interface_name(parsed_data['interface'])
                            logger.debug(f"Normalized interface name: {if_name}")

                            if if_name in self.interfaces:
                                logger.debug(f"Updating interface {if_name}")
                                update_data = {
                                    "status": parsed_data['status']
                                }

                                # Add fields based on section type
                                if current_section in ['ethernet', 'portchannel']:
                                    update_data.update({
                                        "vlan": parsed_data['vlan'],
                                        "reason": parsed_data['reason'],
                                        "speed": parsed_data['speed'].split('(')[0].strip(),  # Remove (D) suffix
                                    })
                                    if 'port_ch' in parsed_data:
                                        if parsed_data['port_ch'] != '--':
                                            update_data["port_channel"] = parsed_data['port_ch']
                                elif current_section == 'vlan':
                                    update_data.update({
                                        "reason": parsed_data['reason']
                                    })

                                self.interfaces[if_name].update(update_data)
                            else:
                                logger.debug(f"Interface {if_name} not found in running-config")

                    logger.debug("\nCompleted parsing Nexus interface brief output")

                    # Continue with detailed output parsing for any missing information
                    if hasattr(self, 'show_interfaces'):
                        interface_sections = re.split(r'\n(?=\S+? is)', self.show_interfaces)
                        for section in interface_sections:
                            name_match = re.match(r'(\S+?) is', section)
                            if not name_match:
                                continue

                            if_name = self._normalize_interface_name(name_match.group(1))
                            if if_name not in self.interfaces:
                                continue

                            # Update speed if not already set
                            if not self.interfaces[if_name].get("speed"):
                                bw_match = re.search(r'BW (\d+) (?:Kbit|kbit)', section)
                                if bw_match:
                                    speed_kbps = int(bw_match.group(1))
                                    self.interfaces[if_name]["speed"] = self._convert_speed(speed_kbps)

            else:
                # Original IOS parsing logic
                if not hasattr(self, 'show_interfaces'):
                    return

                interface_sections = re.split(r'\n(?=\S+? is)', self.show_interfaces)
                for section in interface_sections:
                    name_match = re.match(r'(\S+?) is', section)
                    if not name_match:
                        continue

                    if_name = name_match.group(1)
                    if if_name not in self.interfaces:
                        continue

                    status_match = re.search(r'line protocol is (\S+)', section)
                    if status_match:
                        self.interfaces[if_name]["status"] = status_match.group(1)

                    bw_match = re.search(r'BW (\d+) (?:Kbit|kbit)', section)
                    if bw_match:
                        speed_kbps = int(bw_match.group(1))
                        self.interfaces[if_name]["speed"] = self._convert_speed(speed_kbps)

        except Exception as e:
            logger.error(f"Failed to update interface status: {e}")

    def _convert_speed(self, speed_kbps: int) -> str:
        """
        Convert speed from Kbit/sec to human readable format

        Args:
            speed_kbps (int): Speed in Kbit/sec

        Returns:
            str: Formatted speed string
        """
        if speed_kbps >= 10000000:
            return "10G"
        elif speed_kbps >= 1000000:
            return "1G"
        elif speed_kbps >= 100000:
            return "100M"
        elif speed_kbps >= 10000:
            return "10M"
        else:
            return f"{speed_kbps}K"

    def save_output(self, display: bool = False) -> None:
        """
        Save or display interface information

        Args:
            display (bool): If True, display table. If False, save to Excel
        """
        headers = ["Interface", "VLAN", "Type", "Mode", "Status", "Reason",
                   "Speed", "Port-Channel", "Description"]

        # Convert interface dictionary to list of rows
        table_data = [
            {
                "Interface": data["if_name"],
                "VLAN": data["vlan"],
                "Type": data["type"],
                "Mode": data["mode"],
                "Status": data["status"],
                "Reason": data["reason"],
                "Speed": data["speed"],
                "Port-Channel": data["port_channel"],
                "Description": data["description"]
            }
            for data in self.interfaces.values()
        ]

        if display:
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            filename = self.save_to_excel(table_data, headers, "Interfaces")
            print(f"Interface data saved to: {filename}")


def _determine_device_type(content: str) -> str:
    """
    Determine device type by examining show version output

    Args:
        content (str): File content

    Returns:
        str: Device type
    """
    # First try to find show version section
    version_match = None

    # Try IOS-style section marker with flexible whitespace
    ios_version = re.search(
        r'-{18,}\s*show\s+version\s*-+\n(.*?)(?=\n-{18,}|\Z)',
        content, re.DOTALL | re.MULTILINE
    )

    # Try Nexus-style command output with flexible whitespace
    nexus_version = re.search(
        r'(?:^|\n)(?:`show\s+version\s*`|show\s+version\s*\n)(.*?)(?=\n`show|\nshow\s|$)',
        content, re.DOTALL
    )

    version_text = ""
    if ios_version:
        version_text = ios_version.group(1)
    elif nexus_version:
        version_text = nexus_version.group(1)

    logger.debug("Version text found:")
    logger.debug(version_text[:200] + "...")  # Show first 200 chars

    # Determine device type from version text - case insensitive matching
    if re.search(r'NX-OS|Nexus', version_text, re.IGNORECASE):
        return "Nexus Switch"
    elif re.search(r'IOS-XE.*Catalyst|Catalyst.*IOS-XE', version_text, re.IGNORECASE):
        return "Catalyst Switch"
    elif re.search(r'IOS-XE', version_text, re.IGNORECASE):
        return "IOS-XE Router"
    elif re.search(r'IOS Software', version_text, re.IGNORECASE):
        return "IOS Router"
    else:
        return "Unknown Cisco Device"


def sanitize_file_content(filepath: str) -> str:
    """
    Sanitize file content to ASCII-only and save original if modified

    Args:
        filepath (str): Path to the file to sanitize

    Returns:
        str: Path to the sanitized file
    """
    try:
        # First try to read with utf-8 to detect non-ASCII characters
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Check if content needs sanitization
        if all(ord(c) < 128 for c in content):
            logger.debug(f"File {filepath} is already ASCII-only")
            return filepath

        # Create originals directory if it doesn't exist
        originals_dir = os.path.join('input', 'originals')
        os.makedirs(originals_dir, exist_ok=True)

        # Move original file to originals directory
        original_path = os.path.join(originals_dir, os.path.basename(filepath))
        if not os.path.exists(original_path):
            os.rename(filepath, original_path)
            logger.debug(f"Moved original file to {original_path}")

        # Create sanitized content by replacing non-ASCII characters
        sanitized_content = ''.join(c if ord(c) < 128 else ' ' for c in content)

        # Write sanitized content back to original filepath
        with open(filepath, 'w', encoding='ascii') as f:
            f.write(sanitized_content)

        logger.info(f"Created ASCII-only version of {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Failed to sanitize file {filepath}: {e}")
        return filepath


def find_cisco_files() -> List[Dict]:
    """
    Find all Cisco show tech files in input directory

    Returns:
        List[Dict]: List of dictionaries containing file info
    """
    cisco_files = []
    file_id = 1

    # Create input directory if it doesn't exist
    os.makedirs('input', exist_ok=True)

    # Search through input directory
    for filename in os.listdir('input'):
        if filename == 'originals':  # Skip originals directory
            continue

        filepath = os.path.join('input', filename)
        if not os.path.isfile(filepath):
            continue

        try:
            # Create temporary parser to get device info
            parser = CiscoConfigParser(filepath)

            cisco_files.append({
                'id': file_id,
                'filename': filepath,
                'hostname': parser.hostname,
                'device_type': parser.device_type
            })
            file_id += 1
            logger.debug(f"Added {filepath} as {parser.device_type}")

        except Exception as e:
            logger.warning(f"Could not process {filepath}: {e}")
            continue

    return cisco_files


def display_file_selection(files: List[Dict]) -> None:
    """Display available Cisco show tech files"""
    if not files:
        print("No Cisco show tech files found in input directory")
        return

    headers = ["ID", "Hostname", "Device Type", "Filename"]
    table_data = [
        [f['id'], f['hostname'], f['device_type'], f['filename']]
        for f in files
    ]
    print("\nAvailable Cisco show tech files:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print("\nOptions:")
    print("  <id>   : Parse single file by ID")
    print("  all    : Parse all files")
    print("  q      : Quit")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Cisco Configuration Parser")
    parser.add_argument("--show-tech",
                        help="Path to show tech file (optional)")
    parser.add_argument("--display", action="store_true",
                        help="Display output in table format instead of saving to Excel")
    parser.add_argument("--type", choices=['interface', 'acl', 'both'], default='both',
                        help="Type of configuration to parse")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")
    args = parser.parse_args()

    # Set logging level based on debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # If show-tech is provided, process that file directly
        if args.show_tech:
            process_file(args.show_tech, args.type, args.display)
            return

        # Otherwise, show file selection
        cisco_files = find_cisco_files()
        while True:
            try:
                display_file_selection(cisco_files)
                choice = input("\nEnter selection: ").strip().lower()

                if choice == 'q':
                    break
                elif choice == 'all':
                    for file_info in cisco_files:
                        print(f"\nProcessing {file_info['filename']}...")
                        process_file(file_info['filename'], args.type, args.display)
                else:
                    try:
                        file_id = int(choice)
                        file_info = next((f for f in cisco_files if f['id'] == file_id), None)
                        if file_info:
                            process_file(file_info['filename'], args.type, args.display)
                        else:
                            print(f"Invalid ID: {file_id}")
                    except ValueError:
                        print("Invalid selection")

            except KeyboardInterrupt:
                print("\nOperation cancelled by user. Exiting...")
                break

    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error processing show tech file: {e}")
        raise


def process_file(filename: str, parse_type: str, display: bool) -> None:
    """Process a single show tech file"""
    if parse_type == 'both':
        # Parse both interfaces and ACLs
        interface_parser = CiscoInterfaceParser(filename)
        acl_parser = CiscoACLParser(filename)

        print("\n=== Interface Configuration ===")
        interface_parser.save_output(display)

        print("\n=== Access List Configuration ===")
        acl_parser.save_output(display)

    elif parse_type == 'acl':
        config_parser = CiscoACLParser(filename)
        config_parser.save_output(display)

    elif parse_type == 'interface':
        config_parser = CiscoInterfaceParser(filename)
        config_parser.save_output(display)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting...")
        sys.exit(0)