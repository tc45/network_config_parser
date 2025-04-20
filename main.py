#!/usr/bin/env python3

"""
Network Configuration Parser - Main entry point
Handles command line arguments and logging setup for all parsers
"""

import argparse
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
from datetime import datetime
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from tabulate import tabulate
from apps.identify import identify_device_type

def setup_logging(debug_mode: bool = False) -> None:
    """
    Set up logging configuration with both file and console handlers.
    
    Args:
        debug_mode (bool): Whether to enable debug logging
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Configure rich console with custom theme
    custom_theme = Theme({
        "info": "green",
        "warning": "yellow",
        "error": "orange1",
        "debug": "blue"
    })
    console = Console(theme=custom_theme)

    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set the base logging level
    base_level = logging.DEBUG if debug_mode else logging.INFO
    root_logger.setLevel(base_level)

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter('%(message)s')  # Simpler format for console

    # Create and configure TimedRotatingFileHandler for daily rotation
    log_file = os.path.join('logs', 'network_parser.log')
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days of logs
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(base_level)

    # Create and configure RichHandler for console output
    console_handler = RichHandler(
        console=console,
        show_path=False,
        rich_tracebacks=True,
        tracebacks_show_locals=debug_mode,
        markup=True,
        log_time_format='[%X]'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(base_level)

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Log initial setup message
    logger = logging.getLogger(__name__)
    logger.debug("Logging system initialized" + (" with debug mode enabled" if debug_mode else ""))

def get_parser_class(device_type: str):
    """Get the appropriate parser class based on device type"""
    if device_type == "Cisco IOS" or device_type == "Cisco NXOS":
        from apps.cisco_if_parser import CiscoInterfaceParser, CiscoACLParser
        return (CiscoInterfaceParser, CiscoACLParser)
    elif device_type == "Cisco ASA":
        from apps.asa_parser import AsaParser
        return (AsaParser,)
    elif device_type == "Palo Alto":
        from apps.palo_alto import PaloAltoParser
        return (PaloAltoParser,)
    else:
        return None

def main():
    """Main entry point for the network configuration parser"""
    parser = argparse.ArgumentParser(
        description="Network Configuration Parser - Parse and analyze network device configurations"
    )
    parser.add_argument(
        "--show-tech", 
        help="Path to show tech file (optional)"
    )
    parser.add_argument(
        "--display", 
        action="store_true",
        help="Display output in table format instead of saving to Excel"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    args = parser.parse_args()

    # Set up logging first thing
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    try:
        # Create input directory if it doesn't exist
        os.makedirs('input', exist_ok=True)

        # Get list of files and identify their types
        if args.show_tech:
            files = [(1, args.show_tech, identify_device_type(args.show_tech))]
        else:
            files = []
            for idx, filename in enumerate(os.listdir('input'), 1):
                filepath = os.path.join('input', filename)
                if os.path.isfile(filepath):
                    device_type = identify_device_type(filepath)
                    files.append((idx, filepath, device_type))

        if not files:
            logger.warning("No configuration files found to process")
            return

        # Display file selection menu
        while True:
            print("\nAvailable configuration files:")
            headers = ["ID", "Filename", "Device Type"]
            table_data = [[id, os.path.basename(file), type] for id, file, type in files]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            print("\nOptions:")
            print("  <id>   : Parse single file by ID")
            print("  all    : Parse all files")
            print("  q      : Quit")

            choice = input("\nEnter selection: ").strip().lower()

            if choice == 'q':
                break
            elif choice == 'all':
                for file_id, filepath, device_type in files:
                    process_file(filepath, device_type, args.display)
            else:
                try:
                    file_id = int(choice)
                    selected = next((f for f in files if f[0] == file_id), None)
                    if selected:
                        process_file(selected[1], selected[2], args.display)
                    else:
                        logger.error(f"Invalid ID: {file_id}")
                except ValueError:
                    logger.error("Invalid selection")

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error processing configuration: {e}", exc_info=True)
        sys.exit(1)

def process_file(filepath: str, device_type: str, display: bool) -> None:
    """Process a single configuration file"""
    logger = logging.getLogger(__name__)
    logger.info(f"Processing {device_type} configuration: {filepath}")

    try:
        parser_classes = get_parser_class(device_type)
        if not parser_classes:
            logger.error(f"No parser available for device type: {device_type}")
            return

        # Initialize variables to store combined data
        combined_data = {}
        hostname = None

        # Initialize and run each parser
        for parser_class in parser_classes:
            parser = parser_class(filepath)
            parsed_data = parser.parse_file()
            
            # Get hostname from first parser if not set
            if hostname is None:
                hostname = parser.get_hostname()
            
            # Combine the parsed data
            if parsed_data:
                combined_data.update(parsed_data)
        
        if combined_data:
            if not display:
                # Create output directory if it doesn't exist
                output_dir = 'output'
                os.makedirs(output_dir, exist_ok=True)
                
                # Import and use the exporter
                from apps.exporter import export_data_to_excel
                export_data_to_excel(combined_data, output_dir, hostname)
            else:
                # Display tables in console using tabulate
                for sheet_name, data in combined_data.items():
                    if data:
                        logger.info(f"Adding new sheet: {sheet_name}")
                        headers = data[0].keys()
                        table_data = [row.values() for row in data]
                        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    except Exception as e:
        logger.error(f"Failed to process {filepath}: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
