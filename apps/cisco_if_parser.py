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
import sys
from openpyxl import Workbook, load_workbook
from apps.utils import ip_mask_to_cidr # Import the new utility
from logging.handlers import TimedRotatingFileHandler

# Get module logger
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
        self.parsed_data: Dict = {} # To store parsed results
        self.sections: Dict[str, str] = {} # Store extracted sections

        # Check if file has already been parsed
        if show_tech_file in self._section_cache:
            cache = self._section_cache[show_tech_file]
            self.sections = cache['sections'] # Load sections from cache
            self.running_config = self.sections.get('show running-config') or self.sections.get('show running') # Try both keys
            self.device_type = cache['device_type']
            self.hostname = cache['hostname']
            logger.debug(f"Using cached sections for {show_tech_file}")
        else:
            self._extract_sections() # Call the refactored extraction method
            # Populate main attributes after extraction
            self.running_config = self.sections.get('show running-config') or self.sections.get('show running')
            if self.running_config:
                self._extract_hostname_from_running_config()
                self.device_type = self._determine_device_type_from_running_config() # Determine type from running config if possible
            else:
                logger.error("Running config section not found after extraction!")
                # Optionally try determining type from version section if running config missing
                version_section = self.sections.get('show version')
                if version_section:
                    self.device_type = _determine_device_type(version_section) # Use the standalone function with version text
                else:
                    self.device_type = "Unknown" # Fallback if no version or running-config

            # Cache the extracted sections and derived info
            self._section_cache[self.show_tech_file] = {
                'sections': self.sections,
                'device_type': self.device_type,
                'hostname': self.hostname
            }

    def _extract_hostname_from_running_config(self) -> None:
        """Extract hostname specifically from the running-config section."""
        if not self.running_config:
            logger.warning("Cannot extract hostname, running_config is missing.")
            return
        hostname_pattern = re.compile(r'^hostname\s+(\S+)', re.MULTILINE)
        hostname_match = hostname_pattern.search(self.running_config)
        if hostname_match:
            self.hostname = hostname_match.group(1)
            logger.info(f"Found hostname from running-config: {self.hostname}")
        else:
            logger.warning("Could not find hostname in running-config")
            self.hostname = "unknown"

    def _determine_device_type_from_running_config(self) -> str:
        """Attempt to determine device type based on running-config content."""
        if not self.running_config:
            return "Unknown"
        # Simple heuristics based on common config commands
        if "feature nxos-extsdk" in self.running_config or "feature vpc" in self.running_config:
            return "Nexus Switch"
        # Add more heuristics if needed, e.g., based on interface naming, specific commands
        
        # Fallback: Use version section if running-config doesn't give clues
        version_section = self.sections.get('show version')
        if version_section:
            return _determine_device_type(version_section)
        
        return "Unknown Cisco Device" # Default if no specific clues found

    def _extract_sections(self) -> None:
        """Extract sections based on header patterns like '--- show command ---'."""
        self.sections = {}
        found_commands = [] # Log commands found
        try:
            with open(self.show_tech_file, 'r', encoding='ascii', errors='ignore') as f:
                content = f.read()

            # Multiple patterns to find section headers
            header_patterns = [
                # Classic pattern with dashes/stars/equals
                r"^(?:-{5,}|\*{5,}|={5,})\s*(show\s+.*?)\s*(?:-{5,}|\*{5,}|={5,})\s*$",
                # Nexus-style with backticks
                r"^(?:`|')\s*(show\s+.*?)\s*(?:`|')\s*$",
                # Simple show command at start of line
                r"^(show\s+(?:ip\s+)?(?:interface|cdp|trunk).*?)(?:\n|$)",
                # Command with timestamp
                r"^\d{2}:\d{2}:\d{2}.\d{3}\s+(show\s+.*?)(?:\n|$)"
            ]

            # Try each pattern
            for pattern in header_patterns:
                header_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                matches = list(header_pattern.finditer(content))
                logger.debug(f"Found {len(matches)} potential section headers using pattern: {pattern}")

                for i, match in enumerate(matches):
                    # The header line itself is the match
                    header_line_end_pos = match.end()
                    # Content starts *after* the header line
                    content_start_pos = header_line_end_pos + 1 # Skip the newline after header
                    
                    # Command is the 1st capture group, normalize whitespace and case
                    command = " ".join(match.group(1).lower().split())
                    
                    # Skip if we already found this command with a previous pattern
                    if command in self.sections:
                        continue
                        
                    found_commands.append(command) # Add command to list for logging
                    logger.debug(f"Found section header: '{command}' matching line: {match.group(0)}")

                    # Find end of section - look for next header or end of file
                    # First try to find the next header from any pattern
                    next_header_pos = len(content)
                    for next_pattern in header_patterns:
                        next_match = re.compile(next_pattern, re.IGNORECASE | re.MULTILINE).search(content, header_line_end_pos + 1)
                        if next_match and next_match.start() < next_header_pos:
                            next_header_pos = next_match.start()
                    
                    section_content = content[content_start_pos:next_header_pos].strip()
                    if section_content:  # Only store if we found content
                        self.sections[command] = section_content
                        logger.info(f"Extracted section: '{command}' ({len(section_content)} chars)")

            if not self.sections:
                logger.warning(f"No sections extracted using header patterns. File might have unexpected format: {self.show_tech_file}")

        except FileNotFoundError:
            logger.error(f"Show tech file not found: {self.show_tech_file}")
            raise
        except Exception as e:
            logger.error(f"Failed to extract sections from file: {e}", exc_info=True)
            # Don't raise here, allow parsing methods to handle missing sections

        logger.info(f"Finished section extraction. Found commands: {found_commands}") # Log all found commands at the end

    def get_hostname(self):
        """Return the hostname found during parsing."""
        return self.hostname

    def parse_file(self, file_path: Optional[str] = None) -> Dict:
        """
        Placeholder parse method to maintain interface consistency.
        Actual parsing happens during __init__ and specific subclass methods.
        Subclasses should override this to call their specific parsing logic.
        Returns the parsed data.
        """
        # File path argument is ignored here as parsing happens in init
        # Subclasses should implement their specific parsing triggers here if needed
        # For now, just return the data potentially populated by __init__ or subclasses
        # This might need refinement based on how subclasses store results.
        logger.warning("Base CiscoConfigParser.parse_file called. Ensure subclass overrides it correctly.")
        return self.parsed_data


