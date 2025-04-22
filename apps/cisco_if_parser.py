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
import json

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
        self.show_interfaces = None  # Initialize show interfaces
        self.show_interfaces_brief = None  # Initialize show interfaces brief

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
        logger.info("START - Extracting hostname from configuration")
        if not self.running_config:
            logger.warning("Cannot extract hostname, running_config is missing.")
            logger.info("END - Extracting hostname from configuration (no running config)")
            return
        hostname_pattern = re.compile(r'^hostname\s+(\S+)', re.MULTILINE)
        hostname_match = hostname_pattern.search(self.running_config)
        if hostname_match:
            self.hostname = hostname_match.group(1)
            logger.info(f"Found hostname from running-config: {self.hostname}")
        else:
            logger.warning("Could not find hostname in running-config")
            self.hostname = "unknown"
        logger.info(f"END - Extracting hostname: {self.hostname}")

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
        logger.info("START - Extracting sections from show tech file")
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
                        logger.debug(f"Extracted section: '{command}' ({len(section_content)} chars)")

            if not self.sections:
                logger.warning(f"No sections extracted using header patterns. File might have unexpected format: {self.show_tech_file}")

            # After extracting all sections, populate show interfaces attributes
            self.show_interfaces = self.sections.get('show interfaces')
            self.show_interfaces_brief = self.sections.get('show interfaces brief')
            logger.debug(f"Found show interfaces section: {'Yes' if self.show_interfaces else 'No'}")
            logger.debug(f"Found show interfaces brief section: {'Yes' if self.show_interfaces_brief else 'No'}")

        except FileNotFoundError:
            logger.error(f"Show tech file not found: {self.show_tech_file}")
            raise
        except Exception as e:
            logger.error(f"Failed to extract sections from file: {e}", exc_info=True)
            # Don't raise here, allow parsing methods to handle missing sections

        logger.info(f"Finished section extraction. Found commands: {found_commands}") # Log all found commands at the end
        logger.info("END - Extracting sections from show tech file")

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
    """
    Parser for Cisco Access Control List (ACL) configurations.
    
    This class specializes in parsing and analyzing Cisco ACL configurations from
    show-tech files or running configurations. It can handle both standard and
    extended ACLs, named and numbered ACLs, and provides detailed information
    about ACL entries.
    
    Features:
        - Parses both standard and extended ACLs
        - Handles named and numbered ACLs
        - Extracts source/destination addresses, ports, and protocols
        - Identifies permit/deny actions
        - Supports ACL remarks and descriptions
    
    Attributes:
        acls (Dict[str, List[Dict]]): Parsed ACL data organized by ACL name/number
    
    Example:
        >>> parser = CiscoACLParser("router_config.txt")
        >>> acl_data = parser.parse_file()
        >>> for acl_name, entries in acl_data.items():
        ...     print(f"ACL {acl_name} has {len(entries)} entries")
    
    Notes:
        - ACL parsing happens automatically during initialization
        - Inherits base functionality from CiscoConfigParser
        - Returns empty dict if no ACLs are found
    """

    def __init__(self, show_tech_file: str):
        """
        Initialize the ACL parser.
        
        Args:
            show_tech_file (str): Path to the show-tech or configuration file
                                 containing ACL configurations.
        
        Notes:
            - Calls parent class initialization first
            - Automatically triggers ACL parsing if running config is available
            - Initializes empty acls dictionary for storing parsed results
        """
        super().__init__(show_tech_file)
        self.acls: Dict[str, List[Dict]] = {}
        if self.running_config:
            self._parse_acls()  # Parse ACLs during init
            # Flatten ACL data for the exporter
            flat_acl_data = [item for sublist in self.acls.values() for item in sublist]
            self.parsed_data['Access Lists'] = flat_acl_data # Use sheet name as key

    def _parse_acls(self) -> None:
        """Parse access-list configurations"""
        logger.info("START - Parsing access-list configurations")
        if not self.running_config:
            logger.info("END - Parsing access-list configurations (no running config found)")
            return

        self.acls = {}  # Reset ACLs dictionary
        local_hostname = self.get_hostname()

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
                line_number = 0  # Reset line number for each ACL

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
                        "Host": local_hostname,  # Add hostname as first column
                        "Number": acl_id,        # Move ACL number before Line
                        "Line": line_number,     # Line number now comes after ACL number
                        "Action": parts[2],
                        "Protocol": parts[3] if len(parts) > 3 else '',
                        "Src-IP": '',
                        "Src-Protocol": '',
                        "Dst-IP": '',
                        "Dst-Protocol": '',
                        "Remark": ' | '.join(current_remarks)
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

            logger.info("END - Parsing access-list configurations")

        except Exception as e:
            logger.error(f"Failed to parse ACL entry: {e}")
            logger.info("END - Parsing access-list configurations (with errors)")
            raise

    def parse_file(self, file_path: Optional[str] = None) -> Dict:
        """
        Overrides base parse_file. Returns the parsed ACL data.
        """
        try:
            # Get existing data if any
            existing_data = self.parsed_data.copy() if self.parsed_data else {}
            
            # Add ACL data to existing data
            existing_data['Access Lists'] = [item for sublist in self.acls.values() for item in sublist]
            
            # Update parsed_data with combined data
            self.parsed_data = existing_data
            return self.parsed_data
        except Exception as e:
            logger.error(f"Failed to prepare ACL data for export: {e}")
            return {}


