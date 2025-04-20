"""
Parser for Palo Alto configuration files.
Allows viewing nested dictionary structure at configurable depth levels.
"""
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from tabulate import tabulate


def xml_to_dict(element: ET.Element) -> Dict[str, Any]:
    """
    Convert XML to dictionary recursively.

    Args:
        element: XML element to convert

    Returns:
        Dictionary representation of the XML
    """
    result = {}

    # Handle attributes if present
    if element.attrib:
        result.update(element.attrib)

    # Handle child elements
    for child in element:
        child_dict = xml_to_dict(child)

        if child.tag in result:
            # If tag already exists, convert to list or append
            if isinstance(result[child.tag], list):
                result[child.tag].append(child_dict)
            else:
                result[child.tag] = [result[child.tag], child_dict]
        else:
            result[child.tag] = child_dict

    # Handle element text
    if element.text and element.text.strip():
        if result:
            result['text'] = element.text.strip()
        else:
            result = element.text.strip()

    return result


def print_dict_levels(d: Dict[str, Any], current_level: int = 0,
                      max_level: Optional[int] = None, indent: str = ""):
    """
    Print dictionary structure up to specified number of levels.

    Args:
        d: Dictionary to print
        current_level: Current depth level (used internally for recursion)
        max_level: Maximum depth level to print
        indent: Indentation string (used internally for formatting)
    """
    if max_level is not None and current_level > max_level:
        return

    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, (dict, list)):
                print(f"{indent}{key}:")
                print_dict_levels(value, current_level + 1, max_level, indent + "  ")
            else:
                print(f"{indent}{key}: {value}")
    elif isinstance(d, list):
        for item in d:
            print_dict_levels(item, current_level, max_level, indent)
    else:
        print(f"{indent}{d}")


def get_level_2_items(d: Dict[str, Any]) -> list:
    """
    Get all items at level 2 of the dictionary.

    Args:
        d: Dictionary to analyze

    Returns:
        List of level 2 items
    """
    level_2_items = []
    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, dict):
                for sub_key in value.keys():
                    level_2_items.append(f"{key}.{sub_key}")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        for sub_key in item.keys():
                            level_2_items.append(f"{key}.{sub_key}")
    return sorted(list(set(level_2_items)))


def display_menu(config_dict: Dict[str, Any]) -> None:
    """
    Display interactive menu for viewing configuration.

    Args:
        config_dict: Configuration dictionary to display
    """
    while True:
        # Get level 2 items for display options
        level_2_items = get_level_2_items(config_dict)

        # Create menu options
        menu_options = [
            ["1", "Select level to display"],
            ["2", "Display specific section"],
            ["q", "Quit"]
        ]

        print("\nAvailable Options:")
        print(tabulate(menu_options, headers=["Choice", "Action"], tablefmt="grid"))

        choice = input("\nEnter your choice: ").lower()

        if choice == 'q':
            break
        elif choice == '1':
            try:
                levels = int(input("Enter number of levels to display: "))
                if levels < 0:
                    print("Please enter a positive number")
                    continue
                print("\nConfiguration structure:")
                print_dict_levels(config_dict, max_level=levels)
            except ValueError:
                print("Please enter a valid number")
        elif choice == '2':
            # Display available sections
            section_options = [[str(i + 1), item] for i, item in enumerate(level_2_items)]
            print("\nAvailable Sections:")
            print(tabulate(section_options, headers=["Choice", "Section"], tablefmt="grid"))

            try:
                section_choice = int(input("\nEnter section number: ")) - 1
                if 0 <= section_choice < len(level_2_items):
                    selected_path = level_2_items[section_choice].split('.')

                    # Navigate to selected section
                    current_dict = config_dict
                    for key in selected_path:
                        if isinstance(current_dict, dict):
                            current_dict = current_dict.get(key, {})
                        elif isinstance(current_dict, list):
                            # Handle list case if needed
                            current_dict = current_dict[0].get(key, {})

                    # Ask for levels to display
                    try:
                        levels = int(input("Enter number of additional levels to display: "))
                        if levels < 0:
                            print("Please enter a positive number")
                            continue
                        print(f"\nDisplaying section: {level_2_items[section_choice]}")
                        print_dict_levels(current_dict, max_level=levels)
                    except ValueError:
                        print("Please enter a valid number")
                else:
                    print("Invalid section number")
            except ValueError:
                print("Please enter a valid number")
        else:
            print("Invalid choice")


def main():
    """
    Main function to parse Palo Alto config and display structure.
    """
    # Parse XML file
    tree = ET.parse('input/UNCSO-Panorama-M-200_017607002338.xml')
    root = tree.getroot()

    # Convert to dictionary
    config_dict = xml_to_dict(root)

    # Display interactive menu
    display_menu(config_dict)


if __name__ == "__main__":
    main()