class CiscoACLParser(CiscoConfigParser):
    """Parser for Cisco access-list configurations"""

    def __init__(self, show_tech_file: str):
        """Initialize the ACL parser"""
        super().__init__(show_tech_file)
        self.acls: Dict[str, List[Dict]] = {}
        if self.running_config:
            self._parse_acls() # Parse ACLs during init
            # Flatten ACL data for the exporter
            flat_acl_data = [item for sublist in self.acls.values() for item in sublist]
            self.parsed_data['Access Lists'] = flat_acl_data # Use sheet name as key

    def _parse_acls(self) -> None:
        """Parse access-list configurations"""
        if not self.running_config:
            return

        self.acls = {}  # Reset ACLs dictionary

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

                    # Create entry with default values
                    entry = {
                        'Line': line_number,
                        'Number': acl_id,
                        'Action': parts[2],
                        'Protocol': parts[3] if len(parts) > 3 else '',
                        'Src-IP': '',
                        'Src-Protocol': '',
                        'Dst-IP': '',
                        'Dst-Protocol': '',
                        'Remark': ' | '.join(current_remarks)
                    }

                    # Handle special case of "permit any" or "deny any"
                    if len(parts) == 4 and parts[3] == 'any':
                        entry['Src-IP'] = 'any'
                        entry['Dst-IP'] = 'any'
                        if acl_id not in self.acls:
                            self.acls[acl_id] = []
                        self.acls[acl_id].append(entry)
                        continue

                    # Parse source
                    idx = 4
                    if idx < len(parts):
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

                    if acl_id not in self.acls:
                        self.acls[acl_id] = []
                    self.acls[acl_id].append(entry)

                logger.debug(f"Completed processing access-list {acl_id}")

        except Exception as e:
            logger.error(f"Failed to parse ACL entry: {e}")
            raise

    def parse_file(self, file_path: Optional[str] = None) -> Dict:
        """
        Overrides base parse_file. Returns the parsed ACL data.
        """
        # Parsing is done in __init__, just return the results
        return self.parsed_data