class CiscoInterfaceParser(CiscoConfigParser):
    """
    Parser for Cisco interface configurations and status information.
    
    This class specializes in parsing and analyzing Cisco interface configurations
    from show-tech files or running configurations. It provides comprehensive
    information about interface status, configuration, and connectivity.
    
    Features:
        - Parses interface configurations and running status
        - Extracts IP addresses, VLANs, and descriptions
        - Handles various interface types (Ethernet, Port-channel, VLAN, etc.)
        - Normalizes interface names for consistent formatting
        - Collects CDP neighbor information
        - Analyzes trunk port configurations
    
    The parser processes multiple show commands to build a complete view:
        - show running-config
        - show interfaces
        - show interfaces status
        - show interfaces trunk
        - show cdp neighbors detail
    
    Attributes:
        interfaces (Dict[str, Dict]): Parsed interface data organized by interface name
        trunk_data (List[Dict]): Information about trunk ports
        cdp_neighbors (List[Dict]): CDP neighbor details
    
    Example:
        >>> parser = CiscoInterfaceParser("switch_config.txt")
        >>> interface_data = parser.parse_file()
        >>> for interface in interface_data.get('interfaces', []):
        ...     print(f"{interface['name']}: {interface['status']}")
    
    Notes:
        - Interface parsing happens during initialization
        - Supports both IOS and NXOS interface naming conventions
        - Handles missing or incomplete show command output gracefully
        - Returns data in a format suitable for Excel export
    """

    def __init__(self, show_tech_file: str):
        """
        Initialize the interface parser.
        
        Args:
            show_tech_file (str): Path to the show-tech or configuration file
                                 containing interface configurations and status.
        
        Notes:
            - Calls parent class initialization first
            - Sets up data structures for interfaces, trunks, and CDP
            - Automatically triggers interface parsing if config is available
        """
        super().__init__(show_tech_file)
        self.interfaces: Dict[str, Dict] = {}
        self.trunk_data: List[Dict] = []
        self.cdp_neighbors: List[Dict] = []
        
        # Initialize parsing
        if self.running_config:
            self._parse_interfaces()  # Parse interfaces during init
            
        # Parse trunk information if available
        if 'show interfaces trunk' in self.sections:
            self.show_interfaces_trunk = self.sections['show interfaces trunk']
            self._parse_show_interfaces_trunk()
            
        # Parse CDP information if available
        if 'show cdp neighbor detail' in self.sections:  # Fixed section name
            logger.debug("Found CDP neighbor detail section")
            self.show_cdp_neighbor_detail = self.sections['show cdp neighbor detail']
            self._parse_cdp_neighbor_detail()
        else:
            logger.debug("No CDP neighbor detail section found in sections: " + ", ".join(self.sections.keys()))

    def _normalize_interface_name(self, if_name: str) -> str:
        """
        Normalize interface names to a consistent format.
        
        This method standardizes interface names by expanding common abbreviations
        and ensuring consistent capitalization. It handles various Cisco interface
        naming conventions across different platforms.
        
        Args:
            if_name (str): Raw interface name from configuration
                          (e.g., 'Gi0/1', 'Te1/1', 'Po1')
        
        Returns:
            str: Normalized interface name (e.g., 'GigabitEthernet0/1',
                'TenGigabitEthernet1/1', 'Port-channel1')
        
        Examples:
            >>> parser._normalize_interface_name('Gi0/1')
            'GigabitEthernet0/1'
            >>> parser._normalize_interface_name('Te1/1')
            'TenGigabitEthernet1/1'
        
        Notes:
            - Case-sensitive replacement
            - Handles both IOS and NXOS naming conventions
            - Preserves interface numbers and subinterfaces
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

    def _get_truncated_interface_name(self, if_name: str) -> str:
        """Convert full interface name to truncated version for trunk matching."""
        if_name_lower = if_name.lower()
        
        # Handle port-channels - convert both Po and port-channel formats to Po format
        if if_name_lower.startswith('port-channel'):
            return f"Po{if_name_lower.replace('port-channel', '')}"
        elif if_name_lower.startswith('po'):
            return if_name  # Keep Po format as is
        
        # Map of full names to their truncated versions
        name_map = {
            'tengigabitethernet': 'Te',
            'gigabitethernet': 'Gi',
            'fastethernet': 'Fa',
            'ethernet': 'Et'
        }
        
        for full_name, short_name in name_map.items():
            if if_name_lower.startswith(full_name):
                # Extract the interface number and append to truncated name
                number_part = if_name[len(full_name):]
                return f"{short_name}{number_part}"
        
        return if_name  # Return original if no mapping found

    def _get_column_positions(self, header_line: str, section_type: str) -> Dict[str, tuple]:
        """
        Parse column positions from show command output headers.
        
        This method analyzes the header line from various show commands to determine
        the start and end positions of each column. This is crucial for correctly
        parsing fixed-width output formats commonly used in Cisco CLI.
        
        Args:
            header_line (str): The header line containing column names
            section_type (str): Type of show command output being parsed
                              (e.g., 'status', 'brief')
        
        Returns:
            Dict[str, tuple]: Dictionary mapping column names to their positions:
                            {'column_name': (start_pos, end_pos)}
        
        Example:
            Header line: "Port      Name  Status  Vlan  Duplex Speed Type"
            Returns: {
                'Port': (0, 8),
                'Name': (8, 14),
                'Status': (14, 22),
                ...
            }
        
        Notes:
            - Handles variable width columns
            - Accounts for spaces in column names
            - Different parsing logic for different show command types
            - Returns empty dict if header line is invalid
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
        Parse a single line from show interface output using column positions.
        
        This method extracts interface information from a line of show command
        output using the pre-determined column positions. It handles the
        fixed-width format of Cisco CLI output.
        
        Args:
            line (str): A single line from show interface output
            columns (Dict[str, tuple]): Column position mapping from _get_column_positions
        
        Returns:
            Dict[str, str]: Parsed values for each column:
                          {'column_name': 'value', ...}
        
        Example:
            Line: "Gi0/1     uplink    up      1    auto  auto  10/100BaseTX"
            Returns: {
                'interface': 'Gi0/1',
                'name': 'uplink',
                'status': 'up',
                'vlan': '1',
                ...
            }
        
        Notes:
            - Strips whitespace from extracted values
            - Handles missing or truncated values
            - Returns empty strings for values that don't exist
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
        logger.info("START - Parsing interface configurations")
        if not self.running_config:
            logger.info("END - Parsing interface configurations (no running config found)")
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
                    "Host": self.get_hostname(),  # Add hostname as first column
                    "if_name": normalized_name,
                    "type": interface_type,
                    "mode": "access",  # Default mode is access
                    "vlan": "",
                    "allowed_trunks": "", # Initialize allowed_trunks
                    "admin_state": "",
                    "protocol_status": "",
                    "speed": "",
                    "duplex": "",
                    "media_type": "",
                    "link_type": "",
                    "flow_control_in": "",
                    "flow_control_out": "",
                    "port_channel": port_channel_num,  # Set port-channel number if found
                    "description": "",
                    "ip_cidr": "",
                    "hardware_type": "",
                    "mac_address": "",
                    "bia_address": "",  # Burned In Address
                    "mtu": "",
                    "bandwidth": "",
                    "delay": "",
                    "reliability": "",
                    "txload": "",
                    "rxload": "",
                    "encapsulation": "",
                    "arp_timeout": "",
                    "last_input": "",
                    "last_output": "",
                    "last_output_hang": "",
                    "queue_strategy": "",
                    "input_rate (bps)": "",
                    "output_rate (bps)": "",
                    "input_packets": "",
                    "input_bytes": "",
                    "output_packets": "",
                    "output_bytes": "",
                    "input_errors": "",
                    "output_errors": "",
                    "crc_errors": "",
                    "frame_errors": "",
                    "overrun_errors": "",
                    "unknown_protocols": "",
                    "broadcasts_received": "",
                    "multicasts_received": "",
                    "input_drops": "",
                    "output_drops": "",
                    "interface_resets": "",
                    "carrier_transitions": ""
                }

                # If it's a Vlan or Loopback interface, force mode to routed immediately
                if interface_type in ["vlan", "loopback"]:
                    self.interfaces[normalized_name]["mode"] = "routed"
                    # Extract and set VLAN number for VLAN interfaces
                    if interface_type == "vlan":
                        vlan_match = re.search(r'vlan(\d+)', normalized_name, re.IGNORECASE)
                        if vlan_match:
                            self.interfaces[normalized_name]["vlan"] = vlan_match.group(1)
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
            logger.info("END - Parsing interface configurations")

        except Exception as e:
            logger.error(f"Failed to parse interfaces: {e}")
            logger.info("END - Parsing interface configurations (with errors)")
            raise

    def _determine_type(self, interface_name: str) -> str:
        """
        Determine the interface type from its name.
        
        This method analyzes the interface name to determine its type based on
        Cisco's interface naming conventions. It supports all common Cisco
        interface types across IOS and NXOS platforms.
        
        Args:
            interface_name (str): Normalized interface name
                                (e.g., 'GigabitEthernet0/1', 'Vlan100')
        
        Returns:
            str: Interface type category:
                - 'Physical': For physical interfaces (Ethernet, Fiber, etc.)
                - 'Port-channel': For link aggregation interfaces
                - 'VLAN': For VLAN interfaces
                - 'Tunnel': For tunnel interfaces
                - 'Loopback': For loopback interfaces
                - 'Other': For other interface types
        
        Examples:
            >>> parser._determine_type('GigabitEthernet0/1')
            'Physical'
            >>> parser._determine_type('Port-channel1')
            'Port-channel'
        
        Notes:
            - Case-insensitive matching
            - Returns 'Other' for unrecognized interface types
            - Handles both full names and abbreviated forms
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
        logger.info("START - Updating interface status information")
        if not self.show_interfaces and not self.show_interfaces_brief:
            logger.debug("Neither show interfaces nor show interfaces brief section found. Cannot update status.")
            logger.info("END - Updating interface status information (no status sections found)")
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
                                    "protocol_status": parsed_data['status']
                                }

                                # Add fields based on section type
                                if current_section in ['ethernet', 'portchannel']:
                                    update_data.update({
                                        "vlan": parsed_data['vlan'],
                                        "speed": parsed_data['speed'].split('(')[0].strip(),  # Remove (D) suffix
                                    })
                                    if 'port_ch' in parsed_data:
                                        if parsed_data['port_ch'] != '--':
                                            update_data["port_channel"] = parsed_data['port_ch']

                                self.interfaces[if_name].update(update_data)
                            else:
                                logger.debug(f"Interface {if_name} not found in running-config")

            # Parse detailed interface information from show interfaces
            if hasattr(self, 'show_interfaces'):
                interface_sections = re.split(r'\n(?=\S+? is)', self.show_interfaces)
                for section in interface_sections:
                    if not section.strip():
                        continue

                    # Extract interface name and basic status
                    name_match = re.match(r'(\S+?) is (.*?), line protocol is (\S+)', section)
                    if not name_match:
                        continue

                    if_name = self._normalize_interface_name(name_match.group(1))
                    if if_name not in self.interfaces:
                        continue

                    # Update admin and protocol status
                    self.interfaces[if_name]["admin_state"] = name_match.group(2)
                    self.interfaces[if_name]["protocol_status"] = name_match.group(3)

                    # Extract hardware type and MAC addresses
                    hw_match = re.search(r'Hardware is (.*?), address is (\S+)(?:\s+\(bia (\S+)\))?', section)
                    if hw_match:
                        self.interfaces[if_name]["hardware_type"] = hw_match.group(1)
                        self.interfaces[if_name]["mac_address"] = hw_match.group(2)
                        if hw_match.group(3):
                            self.interfaces[if_name]["bia_address"] = hw_match.group(3)

                    # Extract duplex, speed, link type and media type
                    link_info_match = re.search(r'((?:Auto|Full|Half)-duplex), (\d+(?:\.\d+)?[MG]b/s)(?:, link type is ([\w-]+))?,?\s*(?:media type is ((?:[\w-]+(?:/[\w-]+)*)+(?:\s+[\w-]+)*(?:\s+SFP)?))(?:\s*$|\n)', section)
                    if link_info_match:
                        self.interfaces[if_name]["duplex"] = link_info_match.group(1)
                        self.interfaces[if_name]["speed"] = link_info_match.group(2)
                        if link_info_match.group(3):
                            self.interfaces[if_name]["link_type"] = link_info_match.group(3)
                        if link_info_match.group(4):
                            self.interfaces[if_name]["media_type"] = link_info_match.group(4).strip()

                    # Extract flow control information
                    flow_control_match = re.search(r'input flow-control is (\w+), output flow-control is (\w+)', section)
                    if flow_control_match:
                        self.interfaces[if_name]["flow_control_in"] = flow_control_match.group(1)
                        self.interfaces[if_name]["flow_control_out"] = flow_control_match.group(2)

                    # Extract MTU, BW, DLY
                    mtu_match = re.search(r'MTU (\d+) bytes, BW (\d+) Kbit/sec, DLY (\d+) usec', section)
                    if mtu_match:
                        self.interfaces[if_name]["mtu"] = mtu_match.group(1)
                        self.interfaces[if_name]["bandwidth"] = mtu_match.group(2)
                        self.interfaces[if_name]["delay"] = mtu_match.group(3)

                    # Extract reliability and load
                    load_match = re.search(r'reliability (\d+)/\d+, txload (\d+)/\d+, rxload (\d+)/\d+', section)
                    if load_match:
                        self.interfaces[if_name]["reliability"] = load_match.group(1)
                        self.interfaces[if_name]["txload"] = load_match.group(2)
                        self.interfaces[if_name]["rxload"] = load_match.group(3)

                    # Extract input/output rates
                    rate_match = re.search(r'(\d+) minute input rate (\d+) bits/sec.*?(\d+) minute output rate (\d+) bits/sec', section, re.DOTALL)
                    if rate_match:
                        self.interfaces[if_name]["input_rate (bps)"] = rate_match.group(2)
                        self.interfaces[if_name]["output_rate (bps)"] = rate_match.group(4)

                    # Extract packet statistics
                    packets_match = re.search(r'(\d+) packets input,\s*(\d+) bytes.*?(\d+) packets output,\s*(\d+) bytes', section, re.DOTALL)
                    if packets_match:
                        self.interfaces[if_name]["input_packets"] = packets_match.group(1)
                        self.interfaces[if_name]["input_bytes"] = packets_match.group(2)
                        self.interfaces[if_name]["output_packets"] = packets_match.group(3)
                        self.interfaces[if_name]["output_bytes"] = packets_match.group(4)

                    # Extract error statistics
                    input_errors_match = re.search(r'(\d+) input errors,\s*(\d+) CRC,\s*(\d+) frame,\s*(\d+) overrun', section)
                    if input_errors_match:
                        self.interfaces[if_name]["input_errors"] = input_errors_match.group(1)
                        self.interfaces[if_name]["crc_errors"] = input_errors_match.group(2)
                        self.interfaces[if_name]["frame_errors"] = input_errors_match.group(3)
                        self.interfaces[if_name]["overrun_errors"] = input_errors_match.group(4)

                    # Extract output errors
                    output_errors_match = re.search(r'(\d+) output errors', section)
                    if output_errors_match:
                        self.interfaces[if_name]["output_errors"] = output_errors_match.group(1)

                    # Extract broadcast/multicast information
                    broadcast_match = re.search(r'Received (\d+) broadcasts \((\d+) multicasts\)', section)
                    if broadcast_match:
                        self.interfaces[if_name]["broadcasts_received"] = broadcast_match.group(1)
                        self.interfaces[if_name]["multicasts_received"] = broadcast_match.group(2)

                    # Extract queue drops
                    queue_match = re.search(r'Input queue: (\d+)/\d+/(\d+)/\d+ \(size/max/drops/flushes\); Total output drops: (\d+)', section)
                    if queue_match:
                        self.interfaces[if_name]["input_drops"] = queue_match.group(2)
                        self.interfaces[if_name]["output_drops"] = queue_match.group(3)

                    # Extract interface resets and carrier transitions
                    resets_match = re.search(r'(\d+) interface resets', section)
                    if resets_match:
                        self.interfaces[if_name]["interface_resets"] = resets_match.group(1)

                    carrier_match = re.search(r'(\d+) lost carrier, (\d+) no carrier', section)
                    if carrier_match:
                        total_transitions = int(carrier_match.group(1)) + int(carrier_match.group(2))
                        self.interfaces[if_name]["carrier_transitions"] = str(total_transitions)

                    # Extract encapsulation
                    encap_match = re.search(r'Encapsulation (\w+)', section)
                    if encap_match:
                        self.interfaces[if_name]["encapsulation"] = encap_match.group(1)

                    # Extract ARP timeout
                    arp_match = re.search(r'ARP Timeout (\d{2}:\d{2}:\d{2})', section)
                    if arp_match:
                        self.interfaces[if_name]["arp_timeout"] = arp_match.group(1)

                    # Extract last input/output times
                    last_io_match = re.search(r'Last input ([\w\d:]+), output ([\w\d:]+), output hang ([\w\d:]+)', section)
                    if last_io_match:
                        self.interfaces[if_name]["last_input"] = last_io_match.group(1)
                        self.interfaces[if_name]["last_output"] = last_io_match.group(2)
                        self.interfaces[if_name]["last_output_hang"] = last_io_match.group(3)

                    # Extract queueing strategy
                    queue_match = re.search(r'Queueing strategy: (\w+)', section)
                    if queue_match:
                        self.interfaces[if_name]["queue_strategy"] = queue_match.group(1)

            logger.info("END - Updating interface status information")

        except Exception as e:
            logger.error(f"Failed to update interface status: {e}", exc_info=True)
            logger.info("END - Updating interface status information (with errors)")

    def _parse_show_interfaces_trunk(self) -> None:
        """Parse 'show interfaces trunk' output."""
        trunk_data = {}
        current_section = None
        current_interface = None

        # Initialize patterns
        interface_pattern = re.compile(r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)')
        vlan_pattern = re.compile(r'^(\S+)\s+(.+)$')

        for line in self.show_interfaces_trunk.splitlines():
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue

            # Detect section headers
            if 'Port' in line and 'Mode' in line:
                current_section = 'ports'
                continue
            elif 'Vlans allowed on trunk' in line:
                current_section = 'allowed'
                continue
            elif 'Vlans allowed and active in management domain' in line:
                current_section = 'active'
                continue
            elif 'Vlans in spanning tree forwarding state' in line:
                current_section = 'forwarding'
                continue

            # Process data based on current section
            if current_section == 'ports':
                match = interface_pattern.match(line)
                if match:
                    current_interface = match.group(1)
                    trunk_data[current_interface] = {
                        'mode': match.group(2),
                        'encapsulation': match.group(3),
                        'status': match.group(4),
                        'native_vlan': match.group(5),
                        'allowed_vlans': [],
                        'active_vlans': [],
                        'forwarding_vlans': []
                    }
            elif current_section in ['allowed', 'active', 'forwarding'] and current_interface:
                match = vlan_pattern.match(line)
                if match:
                    # Skip the interface name column if present
                    vlan_list = match.group(2) if match.group(1) == current_interface else match.group(1)
                    # Convert VLAN ranges to list of VLANs
                    vlans = self._expand_vlan_range(vlan_list)
                    
                    if current_section == 'allowed':
                        trunk_data[current_interface]['allowed_vlans'] = vlans
                    elif current_section == 'active':
                        trunk_data[current_interface]['active_vlans'] = vlans
                    elif current_section == 'forwarding':
                        trunk_data[current_interface]['forwarding_vlans'] = vlans

        # Log the final trunk data for debugging
        logger.debug(f"Parsed trunk data: {json.dumps(trunk_data, indent=2)}")
        self.trunk_data = trunk_data

    def _expand_vlan_range(self, vlan_str: str) -> List[int]:
        """Convert a VLAN range string to a list of individual VLAN numbers."""
        vlans = []
        for part in vlan_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                vlans.extend(range(start, end + 1))
            else:
                try:
                    vlans.append(int(part))
                except ValueError:
                    logger.warning(f"Invalid VLAN number: {part}")
                    continue
        return sorted(list(set(vlans)))  # Remove duplicates and sort

    def _parse_cdp_neighbor_detail(self) -> None:
        """Parse the output of 'show cdp neighbor detail' command."""
        logger.info("START - Parsing CDP neighbor information")
        if not self.show_cdp_neighbor_detail:
            logger.debug("No 'show cdp neighbor detail' output found to parse.")
            logger.info("END - Parsing CDP neighbor information (no CDP data found)")
            return

        logger.debug("=== Starting CDP Parsing ===")
        logger.debug("Raw CDP section content (first 500 chars):\n" + self.show_cdp_neighbor_detail[:500] + "...")
        self.cdp_neighbors = []
        local_hostname = self.get_hostname()
        logger.debug(f"Local hostname: {local_hostname}")

        try:
            # Split the output into individual neighbor entries
            neighbor_entries = re.split(r'\n(?=-{3,}|\s*Device ID:)', self.show_cdp_neighbor_detail)
            logger.debug(f"Found {len(neighbor_entries)} potential CDP entries")
            logger.debug("First entry preview (first 200 chars):\n" + neighbor_entries[0][:200] + "...")
            if len(neighbor_entries) > 1:
                logger.debug("Second entry preview (first 200 chars):\n" + neighbor_entries[1][:200] + "...")
        except Exception as e:
            logger.error(f"Failed to split CDP entries: {str(e)}")
            return

        # Map for converting capability text to codes
        capability_map = {
            "Router": "R", "Switch": "S", "IGMP": "I", "Host": "H",
            "Trans-Bridge": "T", "Source-Route-Bridge": "B", "Bridge": "B",
            "Phone": "P", "Remote": "D", "CVTA": "C", "Two-port-Mac-Relay": "M",
            "Trans Bridge": "T", "Source Route Bridge": "B", "Two-port Mac Relay": "M"
        }

        for i, entry in enumerate(neighbor_entries, 1):
            if not entry.strip():
                logger.debug(f"Skipping empty entry {i}")
                continue

            logger.debug(f"\n=== Processing CDP Entry {i} ===")
            logger.debug(f"Entry content preview:\n{entry[:300]}...")

            try:
                # Initialize data dictionary for this neighbor
                data = {
                    "Host": local_hostname,
                    "Local Interface": "",
                    "Remote Hostname": "",
                    "Remote Port": "",
                    "Remote IP": "",
                    "Platform": "",
                    "Capabilities": "",
                    "Remote Version": ""
                }

                # Extract Device ID (Remote Hostname)
                device_id_pattern = r"(?:Device ID:|Device ID\s*:\s*)(.*?)(?:\(|\n|$)"
                device_id_match = re.search(device_id_pattern, entry, re.IGNORECASE | re.MULTILINE)
                if device_id_match:
                    data["Remote Hostname"] = device_id_match.group(1).strip()
                    logger.debug(f"Found Device ID: '{data['Remote Hostname']}'")
                else:
                    logger.debug(f"No Device ID match found. Pattern: {device_id_pattern}")
                    logger.debug("Entry section:\n" + entry[:200])

                # Extract Interface and Port ID
                interface_pattern = r"Interface:\s*([\w\-/\.]+)[,\s]*Port ID \(outgoing port\):\s*(.*?)(?:\n|$)"
                interface_match = re.search(interface_pattern, entry, re.IGNORECASE | re.MULTILINE)
                if interface_match:
                    data["Local Interface"] = self._normalize_interface_name(interface_match.group(1).strip())
                    data["Remote Port"] = interface_match.group(2).strip()
                    logger.debug(f"Found Interface: '{data['Local Interface']}', Port: '{data['Remote Port']}'")
                else:
                    logger.debug(f"No Interface match found. Pattern: {interface_pattern}")
                    logger.debug("Entry section:\n" + entry[:200])

                # Extract Platform
                platform_pattern = r"Platform:\s*(.*?)(?:,|\n|$)"
                platform_match = re.search(platform_pattern, entry, re.IGNORECASE | re.MULTILINE)
                if platform_match:
                    data["Platform"] = platform_match.group(1).strip()
                    logger.debug(f"Found Platform: '{data['Platform']}'")
                else:
                    logger.debug(f"No Platform match found. Pattern: {platform_pattern}")

                # Extract Capabilities
                caps_pattern = r"Capabilities:\s*(.*?)(?:\n|$)"
                caps_match = re.search(caps_pattern, entry, re.IGNORECASE | re.MULTILINE)
                if caps_match: 
                    caps_text = caps_match.group(1).strip()
                    cap_codes = []
                    logger.debug(f"Found capabilities text: '{caps_text}'")
                    for cap in caps_text.split():
                        cap = cap.strip(' ,')
                        if cap in capability_map:
                            cap_codes.append(capability_map[cap])
                            logger.debug(f"Mapped capability '{cap}' to '{capability_map[cap]}'")
                        else:
                            logger.debug(f"No mapping found for capability: '{cap}'")
                    data["Capabilities"] = "".join(sorted(set(cap_codes)))
                    logger.debug(f"Final capabilities string: '{data['Capabilities']}'")
                else:
                    logger.debug(f"No Capabilities match found. Pattern: {caps_pattern}")

                # Extract IP Address
                ip_pattern = r"(?:Management address|IP address|IPv4 address):\s*([\d\.]+)"
                ip_match = re.search(ip_pattern, entry, re.IGNORECASE | re.MULTILINE)
                if ip_match:
                    data["Remote IP"] = ip_match.group(1).strip()
                    logger.debug(f"Found IP: '{data['Remote IP']}'")
                else:
                    logger.debug(f"No IP match found. Pattern: {ip_pattern}")

                # Extract Software Version
                version_pattern = r"(?:Software Version|Version|Cisco IOS Software).*?[\r\n]+\s*(.*?)(?:\n\n|\n(?=[A-Z])|advertisement|Configuration|Copyright|\Z)"
                version_match = re.search(version_pattern, entry, re.DOTALL | re.IGNORECASE)
                if version_match:
                    version = re.sub(r'\s+', ' ', version_match.group(1).strip())
                    data["Remote Version"] = version
                    logger.debug(f"Found Version: '{version[:100]}...'")
                else:
                    logger.debug(f"No Version match found. Pattern: {version_pattern}")

                # Validate entry
                if data["Remote Hostname"] and data["Local Interface"]:
                    self.cdp_neighbors.append(data)
                    logger.debug(f"Successfully added CDP neighbor: {data['Local Interface']} -> {data['Remote Hostname']}")
                else:
                    logger.warning(
                        f"Skipping CDP entry {i} due to missing essential information:\n"
                        f"Remote Hostname='{data['Remote Hostname']}'\n"
                        f"Local Interface='{data['Local Interface']}'"
                    )

            except Exception as e:
                logger.error(f"Error processing CDP entry {i}: {str(e)}")
                logger.debug("Problematic entry content:\n" + entry)
                continue

        logger.debug("\n=== Final CDP Processing Results ===")
        logger.debug(f"Total entries processed: {len(neighbor_entries)}")
        logger.debug(f"Successfully parsed neighbors: {len(self.cdp_neighbors)}")
        if self.cdp_neighbors:
            logger.debug("Parsed CDP neighbors:")
            for neighbor in self.cdp_neighbors:
                logger.debug(
                    f"  {neighbor['Local Interface']} -> {neighbor['Remote Hostname']}\n"
                    f"    IP: {neighbor['Remote IP']}\n"
                    f"    Platform: {neighbor['Platform']}\n"
                    f"    Capabilities: {neighbor['Capabilities']}"
                )
        else:
            logger.warning("No CDP neighbors were successfully parsed!")

        logger.info(f"END - Parsing CDP neighbor information (found {len(self.cdp_neighbors)} neighbors)")

    def parse_file(self, file_path: Optional[str] = None) -> Dict:
        """Parse interface configuration and status information."""
        try:
            logger.info("START - Preparing interface data for export")
            # Convert interfaces dictionary to list for Excel export
            interface_list = []
            for interface in self.interfaces.values():
                interface_list.append(interface)
            
            # Prepare the data dictionary with all sections
            self.parsed_data = {
                'Interfaces': interface_list,
                'Trunks': self.trunk_data if hasattr(self, 'trunk_data') else [],
                'CDP': self.cdp_neighbors if hasattr(self, 'cdp_neighbors') else []
            }
            
            logger.info("END - Preparing interface data for export")
            return self.parsed_data
        except Exception as e:
            logger.error(f"Failed to prepare interface data for export: {e}")
            logger.info("END - Preparing interface data for export (with errors)")
            return {}


def _determine_device_type(content: str) -> str:
    """Determine device type by examining show version output"""
    logger.info("START - Determining device type")
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
        device_type = "Nexus Switch"
    elif re.search(r'IOS-XE.*Catalyst|Catalyst.*IOS-XE', version_text, re.IGNORECASE):
        device_type = "Catalyst Switch"
    elif re.search(r'IOS-XE', version_text, re.IGNORECASE):
        device_type = "IOS-XE Router"
    elif re.search(r'IOS Software', version_text, re.IGNORECASE):
        device_type = "IOS Router"
    else:
        device_type = "Unknown Cisco Device"

    logger.info(f"END - Determining device type: {device_type}")
    return device_type


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
    try:
        logger.info(f"START - Processing file: {filename}")
        if parse_type == 'both':
            # Parse interfaces first
            interface_parser = CiscoInterfaceParser(filename)
            interface_data = interface_parser.parse_file()
            
            # Parse ACLs and combine with interface data
            acl_parser = CiscoACLParser(filename)
            acl_data = acl_parser.parse_file()
            
            # Combine the data
            combined_data = interface_data.copy()
            combined_data.update(acl_data)
            
            # Update the parsed_data in interface_parser
            interface_parser.parsed_data = combined_data
            
            print("\n=== Combined Configuration ===")
            interface_parser.save_output(display)

        elif parse_type == 'acl':
            config_parser = CiscoACLParser(filename)
            config_parser.parse_file()  # Make sure to parse before saving
            config_parser.save_output(display)

        elif parse_type == 'interface':
            config_parser = CiscoInterfaceParser(filename)
            config_parser.parse_file()  # Make sure to parse before saving
            config_parser.save_output(display)
            
        logger.info(f"END - Processing file: {filename}")
    except Exception as e:
        logger.error(f"Failed to process {filename}: {e}", exc_info=True)
        logger.info(f"END - Processing file: {filename} (with errors)")
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting...")
        sys.exit(0)