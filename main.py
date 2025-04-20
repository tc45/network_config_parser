import argparse
import os
import datetime
import logging
from tabulate import tabulate
from apps.asa_parser import AsaParser
from apps.netmiko_util import NetmikoUtil

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_files_in_input_directory():
    """Retrieve a list of files in the input directory."""
    input_dir = 'input'
    return [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

def identify_device_type(file_path):
    """Identify the device type based on the file content."""
    # Placeholder logic for identifying device type
    # For now, assume all files are Cisco ASA
    return 'Cisco ASA'

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Network Configuration Parser')
    parser.add_argument('--output_format', type=str, choices=['excel'], default='excel', help='Output format')
    parser.add_argument('--use_netmiko', action='store_true', help='Use Netmiko to connect to devices')
    parser.add_argument('--device_ip', type=str, help='IP address of the device for Netmiko connection')
    parser.add_argument('--username', type=str, help='Username for Netmiko connection')
    parser.add_argument('--password', type=str, help='Password for Netmiko connection')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    return parser.parse_args()

def main():
    """Main function to execute the parsing utility."""
    args = parse_arguments()

    # Configure logging level based on debug argument
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # Ensure input and output directories exist
    if not os.path.exists('input'):
        os.makedirs('input')
    if not os.path.exists('output'):
        os.makedirs('output')

    # Initialize the ASA parser
    asa_parser = AsaParser()

    if args.use_netmiko:
        # Use Netmiko to connect to the device
        device_params = {
            'device_type': 'cisco_asa',
            'host': args.device_ip,
            'username': args.username,
            'password': args.password,
        }
        netmiko_util = NetmikoUtil(device_params)
        try:
            config_data = netmiko_util.get_running_config()
            parsed_data = asa_parser.parse_data(config_data)

            # Determine output file name
            hostname = "default_hostname"  # Placeholder for hostname extraction logic
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_file_name = f"{hostname}_{timestamp}.xlsx"
            output_path = os.path.join('output', output_file_name)

            # Export to Excel
            asa_parser.export_to_excel(parsed_data, output_path)
        except Exception as e:
            logging.error(f"An error occurred while processing the device: {e}")
    else:
        # Get files from the input directory
        files = get_files_in_input_directory()
        if not files:
            logging.info("No files found in the input directory.")
            return

        # Identify device types
        file_device_map = {}
        for file in files:
            file_path = os.path.join('input', file)
            device_type = identify_device_type(file_path)
            file_device_map[file] = device_type

        # Display files and device types using tabulate
        table_data = [[i + 1, file, device_type] for i, (file, device_type) in enumerate(file_device_map.items())]
        table_data.append([len(table_data) + 1, 'Parse All', 'All Devices'])
        print(tabulate(table_data, headers=['Selection', 'File Name', 'Device Type'], tablefmt='grid'))

        # Prompt user to select files to parse
        selected_option = input("Enter the selection number of the files you want to parse, or 'Parse All': ").strip()

        if selected_option.lower() == 'parse all':
            selected_files = list(file_device_map.keys())
        else:
            try:
                selected_index = int(selected_option) - 1
                if selected_index < len(file_device_map):
                    selected_files = [list(file_device_map.keys())[selected_index]]
                else:
                    logging.error("Invalid selection.")
                    return
            except ValueError:
                logging.error("Invalid input. Please enter a number or 'Parse All'.")
                return

        for file in selected_files:
            file_path = os.path.join('input', file)
            try:
                # Parse the input file
                parsed_data = asa_parser.parse_file(file_path)

                # Determine output file name
                hostname = "default_hostname"  # Placeholder for hostname extraction logic
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                output_file_name = f"{hostname}_{timestamp}.xlsx"
                output_path = os.path.join('output', output_file_name)

                # Export to Excel
                asa_parser.export_to_excel(parsed_data, output_path)
            except Exception as e:
                logging.error(f"An error occurred while processing {file}: {e}")

if __name__ == '__main__':
    main()
