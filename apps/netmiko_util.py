"""
Netmiko Connection Utility Module

This module provides a wrapper class around Netmiko to simplify network device
connections and command execution. It handles the connection lifecycle and
provides methods for common operations like retrieving device configurations.
"""

from netmiko import ConnectHandler

class NetmikoUtil:
    """
    Utility class for handling Netmiko connections to network devices.
    
    This class provides a simplified interface for connecting to network devices
    and executing commands using the Netmiko library. It handles connection
    management and provides methods for common operations.
    
    Attributes:
        device_params (dict): Dictionary containing device connection parameters:
            - device_type: Type of device (e.g., 'cisco_ios', 'cisco_nxos')
            - host: Device hostname or IP address
            - username: SSH username
            - password: SSH password
            - secret: Enable secret (if required)
            
    Example:
        >>> params = {
        ...     'device_type': 'cisco_ios',
        ...     'host': '192.168.1.1',
        ...     'username': 'admin',
        ...     'password': 'cisco'
        ... }
        >>> device = NetmikoUtil(params)
        >>> config = device.get_running_config()
    """

    def __init__(self, device_params):
        """
        Initialize a new NetmikoUtil instance.
        
        Args:
            device_params (dict): Dictionary containing device connection parameters.
                                Must include at minimum: device_type, host, username, password.
                                See class docstring for full parameter list.
        
        Example:
            >>> params = {
            ...     'device_type': 'cisco_ios',
            ...     'host': '192.168.1.1',
            ...     'username': 'admin',
            ...     'password': 'cisco'
            ... }
            >>> device = NetmikoUtil(params)
        """
        self.device_params = device_params

    def get_running_config(self):
        """
        Retrieve the running configuration from the network device.
        
        This method establishes a connection to the device using the provided
        parameters, executes the 'show running-config' command, and returns
        the complete running configuration.
        
        Returns:
            str: The complete running configuration from the device.
        
        Raises:
            Exception: If connection fails or command execution fails.
                      The original exception is re-raised after printing error details.
        
        Example:
            >>> device = NetmikoUtil(device_params)
            >>> try:
            ...     config = device.get_running_config()
            ...     print("Configuration retrieved successfully")
            ... except Exception as e:
            ...     print(f"Failed to get config: {e}")
        
        Notes:
            - Uses context manager to ensure proper connection cleanup
            - Prints error message before re-raising exceptions for debugging
            - May take several seconds to complete depending on config size
        """
        try:
            with ConnectHandler(**self.device_params) as net_connect:
                output = net_connect.send_command("show running-config")
            return output
        except Exception as e:
            print(f"Failed to retrieve running configuration: {e}")
            raise