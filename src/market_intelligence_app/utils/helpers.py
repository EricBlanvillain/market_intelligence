"""
Helper functions for the Market Intelligence Platform.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def format_timestamp(timestamp: Optional[str] = None) -> str:
    """
    Format a timestamp string or generate a current timestamp.

    Args:
        timestamp: Optional timestamp string to format

    Returns:
        Formatted timestamp string
    """
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.warning(f"Could not parse timestamp: {timestamp}")
            return timestamp
    else:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary containing the JSON data
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return {}

def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to a JSON file.

    Args:
        data: Dictionary to save
        file_path: Path to save the JSON file

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False

def get_env_variable(name: str, default: Optional[str] = None) -> str:
    """
    Get an environment variable with a default value.

    Args:
        name: Name of the environment variable
        default: Default value if the environment variable is not set

    Returns:
        Value of the environment variable or default
    """
    value = os.environ.get(name, default)
    if value is None:
        logger.warning(f"Environment variable {name} not set and no default provided")
    return value

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length of the text

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
