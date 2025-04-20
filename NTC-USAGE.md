# NTC Templates Usage Guide

## Overview
This guide demonstrates how to use NTC Templates to parse Cisco IOS and ASA device outputs in Python applications. NTC Templates provides a consistent way to parse CLI output into structured data without writing custom regex patterns.

## Installation

```bash
pip install ntc-templates
```

## Basic Usage

```python
from ntc_templates.parse import parse_output

def parse_device_output(platform, command, output_text):
    """
    Generic function to parse any supported command output.
    
    Args:
        platform (str): Device platform ('cisco_ios' or 'cisco_asa')
        command (str): The exact command that generated the output
        output_text (str): The command output text to parse
        
    Returns:
        list: List of dictionaries containing parsed data
    """
    try:
        parsed_output = parse_output(
            platform=platform,
            command=command,
            data=output_text
        )
        return parsed_output
    except Exception as e:
        print(f"Error parsing {command} output: {str(e)}")
        return None
```

## Supported Commands

### Cisco IOS Common Commands

```python
# Dictionary of common Cisco IOS commands and their parsing examples
IOS_COMMANDS = {
    'show interfaces': {
        'platform': 'cisco_ios',
        'example_fields': [
            'interface', 'link_status', 'protocol_status', 
            'hardware_type', 'address', 'mtu', 'duplex', 
            'speed', 'bandwidth'
        ]
    },
    'show ip interface brief': {
        'platform': 'cisco_ios',
        'example_fields': [
            'interface', 'ip_address', 'status', 
            'protocol'
        ]
    },
    'show cdp neighbors': {
        'platform': 'cisco_ios',
        'example_fields': [
            'destination_host', 'local_interface', 
            'capability', 'platform', 'neighbor_interface'
        ]
    },
    'show version': {
        'platform': 'cisco_ios',
        'example_fields': [
            'version', 'rommon', 'hostname', 'uptime',
            'running_image', 'hardware'
        ]
    },
    'show ip route': {
        'platform': 'cisco_ios',
        'example_fields': [
            'protocol', 'network', 'mask', 'distance',
            'metric', 'nexthop_ip', 'nexthop_if'
        ]
    },
    'show access-lists': {
        'platform': 'cisco_ios',
        'example_fields': [
            'acl_name', 'acl_type', 'ace_action',
            'ace_source', 'ace_destination', 'ace_protocol'
        ]
    }
}

### Cisco ASA Common Commands

```python
# Dictionary of common Cisco ASA commands and their parsing examples
ASA_COMMANDS = {
    'show interface': {
        'platform': 'cisco_asa',
        'example_fields': [
            'interface', 'link_status', 'protocol_status',
            'hardware_type', 'address', 'mtu', 'duplex',
            'speed', 'bandwidth'
        ]
    },
    'show version': {
        'platform': 'cisco_asa',
        'example_fields': [
            'version', 'device_mgr_version', 'compile_date',
            'hostname', 'uptime', 'hardware'
        ]
    },
    'show access-list': {
        'platform': 'cisco_asa',
        'example_fields': [
            'acl_name', 'line_num', 'permit_deny',
            'source_network', 'destination_network',
            'protocol', 'hits'
        ]
    },
    'show nameif': {
        'platform': 'cisco_asa',
        'example_fields': [
            'interface', 'nameif', 'security_level'
        ]
    }
}
```

## Example Usage Scenarios

### 1. Parsing Interface Information

```python
def get_interface_details(device_output, platform='cisco_ios'):
    """
    Parse interface details from 'show interfaces' output.
    
    Args:
        device_output (str): The output from 'show interfaces' command
        platform (str): Device platform ('cisco_ios' or 'cisco_asa')
        
    Returns:
        list: List of dictionaries containing interface details
    """
    parsed_data = parse_device_output(
        platform=platform,
        command='show interfaces',
        output_text=device_output
    )
    
    # Example of processing the parsed data
    interface_stats = []
    for interface in parsed_data:
        stats = {
            'name': interface['interface'],
            'status': interface['link_status'],
            'protocol': interface['protocol_status'],
            'bandwidth': interface.get('bandwidth', 'N/A'),
            'mtu': interface.get('mtu', 'N/A')
        }
        interface_stats.append(stats)
    
    return interface_stats
```

### 2. Analyzing ACLs

```python
def analyze_acls(acl_output, platform='cisco_ios'):
    """
    Parse and analyze access control lists.
    
    Args:
        acl_output (str): The output from 'show access-lists' command
        platform (str): Device platform ('cisco_ios' or 'cisco_asa')
        
    Returns:
        dict: Dictionary containing ACL analysis
    """
    command = 'show access-lists' if platform == 'cisco_ios' else 'show access-list'
    parsed_data = parse_device_output(
        platform=platform,
        command=command,
        output_text=acl_output
    )
    
    acl_analysis = {
        'total_acls': len(set(acl['acl_name'] for acl in parsed_data)),
        'acls': {}
    }
    
    for ace in parsed_data:
        acl_name = ace['acl_name']
        if acl_name not in acl_analysis['acls']:
            acl_analysis['acls'][acl_name] = {
                'permit_count': 0,
                'deny_count': 0,
                'entries': []
            }
        
        action = ace.get('permit_deny', ace.get('ace_action', '')).lower()
        if 'permit' in action:
            acl_analysis['acls'][acl_name]['permit_count'] += 1
        elif 'deny' in action:
            acl_analysis['acls'][acl_name]['deny_count'] += 1
            
        acl_analysis['acls'][acl_name]['entries'].append(ace)
    
    return acl_analysis
