import logging

def identify_device_type(file_path):
    """Identify the device type based on the file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()

        is_asa = False
        is_ios = False

        for line in content:
            # Check for ASA markers
            if "Cisco Adaptive Security Appliance Software Version" in line or "Hardware:   ASA" in line:
                is_asa = True
                break
            # Check for IOS markers
            if "Cisco IOS XE Software" in line or "Cisco IOS Software" in line:
                is_ios = True
                break

        if is_asa:
            return 'Cisco ASA'
        elif is_ios:
            return 'Cisco IOS'
        else:
            # Fallback or default if no specific markers found
            logging.warning(f"Could not definitively identify device type for {file_path}. Defaulting to Unknown.")
            return 'Unknown' # Or potentially 'Cisco ASA' as a default if preferred
    except Exception as e:
        logging.error(f"Error reading or processing file {file_path}: {e}")
        return 'Error' 