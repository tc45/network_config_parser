# Network Configuration Parser

A Python tool for parsing and analyzing network device configurations from show tech-support outputs. Currently supports Cisco IOS/IOS-XE/NXOS devices, Cisco ASA firewalls, and Palo Alto firewalls. The tool extracts and organizes various configuration elements into easily readable Excel spreadsheets.

## Features

### Cisco IOS/IOS-XE/NXOS Parser
- **Interface Configuration Analysis**
  - Parses interface status, type, and configuration
  - Extracts VLAN assignments and port channels
  - Identifies interface descriptions and IP addresses
  - Shows interface speed and status

- **Access Control List (ACL) Analysis**
  - Extracts all ACL configurations
  - Parses source and destination addresses
  - Shows protocol information and remarks
  - Converts wildcard masks to CIDR notation

- **Trunk Port Analysis**
  - Shows allowed VLANs on trunk ports
  - Displays active and forwarding VLANs
  - Includes trunk port descriptions

- **CDP Neighbor Information**
  - Lists all CDP neighbors
  - Shows platform and capability information
  - Includes management IP addresses
  - Maps local to remote interfaces

### Cisco ASA Parser
- **Interface Configuration**
  - Security levels and VLANs
  - Interface names and descriptions
  - IP addressing and status
  - Redundancy configuration

- **NAT Configuration**
  - Auto and Manual NAT rules
  - Object NAT configurations
  - NAT pools and interfaces
  - Policy NAT conditions

- **Access Group Analysis**
  - Interface bindings
  - Rule direction (in/out)
  - Security policy details

### Palo Alto Parser
- **Interface Configuration**
  - Physical and logical interfaces
  - Security zones
  - Virtual routers
  - Layer 2/3 configurations

- **Security Policy Analysis**
  - Security rules and profiles
  - NAT policies
  - Application filters
  - User identification

- **Object Analysis**
  - Address objects and groups
  - Service objects and groups
  - Application objects
  - Security profiles

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd network_config_parser
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place your show tech-support output files in the `input` directory.

2. Run the appropriate parser:
   ```bash
   # For Cisco IOS/NXOS devices
   python apps/cisco_if_parser.py

   # For Cisco ASA devices
   python apps/asa_parser.py

   # For Palo Alto devices
   python apps/palo_parser.py
   ```

3. Choose parsing options:
   - Parse a single file by entering its ID
   - Parse all files by entering 'all'
   - Quit by entering 'q'

### Command Line Arguments

- `--show-tech FILE`: Process a specific show tech file
- `--display`: Display output in table format instead of saving to Excel
- `--type`: Specify type of configuration to parse (varies by device type)
- `--debug`: Enable debug logging

Example:
```bash
python apps/cisco_if_parser.py --show-tech input/device1.txt --type both
```

## Output

The parser generates Excel files with multiple sheets based on device type:

### Cisco IOS/NXOS Output
1. **Interfaces Sheet**
   - Interface name and description
   - VLAN assignment and mode
   - Status and speed
   - IP addressing (if configured)
   - Port-channel membership

2. **Trunks Sheet**
   - Trunk port details
   - Allowed VLAN ranges
   - Active and forwarding VLANs

3. **CDP Sheet**
   - Neighbor device information
   - Connection details
   - Platform and capability information

4. **Access Lists Sheet**
   - ACL entries and remarks
   - Source and destination details
   - Protocol and port information

### Cisco ASA Output
1. **Interfaces Sheet**
   - Interface configuration and status
   - Security levels and nameif
   - IP addressing and VLANs
   - Redundancy status

2. **NAT Rules Sheet**
   - NAT type and direction
   - Source and destination translations
   - Service translations
   - Associated interfaces

3. **Access Groups Sheet**
   - Rule details and remarks
   - Source and destination
   - Service and protocol information
   - Applied interfaces and direction

### Palo Alto Output
1. **Interfaces Sheet**
   - Interface details and zones
   - IP configuration
   - Virtual router assignment
   - VLAN information

2. **Security Policies Sheet**
   - Rule name and action
   - Source and destination zones
   - Applications and services
   - User and group information

3. **NAT Policies Sheet**
   - NAT rule details
   - Source and destination translation
   - Service translation
   - Zone information

4. **Objects Sheet**
   - Address objects and groups
   - Service objects and groups
   - Application filters
   - Security profiles

## Supported Devices

- Cisco IOS/IOS-XE routers and switches
- Cisco Nexus switches
- Cisco ASA firewalls
- Palo Alto firewalls

## Requirements

See `requirements.txt` for detailed package requirements. Main dependencies include:
- ciscoconfparse2
- openpyxl
- rich
- tabulate
- pandas

## Logging

- Log files are stored in the `logs` directory
- Debug logging can be enabled with the `--debug` flag
- Rich console output provides clear status information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 