```

### 3. CDP Neighbor Analysis

```python
def analyze_cdp_neighbors(cdp_output):
    """
    Parse and analyze CDP neighbor information.
    
    Args:
        cdp_output (str): The output from 'show cdp neighbors' command
        
    Returns:
        dict: Dictionary containing neighbor analysis
    """
    parsed_data = parse_device_output(
        platform='cisco_ios',
        command='show cdp neighbors',
        output_text=cdp_output
    )
    
    neighbor_analysis = {
        'total_neighbors': len(parsed_data),
        'neighbor_types': {},
        'connections': []
    }
    
    for neighbor in parsed_data:
        # Track device types
        device_type = neighbor.get('platform', 'unknown')
        neighbor_analysis['neighbor_types'][device_type] = \
            neighbor_analysis['neighbor_types'].get(device_type, 0) + 1
            
        # Track connections
        connection = {
            'local_interface': neighbor['local_interface'],
            'neighbor': neighbor['destination_host'],
            'neighbor_interface': neighbor['neighbor_interface'],
            'capability': neighbor.get('capability', 'unknown')
        }
        neighbor_analysis['connections'].append(connection)
    
    return neighbor_analysis
```

## Best Practices

1. **Error Handling**
```python
def safe_parse_output(platform, command, data):
    """
    Safely parse command output with proper error handling.
    """
    try:
        return parse_output(platform=platform, command=command, data=data)
    except ImportError:
        print("TextFSM not properly installed. Check system requirements.")
        return None
    except Exception as e:
        print(f"Error parsing {command} on {platform}: {str(e)}")
        return None
```

2. **Template Verification**
```python
def verify_template_exists(platform, command):
    """
    Verify if a template exists for the given platform and command.
    """
    try:
        # Attempt a parse with empty data to check template existence
        parse_output(platform=platform, command=command, data='')
        return True
    except Exception:
        return False
```

3. **Batch Processing**
```python
def batch_process_outputs(outputs_list):
    """
    Process multiple command outputs in batch.
    
    Args:
        outputs_list (list): List of dictionaries containing
                           platform, command, and output text
    Returns:
        dict: Dictionary of parsed results
    """
    results = {}
    for item in outputs_list:
        key = f"{item['platform']}_{item['command']}"
        results[key] = parse_device_output(
            platform=item['platform'],
            command=item['command'],
            output_text=item['output']
        )
    return results
```

## Common Issues and Solutions

1. **Template Not Found**
   - Ensure the command matches exactly what's in the template
   - Check platform name is correct
   - Verify NTC Templates version has the template you need

2. **Parsing Errors**
   - Verify output format matches template expectations
   - Check for special characters or formatting in output
   - Ensure command output is complete

3. **Windows Compatibility**
   - Use raw strings for file paths
   - Install appropriate TextFSM version for Windows
   - Handle line endings appropriately

## Integration Examples

### 1. With Pandas for Analysis

```python
import pandas as pd

def analyze_interfaces_with_pandas(interface_output, platform='cisco_ios'):
    """
    Use pandas to analyze interface data.
    """
    parsed_data = parse_device_output(
        platform=platform,
        command='show interfaces',
        output_text=interface_output
    )
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(parsed_data)
    
    # Example analyses
    interface_stats = {
        'total_interfaces': len(df),
        'status_summary': df['link_status'].value_counts().to_dict(),
        'protocol_summary': df['protocol_status'].value_counts().to_dict(),
        'bandwidth_stats': df['bandwidth'].describe().to_dict()
    }
    
    return interface_stats
```

### 2. With Network Configuration Tools

```python
def compare_configs(old_config, new_config, platform='cisco_ios'):
    """
    Compare interface configurations between two outputs.
    """
    old_interfaces = parse_device_output(
        platform=platform,
        command='show interfaces',
        output_text=old_config
    )
    
    new_interfaces = parse_device_output(
        platform=platform,
        command='show interfaces',
        output_text=new_config
    )
    
    changes = {
        'added': [],
        'removed': [],
        'modified': []
    }
    
    old_intf = {i['interface']: i for i in old_interfaces}
    new_intf = {i['interface']: i for i in new_interfaces}
    
    # Find added and modified interfaces
    for intf_name, new_data in new_intf.items():
        if intf_name not in old_intf:
            changes['added'].append(new_data)
        elif new_data != old_intf[intf_name]:
            changes['modified'].append({
                'interface': intf_name,
                'old': old_intf[intf_name],
                'new': new_data
            })
    
    # Find removed interfaces
    for intf_name in old_intf:
        if intf_name not in new_intf:
            changes['removed'].append(old_intf[intf_name])
    
    return changes
```

## Contributing

To contribute additional templates or improvements:

1. Visit the [NTC Templates GitHub repository](https://github.com/networktocode/ntc-templates)
2. Follow the contribution guidelines
3. Test your templates thoroughly
4. Submit a pull request

## Additional Resources

- [NTC Templates Documentation](https://ntc-templates.readthedocs.io/)
- [TextFSM Documentation](https://github.com/google/textfsm/wiki)
- [Network to Code Community](https://networktocode.com/community/) 