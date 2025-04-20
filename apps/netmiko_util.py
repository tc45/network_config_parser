from netmiko import ConnectHandler

class NetmikoUtil:
    """Utility class for handling Netmiko connections."""

    def __init__(self, device_params):
        """Initialize with device parameters."""
        self.device_params = device_params

    def get_running_config(self):
        """Retrieve the running configuration from the device."""
        try:
            with ConnectHandler(**self.device_params) as net_connect:
                output = net_connect.send_command("show running-config")
            return output
        except Exception as e:
            print(f"Failed to retrieve running configuration: {e}")
            raise