class CiscoInterfaceParser(CiscoConfigParser):
    """Parser for Cisco interface configurations"""

    def __init__(self, show_tech_file: str):
        """Initialize the interface parser"""
        super().__init__(show_tech_file)
        self.interfaces: Dict[str, Dict] = {}
        self.interface_status: Dict[str, Dict] = {}
        self.show_interfaces: Optional[str] = None
        self.show_interfaces_brief: Optional[str] = None
        self.show_interfaces_trunk: Optional[str] = None # For show int trunk output
        self.parsed_trunk_data: Dict[str, Dict] = {} # Store parsed trunk status
        self.show_cdp_neighbor_detail: Optional[str] = None # For CDP output
        self.parsed_cdp_data: List[Dict] = [] # Store parsed CDP data

        # Assign sections to their specific attributes
        self.show_interfaces = self.sections.get('show interfaces')
        self.show_interfaces_brief = self.sections.get('show interface brief') or self.sections.get('show interfaces brief')
        self.show_interfaces_trunk = self.sections.get('show interface trunk') or self.sections.get('show interfaces trunk')
        self.show_cdp_neighbor_detail = self.sections.get('show cdp neighbor detail') or self.sections.get('show cdp neighbors detail')

        if self.running_config:
            self._parse_interfaces()  # Parse interfaces from running config
            self._update_interface_status() # Update status from extracted sections
            self._parse_show_interfaces_trunk() # Parse trunk status data
            self._parse_cdp_neighbor_detail() # Parse CDP data

            # Format interface data for the exporter
            interface_list_data = [
                {
                    "Interface": data["if_name"],
                    "VLAN": data["vlan"],
                    "Type": data["type"],
                    "Mode": data["mode"],
                    "Status": data["status"],
                    "Reason": data["reason"],
                    "Speed": data["speed"],
                    "Port-Channel": data["port_channel"],
                    "Description": data["description"],
                    "IP_CIDR": data["ip_cidr"],
                    "Allowed Trunks": data["allowed_trunks"] # Add Allowed Trunks (from config)
                }
                for data in self.interfaces.values()
            ]
            self.parsed_data['Interfaces'] = interface_list_data # Use sheet name as key

            # Format trunk data for the exporter
            trunk_list_data = []
            for if_name, trunk_data in self.parsed_trunk_data.items():
                # Get description from the main interface data
                description = self.interfaces.get(if_name, {}).get("description", "")
                trunk_list_data.append({
                    "Interface": if_name,
                    "Description": description,
                    "Allowed": trunk_data.get("allowed", ""),
                    "Active": trunk_data.get("active", ""),
                    "Forwarding": trunk_data.get("forwarding", "")
                })
            self.parsed_data['Trunks'] = trunk_list_data # New sheet data

            # Format CDP data for the exporter
            self.parsed_data['CDP'] = self.parsed_cdp_data # Add CDP sheet data

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

                # Determine type early
                interface_type = self._determine_type(normalized_name)

                # Extract port-channel number if this is a port-channel interface
                port_channel_num = ""
                if interface_type == "port-channel":
                    match = re.search(r'port-channel(\d+)', normalized_name, re.IGNORECASE)
                    if match:
                        port_channel_num = match.group(1)
                        logger.debug(f"    Found port-channel number: {port_channel_num}")

                # Initialize interface dictionary using normalized name
                self.interfaces[normalized_name] = {
                    "if_name": normalized_name,
                    "vlan": "",
                    "type": interface_type,
                    "mode": "access",  # Default mode is access
                    "status": "",
                    "reason": "",
                    "speed": "",
                    "port_channel": port_channel_num,  # Set port-channel number if found
                    "description": "",
                    "ip_cidr": "",
                    "allowed_trunks": "" # Initialize allowed_trunks
                }

                # If it's a Vlan or Loopback interface, force mode to routed immediately
                if interface_type in ["vlan", "loopback"]:
                    self.interfaces[normalized_name]["mode"] = "routed"
                    logger.debug(f"    Interface type is {interface_type}, setting mode to routed")

                # Parse interface details
                ip_address = ""
                ip_mask = ""
                for child in interface.children:
                    child_text = child.text.strip()
                    logger.debug(f"  Processing child config: {child_text}")
                    if child_text.startswith("description"):
                        self.interfaces[normalized_name]["description"] = child_text.split("description ", 1)[1]
                        logger.debug(f"    Found description: {self.interfaces[normalized_name]['description']}")
                    elif child_text.startswith("switchport access vlan"):
                        self.interfaces[normalized_name]["vlan"] = child_text.split("switchport access vlan ", 1)[1]
                        self.interfaces[normalized_name]["mode"] = "access"
                        logger.debug(f"    Found access VLAN: {self.interfaces[normalized_name]['vlan']}")
                    elif child_text.startswith("switchport trunk native vlan"):
                        self.interfaces[normalized_name]["vlan"] = child_text.split("switchport trunk native vlan ", 1)[1]
                        self.interfaces[normalized_name]["mode"] = "trunk"
                        logger.debug(f"    Found trunk native VLAN: {self.interfaces[normalized_name]['vlan']}")
                    elif child_text == "switchport mode trunk":
                        self.interfaces[normalized_name]["mode"] = "trunk"
                        logger.debug(f"    Found trunk mode")
                    elif child_text.startswith("switchport trunk allowed vlan"):
                        allowed_vlans = child_text.split("switchport trunk allowed vlan ", 1)[1]
                        # Handle keywords like 'add', 'remove', 'except' - for now, just take the value
                        # More sophisticated parsing might be needed depending on requirements
                        self.interfaces[normalized_name]["allowed_trunks"] = allowed_vlans.split()[0] # Take first part for simplicity
                        logger.debug(f"    Found allowed trunk VLANs: {self.interfaces[normalized_name]['allowed_trunks']}")
                    elif child_text.startswith("channel-group"):
                        port_channel = child_text.split("channel-group ", 1)[1].split(" ")[0]
                        self.interfaces[normalized_name]["port_channel"] = port_channel
                        logger.debug(f"    Found port-channel: {port_channel}")
                    elif child_text == "no switchport":
                        self.interfaces[normalized_name]["mode"] = "routed"
                        logger.debug(f"    Found 'no switchport', setting mode to routed")
                    elif child_text.startswith("ip address"):
                        parts = child_text.split()
                        if len(parts) >= 4:
                            ip_address = parts[2]
                            ip_mask = parts[3]
                            logger.debug(f"    Found IP address: {ip_address}/{ip_mask}")
                        else:
                            logger.warning(f"    Could not parse IP address line: {child_text}")

                # Post-processing for the interface
                # Assign default VLAN 1 if mode is access and no VLAN was explicitly set
                if self.interfaces[normalized_name]["mode"] == "access" and not self.interfaces[normalized_name]["vlan"]:
                    self.interfaces[normalized_name]["vlan"] = "1"
                    logger.debug(f"    Mode is access and no VLAN found, defaulting VLAN to 1")
                # If mode is trunk and no specific allowed VLANs were found, default to 1-4094
                elif self.interfaces[normalized_name]["mode"] == "trunk" and not self.interfaces[normalized_name]["allowed_trunks"]:
                    self.interfaces[normalized_name]["allowed_trunks"] = "1-4094"
                    logger.debug(f"    Mode is trunk and no allowed VLANs found, defaulting to 1-4094")

                # Calculate CIDR if mode is routed and IP/mask were found
                if self.interfaces[normalized_name]["mode"] == "routed" and ip_address and ip_mask:
                    self.interfaces[normalized_name]["ip_cidr"] = ip_mask_to_cidr(ip_address, ip_mask)
                    logger.debug(f"    Mode is routed, calculated CIDR: {self.interfaces[normalized_name]['ip_cidr']}")
                # If mode is not routed, ensure ip_cidr is empty
                elif self.interfaces[normalized_name]["mode"] != "routed":
                    self.interfaces[normalized_name]["ip_cidr"] = ""

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
            str: Interface type (ethernet, vlan, port-channel, or loopback)
        """
        if_name_lower = interface_name.lower()
        if if_name_lower.startswith("vlan"):
            return "vlan"
        elif if_name_lower.startswith("port-channel"):
            return "port-channel"
        elif if_name_lower.startswith(("loopback", "lo")):
            return "loopback"
        else:
            # Assuming ethernet or other physical types otherwise
            return "ethernet"

    def _update_interface_status(self) -> None:
        """Update interface status from show interfaces section"""
        if not self.show_interfaces and not self.show_interfaces_brief:
            logger.debug("Neither show interfaces nor show interfaces brief section found. Cannot update status.")
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
            logger.error(f"Failed to update interface status: {e}", exc_info=True)

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

    def _parse_show_interfaces_trunk(self) -> None:
        """Parse the output of 'show interfaces trunk' command."""
        if not self.show_interfaces_trunk:
            logger.debug("No 'show interfaces trunk' output found to parse.")
            return

        logger.debug("--- Parsing show interfaces trunk --- ")
        self.parsed_trunk_data = {}
        current_section = None
        # Regex to find Port lines and capture the rest of the line
        port_line_re = re.compile(r"^([\w\-/\.]+)\s+(.*)$")

        lines = self.show_interfaces_trunk.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Identify the section based on header keywords
            if "allowed on trunk" in line and "active" not in line:
                current_section = "allowed"
                logger.debug("Entering trunk section: allowed")
                continue
            elif "allowed and active" in line:
                current_section = "active"
                logger.debug("Entering trunk section: active")
                continue
            elif "forwarding state and not pruned" in line:
                current_section = "forwarding"
                logger.debug("Entering trunk section: forwarding")
                continue
            elif line.startswith("Port") or line.startswith("---"):
                # Skip header lines or separators
                continue

            # If we are inside a known section, parse the port data
            if current_section:
                match = port_line_re.match(line)
                if match:
                    port_name = self._normalize_interface_name(match.group(1))
                    vlan_data = match.group(2).strip()
                    logger.debug(f"  Found Port: {port_name}, Section: {current_section}, Data: {vlan_data}")

                    if port_name not in self.parsed_trunk_data:
                        self.parsed_trunk_data[port_name] = {}
                    
                    self.parsed_trunk_data[port_name][current_section] = vlan_data
                else:
                    # Handle potential wrapped lines (simple append strategy)
                    # Find the last processed port if possible
                    last_port = list(self.parsed_trunk_data.keys())[-1] if self.parsed_trunk_data else None
                    if last_port and current_section in self.parsed_trunk_data[last_port]:
                        logger.debug(f"    Appending wrapped line to {last_port}[{current_section}]: {line}")
                        self.parsed_trunk_data[last_port][current_section] += " " + line
                    else:
                        logger.warning(f"Could not associate wrapped line in section '{current_section}': {line}")
       
        logger.debug("--- Finished parsing show interfaces trunk --- ")
        logger.debug(f"Parsed trunk data: {self.parsed_trunk_data}")

    def _parse_cdp_neighbor_detail(self) -> None:
        """Parse the output of 'show cdp neighbor detail' command."""
        if not self.show_cdp_neighbor_detail:
            logger.debug("No 'show cdp neighbor detail' output found to parse.")
            return

        logger.debug("--- Parsing show cdp neighbor detail --- ")
        self.parsed_cdp_data = []
        local_hostname = self.get_hostname() # Get local hostname

        # Split the output into individual neighbor entries
        neighbor_entries = re.split(r'\n-{20,}\n', self.show_cdp_neighbor_detail)

        capability_map = {
            "Router": "R", "Switch": "S", "IGMP": "I", "Host": "H",
            "Trans Bridge": "T", "Source Route Bridge": "B", "Repeater": "r",
            "Phone": "P", "Remote": "D", "CVTA": "C", "Two-port Mac Relay": "M"
            # Add other mappings if necessary
        }

        for entry in neighbor_entries:
            if not entry.strip():
                continue
            
            logger.debug(f"Processing CDP entry:\n{entry[:200]}...") # Log start of entry

            data = {
                "Hostname": local_hostname,
                "Local Interface": "",
                "Platform": "",
                "Remote Hostname": "",
                "Remote Port": "",
                "Remote Mgmt IP": "",
                "Remote Type": "",
                "Capabilities": "",
            }

            # Extract fields using regex
            device_id_match = re.search(r"Device ID:\s*(.*)", entry)
            if device_id_match: data["Remote Hostname"] = device_id_match.group(1).strip()

            interface_match = re.search(r"Interface:\s*([\w\-/\.]+),?\s*Port ID\s*\(outgoing port\):\s*(.*)", entry)
            if interface_match:
                data["Local Interface"] = self._normalize_interface_name(interface_match.group(1).strip())
                data["Remote Port"] = interface_match.group(2).strip()

            platform_cap_match = re.search(r"Platform:\s*(.*?),(?:\s*Capabilities:|$) *Capabilities:\s*(.*)", entry, re.IGNORECASE)
            if platform_cap_match:
                data["Platform"] = platform_cap_match.group(1).strip()
                caps_text = platform_cap_match.group(2).strip()
                # Convert text capabilities to codes
                cap_codes = [capability_map.get(cap.strip(), cap.strip()) for cap in caps_text.split()]
                data["Capabilities"] = " ".join(cap_codes)
            else: # Try finding Platform alone if capabilities are missing/different format
                 platform_match = re.search(r"Platform:\s*(.*?)(?:,|$)", entry, re.IGNORECASE)
                 if platform_match: data["Platform"] = platform_match.group(1).strip()
                 # Try finding Capabilities alone
                 caps_match = re.search(r"Capabilities:\s*(.*)", entry, re.IGNORECASE)
                 if caps_match: 
                     caps_text = caps_match.group(1).strip()
                     cap_codes = [capability_map.get(cap.strip(), cap.strip()) for cap in caps_text.split()]
                     data["Capabilities"] = " ".join(cap_codes)

            mgmt_ip_match = re.search(r"Management address\(es\):.*?IP address:\s*([\d\.]+)", entry, re.DOTALL)
            if mgmt_ip_match: data["Remote Mgmt IP"] = mgmt_ip_match.group(1).strip()
            else: # Fallback to Entry address if mgmt not found
                entry_ip_match = re.search(r"Entry address\(es\):.*?IP address:\s*([\d\.]+)", entry, re.DOTALL)
                if entry_ip_match: data["Remote Mgmt IP"] = entry_ip_match.group(1).strip()

            version_match = re.search(r"Version :\s*\n\s*(.*)", entry)
            if version_match: data["Remote Type"] = version_match.group(1).strip()

            # Only add if we found essential info like Remote Hostname
            if data["Remote Hostname"]:
                 self.parsed_cdp_data.append(data)
                 logger.debug(f"  Added CDP neighbor: {data}")
            else:
                 logger.warning(f"Skipping CDP entry due to missing Device ID: {entry[:100]}...")

        logger.debug("--- Finished parsing show cdp neighbor detail --- ")

    def parse_file(self, file_path: Optional[str] = None) -> Dict:
        """
        Overrides base parse_file. Returns the parsed interface data.
        """
        # Parsing is done in __init__, just return the results
        return self.parsed_data


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

    # Set up logging with debug mode if specified
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

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
                        logger.info(f"\nProcessing {file_info['filename']}...")
                        process_file(file_info['filename'], args.type, args.display)
                else:
                    try:
                        file_id = int(choice)
                        file_info = next((f for f in cisco_files if f['id'] == file_id), None)
                        if file_info:
                            process_file(file_info['filename'], args.type, args.display)
                        else:
                            logger.error(f"Invalid ID: {file_id}")
                    except ValueError:
                        logger.error("Invalid selection")

            except KeyboardInterrupt:
                logger.info("\nOperation cancelled by user. Exiting...")
                break

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error processing show tech file: {e}", exc_info=True)
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